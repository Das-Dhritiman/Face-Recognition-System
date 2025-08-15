import cv2
import dlib
import numpy as np
import pickle
import os

# Use a relative import to get extract_features from the same package (src)
from .feature_extraction import extract_features

# Define paths
MODELS_DIR = 'models'
MODEL_PATH = os.path.join(MODELS_DIR, 'expression_model.pkl')
PREDICTOR_PATH = os.path.join(MODELS_DIR, 'shape_predictor_68_face_landmarks.dat')

def recognize_expressions():
    """
    Captures video from the webcam and performs real-time expression
    recognition using the pre-trained model.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}. Please train the model first using '--mode train'.")
        return
    if not os.path.exists(PREDICTOR_PATH):
        print(f"Error: Predictor file not found at {PREDICTOR_PATH}")
        print("Please download it and place it in the 'models' directory.")
        return

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)

    while True:
        ret, frame = cap.read()
        # --- FIX: Check if the frame is valid before processing ---
        if not ret or frame is None:
            print("Warning: Skipping empty frame.")
            continue
        # --- End of FIX ---

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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

            features = extract_features(landmarks)
            features = np.array(features).reshape(1, -1)

            prediction = model.predict(features)[0]
            proba = model.predict_proba(features)
            confidence = np.max(proba)

            text = f"{prediction} ({confidence:.2f})"
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Expression Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
