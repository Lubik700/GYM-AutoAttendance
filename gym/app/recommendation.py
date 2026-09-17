WORKOUT_RECOMMENDATIONS = {
    ('Underweight', 'gain'): {
        'plan_name': 'Muscle Gain Program',
        'description': 'Focus on strength training with progressive overload and a calorie surplus.',
        'routine': {
            'sunday':    ('Chest & Triceps', [('Bench Press', 4, '8'), ('Incline Dumbbell Press', 3, '10'), ('Tricep Pushdowns', 3, '12')]),
            'monday':    ('Back & Biceps', [('Deadlifts', 4, '6'), ('Barbell Rows', 3, '8'), ('Bicep Curls', 3, '10')]),
            'tuesday':   ('Legs', [('Squats', 4, '8'), ('Leg Press', 3, '10'), ('Calf Raises', 3, '15')]),
            'wednesday': (None, None),
            'thursday':  ('Shoulders', [('Overhead Press', 4, '8'), ('Lateral Raises', 3, '12')]),
            'friday':    ('Full Body', [('Pull-ups', 3, '8'), ('Dips', 3, '10')]),
            'saturday':  (None, None),
        }
    },
    ('Normal', 'maintain'): {
        'plan_name': 'General Fitness Maintenance',
        'description': 'Balanced mix of strength and cardio to maintain your current fitness level.',
        'routine': {
            'sunday':    ('Full Body Strength', [('Squats', 3, '12'), ('Push-ups', 3, '15'), ('Rows', 3, '12')]),
            'monday':    ('Cardio', [('Running', 1, '25 min'), ('Jump Rope', 3, '2 min')]),
            'tuesday':   ('Upper Body', [('Bench Press', 3, '10'), ('Shoulder Press', 3, '10')]),
            'wednesday': (None, None),
            'thursday':  ('Lower Body', [('Lunges', 3, '12'), ('Deadlifts', 3, '10')]),
            'friday':    ('Cardio + Core', [('Cycling', 1, '20 min'), ('Plank', 3, '45 sec')]),
            'saturday':  (None, None),
        }
    },
    ('Overweight', 'lose'): {
        'plan_name': 'Fat Loss Program',
        'description': 'Higher-frequency cardio combined with full-body resistance training to support a calorie deficit.',
        'routine': {
            'sunday':    ('Cardio', [('Treadmill', 1, '30 min'), ('Jump Rope', 3, '3 min')]),
            'monday':    ('Full Body Circuit', [('Squats', 3, '15'), ('Push-ups', 3, '15'), ('Rows', 3, '15')]),
            'tuesday':   ('Cardio', [('Cycling', 1, '30 min')]),
            'wednesday': ('Full Body Circuit', [('Lunges', 3, '15'), ('Burpees', 3, '12')]),
            'thursday':  (None, None),
            'friday':    ('Cardio + Core', [('Running', 1, '25 min'), ('Plank', 3, '45 sec')]),
            'saturday':  (None, None),
        }
    },
    ('Obese', 'lose'): {
        'plan_name': 'Beginner Fat Loss Program',
        'description': 'Low-impact cardio and light resistance training, prioritizing consistency and joint safety.',
        'routine': {
            'sunday':    ('Light Cardio', [('Brisk Walking', 1, '20 min')]),
            'monday':    ('Light Strength', [('Bodyweight Squats', 3, '10'), ('Wall Push-ups', 3, '10')]),
            'tuesday':   ('Light Cardio', [('Stationary Cycling', 1, '20 min')]),
            'wednesday': (None, None),
            'thursday':  ('Light Strength', [('Seated Rows', 3, '10'), ('Assisted Lunges', 3, '10')]),
            'friday':    ('Light Cardio', [('Swimming or Walking', 1, '25 min')]),
            'saturday':  (None, None),
        }
    },
}

def get_recommendation(bmi_category, goal):
    key = (bmi_category, goal)
    if key in WORKOUT_RECOMMENDATIONS:
        return WORKOUT_RECOMMENDATIONS[key]
    # fallback: match by category only if exact (category, goal) pair isn't defined
    for (cat, g), plan in WORKOUT_RECOMMENDATIONS.items():
        if cat == bmi_category:
            return plan
    return WORKOUT_RECOMMENDATIONS[('Normal', 'maintain')]  # safe default

def get_recommendation_by_type(workout_type):
    """
    Maps ML-predicted workout type ('Yoga', 'HIIT', 'Cardio', 'Strength')
    to an existing routine dictionary.
    """
    mapping = {
        'Strength': WORKOUT_RECOMMENDATIONS[('Underweight', 'gain')],
        'Cardio': WORKOUT_RECOMMENDATIONS[('Overweight', 'lose')],
        'HIIT': WORKOUT_RECOMMENDATIONS[('Obese', 'lose')],
        'Yoga': WORKOUT_RECOMMENDATIONS[('Normal', 'maintain')],
    }
    return mapping.get(workout_type, WORKOUT_RECOMMENDATIONS[('Normal', 'maintain')])