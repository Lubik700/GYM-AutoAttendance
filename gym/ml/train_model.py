import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(os.path.join(BASE_DIR, 'gym_members_exercise_tracking.csv'))

# Encode Gender (Male/Female -> 0/1)
gender_encoder = LabelEncoder()
df['Gender_encoded'] = gender_encoder.fit_transform(df['Gender'])

# Encode Workout_Type (Yoga/HIIT/Cardio/Strength -> 0/1/2/3)
workout_encoder = LabelEncoder()
df['Workout_encoded'] = workout_encoder.fit_transform(df['Workout_Type'])

# Features - note exact column names with spaces/parentheses
X = df[['Age', 'Gender_encoded', 'BMI', 'Experience_Level']]
y = df['Workout_encoded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model accuracy: {accuracy * 100:.2f}%")

# Show what the encoders actually mapped, for sanity-checking
print("Gender classes:", list(gender_encoder.classes_))
print("Workout classes:", list(workout_encoder.classes_))

joblib.dump(model, os.path.join(BASE_DIR, 'workout_model.pkl'))
joblib.dump(gender_encoder, os.path.join(BASE_DIR, 'gender_encoder.pkl'))
joblib.dump(workout_encoder, os.path.join(BASE_DIR, 'workout_encoder.pkl'))

print("Model and encoders saved successfully.")