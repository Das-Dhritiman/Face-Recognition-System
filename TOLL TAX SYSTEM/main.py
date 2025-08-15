from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import numpy as np
import easyocr
import base64
import mysql.connector
from mysql.connector import Error as DBError
import os
import threading
import webbrowser
from datetime import datetime
import decimal
import json
import re

app = Flask(__name__)
reader = easyocr.Reader(['en'])

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'bongodb',
    'database': 'num_plate_recognition',
}

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

app.json_encoder = DecimalEncoder

def init_db():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'], user=db_config['user'], password=db_config['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number_plate VARCHAR(20) UNIQUE NOT NULL,
                owner_name VARCHAR(100) NOT NULL,
                model_name VARCHAR(100) NOT NULL,
                balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                number_plate VARCHAR(20) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                remaining_balance DECIMAL(10,2) NOT NULL,
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (number_plate) REFERENCES vehicles(number_plate) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()
    except DBError as err:
        print(f"Database initialization error: {err}")

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except DBError as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/decode', methods=['POST'])
def decode():
    try:
        data = request.json.get('image')
        if not data:
            return jsonify({'status': 'error', 'message': 'No image data provided.'}), 400

        encoded_data = data.split(',')[1]
        img_bytes = base64.b64decode(encoded_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        results = reader.readtext(gray)
        
        detected_plate_text = ''
        if results:
            for (bbox, text, prob) in results:
                if prob > 0.25:
                    cleaned_text = re.sub(r'[\W_]+', '', text).upper()
                    if len(cleaned_text) > 2 and any(char.isdigit() for char in cleaned_text):
                        detected_plate_text += cleaned_text

        if not detected_plate_text:
            return jsonify({'status': 'not_found', 'message': 'No plate detected'})

        final_plate = re.sub(r'[^A-Z0-9]', '', detected_plate_text).upper()
        final_plate = final_plate.replace('I', '1').replace('O', '0')

        if len(final_plate) > 10:
            match = re.search(r'[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{1,4}', final_plate)
            if match:
                final_plate = match.group(0)

        if len(final_plate) < 4:
            return jsonify({'status': 'not_found', 'message': 'Detected text too short for a plate.'})

        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
        
        cursor = conn.cursor(dictionary=True)
        response = {}
        
        try:
            # --- SERVER-SIDE COOLDOWN CHECK (THE DEFINITIVE FIX) ---
            cooldown_seconds = 60 # Using a safe 60-second window
            check_recent_tx_query = """
                SELECT transaction_time FROM transactions 
                WHERE number_plate = %s AND transaction_time > NOW() - INTERVAL %s SECOND
                ORDER BY transaction_time DESC LIMIT 1
            """
            cursor.execute(check_recent_tx_query, (final_plate, cooldown_seconds))
            recent_transaction = cursor.fetchone()

            if recent_transaction:
                # If a recent transaction is found, stop immediately and inform the client.
                return jsonify({
                    'status': 'cooldown',
                    'plate': final_plate,
                    'message': f'Plate already processed within the last {cooldown_seconds} seconds.'
                })

            # --- If no recent transaction, proceed with the atomic update logic ---
            deduction_amount = decimal.Decimal('50.00')
            update_query = "UPDATE vehicles SET balance = balance - %s WHERE number_plate = %s AND balance >= %s"
            cursor.execute(update_query, (deduction_amount, final_plate, deduction_amount))

            if cursor.rowcount == 1:
                cursor.execute("SELECT * FROM vehicles WHERE number_plate = %s", (final_plate,))
                vehicle = cursor.fetchone()
                
                insert_transaction_query = "INSERT INTO transactions (number_plate, amount, remaining_balance) VALUES (%s, %s, %s)"
                cursor.execute(insert_transaction_query, (final_plate, deduction_amount, vehicle['balance']))
                
                conn.commit()
                
                response = {
                    'status': 'success',
                    'plate': final_plate,
                    'owner': vehicle['owner_name'],
                    'previous_balance': vehicle['balance'] + deduction_amount,
                    'deduction': deduction_amount,
                    'current_balance': vehicle['balance'],
                }
            else:
                cursor.execute("SELECT * FROM vehicles WHERE number_plate = %s", (final_plate,))
                vehicle = cursor.fetchone()
                
                if vehicle:
                    response = {
                        'status': 'failed',
                        'plate': final_plate,
                        'owner': vehicle['owner_name'],
                        'previous_balance': vehicle['balance'],
                        'message': 'Insufficient balance.'
                    }
                else:
                    response = {
                        'status': 'not_found',
                        'plate': final_plate,
                        'message': 'Vehicle not registered.'
                    }
        except DBError as err:
            conn.rollback()
            print(f"Database transaction error: {err}")
            return jsonify({'status': 'error', 'message': 'A database error occurred.'}), 500
        finally:
            if conn.is_connected():
                conn.close()
            
        return jsonify(response)

    except Exception as e:
        print(f"Error in /decode: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Other Flask Routes (Unchanged) ---
@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        number_plate = data.get('number_plate', '').strip().upper()
        owner_name = data.get('owner_name', '').strip()
        model_name = data.get('model_name', '').strip()
        balance = decimal.Decimal(data.get('balance', 0))
        if not all([number_plate, owner_name, model_name]):
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vehicles (number_plate, owner_name, model_name, balance) VALUES (%s, %s, %s, %s)", (number_plate, owner_name, model_name, balance))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': f'Vehicle {number_plate} added!'})
    except mysql.connector.IntegrityError:
        return jsonify({'status': 'error', 'message': f'Vehicle {number_plate} already exists!'}), 409
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/view_vehicles', methods=['GET'])
def view_vehicles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicles ORDER BY created_at DESC")
        vehicles = cursor.fetchall()
        conn.close()
        return jsonify(vehicles)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete_vehicle', methods=['POST'])
def delete_vehicle():
    try:
        data = request.get_json()
        number_plate = data.get('number_plate', '').strip().upper()
        if not number_plate:
            return jsonify({'status': 'error', 'message': 'Number plate is required.'}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE number_plate = %s", (number_plate,))
        cursor.execute("DELETE FROM vehicles WHERE number_plate = %s", (number_plate,))
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Vehicle not found.'}), 404
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Vehicle deleted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1.25, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=True, use_reloader=True)
