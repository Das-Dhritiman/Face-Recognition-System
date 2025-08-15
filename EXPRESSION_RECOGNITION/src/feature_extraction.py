import numpy as np

def extract_features(landmarks):
    """
    Extracts features from facial landmarks.
    
    The features are the coordinates of each landmark relative to the
    position of the nose (landmark 30). This normalization helps make
    the features independent of the face's position and size in the frame.

    Args:
        landmarks (list of tuples): A list of (x, y) coordinates for the 68 facial landmarks.

    Returns:
        list: A flattened list of normalized landmark coordinates.
    """
    features = []
    # The nose tip (landmark 30) is a good reference point for normalization.
    nose_point = landmarks[30] 
    for i in range(len(landmarks)):
        # Calculate the x and y distance from the nose point
        features.append(landmarks[i][0] - nose_point[0])
        features.append(landmarks[i][1] - nose_point[1])
    return features
