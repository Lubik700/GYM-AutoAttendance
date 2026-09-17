import joblib
import os
from django.conf import settings

ML_DIR = os.path.join(settings.BASE_DIR, 'ml')

_model = joblib.load(os.path.join(ML_DIR, 'workout_model.pkl'))
_gender_encoder = joblib.load(os.path.join(ML_DIR, 'gender_encoder.pkl'))
_workout_encoder = joblib.load(os.path.join(ML_DIR, 'workout_encoder.pkl'))

def predict_workout_type(age, gender, bmi, experience_level):
    """
    gender: accepts 'male'/'female' (your Profile's stored format) - normalized here
    experience_level: 1, 2, or 3
    Returns: predicted workout type string, e.g. 'Strength'
    """
    gender_normalized = gender.strip().capitalize()  # 'male' -> 'Male', 'female' -> 'Female'
    gender_encoded = _gender_encoder.transform([gender_normalized])[0]

    features = [[age, gender_encoded, bmi, experience_level]]
    prediction = _model.predict(features)[0]
    return _workout_encoder.inverse_transform([prediction])[0]