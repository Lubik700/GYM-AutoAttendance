import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, 'gym_members_exercise_tracking.csv'))

# print("Columns:", df.columns.tolist())
# print("\nGender values:", df['Gender'].unique())
# print("\nWorkout_Type values:", df['Workout_Type'].unique())
# print("\nExperience_Level values:", df['Experience_Level'].unique())
# print("\nShape:", df.shape)
# print(df['Workout_Type'].value_counts())
print(df['Workout_Type'])
