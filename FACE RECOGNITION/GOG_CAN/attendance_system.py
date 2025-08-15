import os
import datetime
from tkinter import messagebox
from geopy.geocoders import Nominatim
import mysql.connector

# --- DATABASE CONFIGURATION ---
# !!! IMPORTANT !!!
# Update these details with your own MySQL database credentials.
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'bongodb',
    'database': 'attendance_system'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to MySQL: {err}")
        return None

def setup_database():
    """Connects to the database and creates the attendance table if it doesn't exist."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        # This SQL command creates the 'attendance' table with the required columns.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                person_id INT NOT NULL,
                person_name VARCHAR(255) NOT NULL,
                attendance_date DATE NOT NULL,
                attendance_time TIME NOT NULL,
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                UNIQUE KEY unique_attendance (person_id, attendance_date)
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Setup Error", f"Failed to create table: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_location():
    """Gets the current GPS location."""
    try:
        geolocator = Nominatim(user_agent="face_recognition_app")
        location = geolocator.geocode("India")
        if location:
            return location.latitude, location.longitude
        else:
            return 20.5937, 78.9629  # Fallback coordinates
    except Exception as e:
        print(f"Could not get location: {e}")
        return 20.5937, 78.9629

def mark_attendance(person_id, person_name):
    """Marks attendance for the given person in the MySQL database."""
    conn = get_db_connection()
    if conn is None:
        return

    lat, lon = get_location()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    try:
        cursor = conn.cursor()
        
        # SQL query to insert a new attendance record.
        # The ON DUPLICATE KEY UPDATE part handles cases where attendance for the
        # same person on the same day already exists, preventing duplicates.
        sql = """
            INSERT INTO attendance (person_id, person_name, attendance_date, attendance_time, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE person_name = VALUES(person_name);
        """
        val = (person_id, person_name, date, time, lat, lon)
        
        cursor.execute(sql, val)
        conn.commit()
        
        # Check if a new row was inserted or an existing one was updated.
        if cursor.rowcount > 0:
             messagebox.showinfo("Attendance Marked", f"Attendance for {person_name} has been marked successfully at\nLat: {lat}, Lon: {lon}")
        else:
             messagebox.showinfo("Attendance Info", f"Attendance for {person_name} has already been marked today.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to record attendance: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# --- Initial Database Setup ---
# This function will be called once when the application starts
# to ensure the database table is ready.
setup_database()
