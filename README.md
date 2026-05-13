# BiometricGate

A desktop face recognition and attendance app built with Python, Tkinter, and OpenCV.

This project lets you:
- register a person with ID, name, age, and status
- capture face images from webcam
- train an LBPH face recognition model
- recognize faces live from webcam
- mark attendance in MySQL (with date, time, and location)

## Project Structure

- haarcascade_frontalface_default.xml: Haar cascade model for face detection
- FACE RECOGNITION/src/face_recog.py: main GUI app (registration, training, live recognition)
- FACE RECOGNITION/src/attendance_system.py: attendance insert logic (MySQL + geopy)
- FACE RECOGNITION/src/img_import_locally.py: helper GUI to copy local images into TrainingData/Images
- FACE RECOGNITION/src/img_downloader.py: helper GUI to download images from a CSV of URLs
- TrainingData/: generated local training and attendance artifacts

## Requirements

- Python 3.9+
- Webcam
- MySQL server (running locally or remotely)

Python packages:
- opencv-contrib-python
- pillow
- numpy
- pandas
- mysql-connector-python
- python-dotenv
- geopy
- requests

## Quick Setup (Windows PowerShell)

1. Open terminal in repo root.
2. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install opencv-contrib-python pillow numpy pandas mysql-connector-python python-dotenv geopy requests
```

4. Create MySQL database (only database, table is auto-created by app):

```sql
CREATE DATABASE attendance_system;
```

5. Create a .env file in repo root:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=attendance_system
```

## Run

From repo root:

```powershell
python "FACE RECOGNITION\src\face_recog.py"
```

## How To Use

1. Click Register New Person.
2. Enter ID, Name, Age, Status.
3. Click Capture Images and let it collect around 50 face images.
4. Click Train Model.
5. Open Start Recognition.
6. When a known face appears, click Mark Attendance.

Attendance rows are inserted into MySQL table attendance.

## Optional Helper Scripts

Import local images into training folder:

```powershell
python "FACE RECOGNITION\src\img_import_locally.py"
```

Download images from CSV URLs (column name must be image_url):

```powershell
python "FACE RECOGNITION\src\img_downloader.py"
```

## Common Problems and Fixes

1. Error: module 'cv2' has no attribute 'face'
- Cause: opencv-python installed instead of opencv-contrib-python.
- Fix:

```powershell
pip uninstall opencv-python -y
pip install opencv-contrib-python
```

2. MySQL connection error
- Check MySQL service is running.
- Verify .env values (host, user, password, db).
- Ensure database exists.

3. Camera not opening or black frame
- Close other apps using webcam.
- Try changing webcam index in source (cv2.VideoCapture(0) to 1).

4. Haar cascade not found
- Keep haarcascade_frontalface_default.xml in project root.
- If missing, main app tries auto-download (internet required).

## Git Notes

This repository is configured to ignore generated local data and media, including:
- TrainingData/Images/
- FACE RECOGNITION/JEFF BEZOS IMGS/
- *.csv, *.jpg, *.jpeg, *.png

These files stay on your machine but are not tracked after untracking + commit.

## Future Simplification (Optional)

If you want an even smaller setup, replace MySQL attendance with CSV-only attendance in attendance_system.py. That removes MySQL, dotenv, and geopy dependencies.
