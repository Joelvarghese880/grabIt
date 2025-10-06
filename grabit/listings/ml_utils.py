import os
import joblib
import pandas as pd
from django.conf import settings
import numpy as np

MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'kerala_rent_predictor.pkl')

# Backup prediction formula
def backup_predict(location, bedrooms, size):
    location_factors = {
        'Kochi': 1.2, 'Trivandrum': 1.0, 'Munnar': 1.5,
        'Alappuzha': 1.1, 'Thrissur': 0.9
    }
    base_price = 1200 * bedrooms
    location_factor = location_factors.get(location, 1.0)
    size_factor = np.log1p(size/500)
    return base_price * location_factor * size_factor

# Load model with verification
try:
    model = joblib.load(MODEL_PATH)
    # Verify it's a proper sklearn model
    if not hasattr(model, 'predict'):
        raise ValueError("Invalid model object")
except Exception as e:
    print(f"⚠️ Model loading failed: {e}. Using backup predictor.")
    model = None

def predict_rent(location, bedrooms, size):
    try:
        if model:
            input_data = pd.DataFrame({
                'location': [location],
                'bedrooms': [bedrooms],
                'size': [size]
            })
            return float(model.predict(input_data)[0])
        return backup_predict(location, bedrooms, size)
    except Exception as e:
        print(f"Prediction error for {location}: {str(e)}")
        return backup_predict(location, bedrooms, size)