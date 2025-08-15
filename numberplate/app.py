from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import numpy as np
import easyocr
import base64
import mysql.connector
import os
import threading
import webbrowser
from datetime import datetime


app = Flask(__name__)
reader = easyocr.Reader(['en'])

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'bongodb',
    'database': 'num_plate_recognition',
}

def init_db():
    #Initialize database tables if they don't exist
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS num_plate_recognition")
    cursor.execute("USE num_plate_recognition")

    
    # Create vehicles table
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
    
    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            number_plate VARCHAR(20) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            remaining_balance DECIMAL(10,2) NOT NULL,
            transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (number_plate) REFERENCES vehicles(number_plate)
        )
    """)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug log
        
        # Validate data
        number_plate = data.get('number_plate', '').strip().upper()
        owner_name = data.get('owner_name', '').strip()
        model_name = data.get('model_name', '').strip()
        balance = float(data.get('balance', 0))
        
        if not all([number_plate, owner_name, model_name]):
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400
        
        # Database operation
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vehicles (number_plate, owner_name, model_name, balance)
            VALUES (%s, %s, %s, %s)
        """, (number_plate, owner_name, model_name, balance))
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT * FROM vehicles WHERE number_plate = %s", (number_plate,))
        new_vehicle = cursor.fetchone()
        conn.close()
        
        if not new_vehicle:
            raise Exception("Failed to verify vehicle creation")
            
        return jsonify({
            'status': 'success',
            'message': f'Vehicle {number_plate} added!'
        })
        
    except mysql.connector.IntegrityError:
        return jsonify({
            'status': 'error',
            'message': f'Vehicle {number_plate} already exists!'
        }), 409
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/view_vehicles', methods=['GET'])
def view_vehicles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicles ORDER BY created_at DESC")
        vehicles = cursor.fetchall()
        return jsonify(vehicles)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

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
            return jsonify({'status': 'error', 'message': 'Vehicle not found.'}), 404
            
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Vehicle deleted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

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

        # Preprocess image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

        # Plate detection
        results = reader.readtext(gray)
        detected_plate = ''
        confidence = 0.0
        
        for (bbox, text, prob) in results:
            if prob > 0.3:  # Minimum confidence threshold
                # Filter out non-plate text (basic filtering)
                if len(text) >= 4 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
                    detected_plate += text + ' '
                    confidence = max(confidence, prob)

        detected_plate = detected_plate.strip().replace(" ", "").upper()

        # Database lookup
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE number_plate = %s", (detected_plate,))
        row = cursor.fetchone()

        if row:
            number_plate, owner_name, model_name, balance = row[1:5]  # Skip id and created_at
            if balance >= 50:
                new_balance = balance - 50
                cursor.execute("UPDATE vehicles SET balance = %s WHERE number_plate = %s", (new_balance, number_plate))
                cursor.execute("""
                    INSERT INTO transactions (number_plate, amount, remaining_balance)
                    VALUES (%s, %s, %s)
                """, (number_plate, 50, new_balance))
                conn.commit()
                response = {
                    'status': 'success',
                    'plate': number_plate,
                    'owner': owner_name,
                    'model': model_name,
                    'balance': new_balance,
                    'message': f'₹50 deducted from {owner_name}\'s account. New balance: ₹{new_balance}',
                    'confidence': confidence
                }
            else:
                response = {
                    'status': 'failed',
                    'plate': number_plate,
                    'owner': owner_name,
                    'model': model_name,
                    'balance': balance,
                    'message': f'Insufficient balance! Current balance: ₹{balance}',
                    'confidence': confidence
                }
        else:
            response = {
                'status': 'not_found',
                'plate': detected_plate if detected_plate else 'Not detected',
                'message': 'Number plate not found in database.' if detected_plate else 'No plate detected',
                'confidence': confidence
            }

        conn.close()
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    init_db()  # Initialize database tables
    if os.environ.get('WERKZEUG_RUN_MAIN')=='true':
        threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=True)