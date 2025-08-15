import cv2
import easyocr
import numpy as np

LANGUAGES = ['en']  # Add other languages like 'hi' if needed

# Initialize EasyOCR reader once
print(f"Initializing EasyOCR reader for languages: {LANGUAGES}...")
reader = easyocr.Reader(LANGUAGES, gpu=False)  # Try gpu=False if lagging
print("EasyOCR reader initialized.")

# Confidence threshold
CONF_THRESHOLD = 0.5

# --- Webcam Setup ---
cap = cv2.VideoCapture(0)

# Set lower resolution to reduce lag
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("\nPress 'q' to quit.")
print("Scanning for number plates...")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Resize and convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_frame = cv2.resize(gray_frame, (640, 480))

    detected_plates = []

    # Process every 3rd frame for better performance
    if frame_count % 3 == 0:
        results = reader.readtext(resized_frame)

        for (bbox, text, confidence) in results:
            if confidence > CONF_THRESHOLD:
                bbox = np.array(bbox).astype(int)

                min_x = np.min(bbox[:, 0])
                min_y = np.min(bbox[:, 1])
                max_x = np.max(bbox[:, 0])
                max_y = np.max(bbox[:, 1])

                # Draw rectangle and text
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                cleaned_text = text.replace(" ", "").upper()
                cv2.putText(frame, cleaned_text, (min_x, min_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                detected_plates.append(cleaned_text)

        if detected_plates:
            print(f"Detected Plates: {', '.join(detected_plates)}")

    frame_count += 1

    cv2.imshow('Live ANPR Feed (Press q to quit)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nANPR system stopped.")
