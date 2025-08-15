import cv2
import dlib
import pandas as pd
import os

# Use a relative import to get extract_features from the same package (src)
from .feature_extraction import extract_features

# Define paths
DATA_DIR = 'data'
MODELS_DIR = 'models'
CSV_PATH = os.path.join(DATA_DIR, 'expressions.csv')
PREDICTOR_PATH = os.path.join(MODELS_DIR, 'shape_predictor_68_face_landmarks.dat')

def collect_data(expression_name):
    """
    Collects training data for a given expression by capturing facial landmarks
    from a webcam feed.

    Args:
        expression_name (str): The name of the expression to be collected (e.g., 'smiling').
    """
    if not os.path.exists(PREDICTOR_PATH):
        print(f"Error: Predictor file not found at {PREDICTOR_PATH}")
        print("Please download it and place it in the 'models' directory.")
        return
    os.makedirs(DATA_DIR, exist_ok=True)

    # Use a more stable camera backend for Windows (CAP_DSHOW)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)

    data = []
    print(f"Collecting data for expression: {expression_name}. Look at the camera and press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Warning: Skipping empty frame from camera.")
            continue

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Ensure gray is a valid 8-bit single-channel image
            if gray is None or gray.dtype != 'uint8' or len(gray.shape) != 2:
                print("Warning: Invalid grayscale image. Skipping frame.")
                continue

            faces = detector(gray)

            for face in faces:
                x1, y1, x2, y2 = (face.left(), face.top(), face.right(), face.bottom())
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                landmarks_dlib = predictor(gray, face)
                landmarks = []
                for n in range(0, 68):
                    x = landmarks_dlib.part(n).x
                    y = landmarks_dlib.part(n).y
                    landmarks.append((x, y))
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                features = extract_features(landmarks)
                data.append(features)

        except RuntimeError as e:
            print(f"Warning: Skipping problematic frame. Error: {e}")
            continue

        cv2.imshow("Data Collection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if data:
        df = pd.DataFrame(data)
        df['expression'] = expression_name
        
        if not os.path.exists(CSV_PATH):
            df.to_csv(CSV_PATH, index=False)
        else:
            df.to_csv(CSV_PATH, mode='a', header=False, index=False)
        print(f"Data collected for '{expression_name}' and saved to {CSV_PATH}")
