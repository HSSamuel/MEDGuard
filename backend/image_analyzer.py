import random
import time

def analyze_image(image_path):
    """
    This is a placeholder function to simulate an ML model analyzing an image.
    In a real application, this would be replaced with a call to a trained model.
    """
    # Simulate processing time (2 seconds added intentionally for demonstration purposes)
    time.sleep(2)

    # Simulate a random analysis result
    results = [
        {"label": "Suspicious tampering", "confidence": random.uniform(0.8, 0.95)},
        {"label": "Incorrect coloring", "confidence": random.uniform(0.7, 0.9)},
        {"label": "No defects found", "confidence": random.uniform(0.9, 0.98)},
        {"label": "Unusual dosage markings", "confidence": random.uniform(0.85, 0.99)},
    ]
    
    return random.choice(results)