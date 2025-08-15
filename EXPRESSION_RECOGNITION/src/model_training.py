import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle
import os

# Define paths
DATA_DIR = 'data'
MODELS_DIR = 'models'
CSV_PATH = os.path.join(DATA_DIR, 'expressions.csv')
MODEL_PATH = os.path.join(MODELS_DIR, 'expression_model.pkl')

def train_model():
    """
    Trains a Support Vector Machine (SVM) classifier on the collected
    expression data and saves the trained model.
    """
    # Ensure the necessary directories and files exist
    if not os.path.exists(CSV_PATH):
        print(f"Error: Data file not found at {CSV_PATH}. Please collect data first using '--mode collect'.")
        return
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Load the dataset
    data = pd.read_csv(CSV_PATH)
    
    if data.shape[0] < 2:
        print("Not enough data to train the model. Please collect more data.")
        return

    # Separate features (X) and labels (y)
    X = data.drop('expression', axis=1)
    y = data['expression']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Initialize and train the SVM model
    # Using probability=True allows us to get confidence scores later
    print("Training the model...")
    model = SVC(kernel='linear', probability=True, C=1.0)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Save the trained model to a file
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

    print(f"Model trained and saved as {MODEL_PATH}")

