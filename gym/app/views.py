# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Notice
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, RegisterForm
from .models import Profile


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from .forms import LoginForm
from django.contrib.auth import logout
from .models import Equipment
from .models import Trainer


@login_required
def home(request):
    return render(request, "app/home.html")


from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            try:
                user_obj = User.objects.get(Q(username=identifier) | Q(email=identifier))
            except User.DoesNotExist:
                user_obj = None

            if user_obj and user_obj.check_password(password):
                if not user_obj.is_active:
                    form.add_error(None, "Your registration is pending approval. Please visit the gym for verification.")
                else:
                    user_obj.backend = 'app.backends.EmailOrUsernameBackend'
                    login(request, user_obj)
                    request.session.set_expiry(60 * 60 * 24 * 30 if remember_me else 0)
                    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
                    return redirect(next_url)
            else:
                form.add_error(None, "Invalid username/email or password.")
    else:
        form = LoginForm()
    next_url = request.GET.get('next', '')
    return render(request, 'app/login.html', {'form': form, 'next': next_url})



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            base_username = data['email'].split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
            )
            user.is_active = False   # pending approval
            user.save()

            Profile.objects.create(
                user=user,
                profile_picture=data.get('profile_picture'),
                name=data['name'],
                contact=data['contact'],
                address=data['address'],
                date_of_birth=data['date_of_birth'],
                gender=data['gender'],
            )
            return redirect('registration_success')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})


def registration_success_view(request):
    return render(request, 'app/registration_success.html')


@login_required
def membership_view(request):
    return render(request, "app/register.html")


@login_required
def equipment_view(request):
    equipment_list = Equipment.objects.all()
    paginator = Paginator(equipment_list, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/equipment.html', {
        'equipment_list': page_obj,
        'page_obj': page_obj,
    })

@login_required
def trainers_view(request):
    trainers = Trainer.objects.filter(is_active=True)
    return render(request, 'app/trainers.html', {'trainers': trainers})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WorkoutPlan, WorkoutDay, Exercise, DAY_CHOICES
from .forms import ExerciseForm, WorkoutDayForm


DEFAULT_ROUTINE = {
    'sunday':    ('Chest & Triceps', [('Bench Press', 4, '10'), ('Push-ups', 3, '15'), ('Tricep Dips', 3, '12')]),
    'monday':    ('Back & Biceps', [('Pull-ups', 4, '8'), ('Barbell Rows', 3, '10'), ('Bicep Curls', 3, '12')]),
    'tuesday':   ('Legs', [('Squats', 4, '10'), ('Lunges', 3, '12'), ('Calf Raises', 3, '15')]),
    'wednesday': ('Cardio', [('Treadmill Run', 1, '20 min'), ('Jump Rope', 3, '2 min')]),
    'thursday':  ('Shoulders & Abs', [('Shoulder Press', 4, '10'), ('Lateral Raises', 3, '12'), ('Plank', 3, '45 sec')]),
    'friday':    ('Full Body', [('Deadlifts', 3, '8'), ('Burpees', 3, '12'), ('Mountain Climbers', 3, '20')]),
    'saturday':  (None, None),  # rest day
}


@login_required
def workout_plan_view(request):
    plan, _ = WorkoutPlan.objects.get_or_create(user=request.user)
    days = plan.days.prefetch_related('exercises').order_by(
        'id'
    )
    # keep consistent Sun-Sat order even if partially created
    day_order = [d[0] for d in DAY_CHOICES]
    days = sorted(plan.days.prefetch_related('exercises'), key=lambda d: day_order.index(d.day))

    return render(request, 'app/workout_plan.html', {
        'plan': plan,
        'days': days,
        'has_days': plan.days.exists(),
    })


@login_required
def suggest_workout_plan(request):
    plan, _ = WorkoutPlan.objects.get_or_create(user=request.user)

    if plan.days.exists():
        messages.info(request, "You already have a workout plan. Clear it first if you want to reset to the suggested routine.")
        return redirect('app/workout_plan')

    for day_key, (focus, exercises) in DEFAULT_ROUTINE.items():
        is_rest = focus is None
        day_obj = WorkoutDay.objects.create(
            plan=plan, day=day_key, focus=focus or '', is_rest_day=is_rest
        )
        if exercises:
            for i, (name, sets, reps) in enumerate(exercises):
                Exercise.objects.create(day=day_obj, name=name, sets=sets, reps=reps, order=i)

    messages.success(request, "Suggested workout plan added. Feel free to customize it.")
    return redirect('app/workout_plan')


@login_required
def add_workout_day(request, day_key):
    plan, _ = WorkoutPlan.objects.get_or_create(user=request.user)
    day_obj, created = WorkoutDay.objects.get_or_create(plan=plan, day=day_key)
    if not created:
        messages.info(request, f"{day_obj.get_day_display()} already exists in your plan.")
    return redirect('app/workout_plan')


@login_required
def edit_workout_day(request, day_id):
    day_obj = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    if request.method == 'POST':
        form = WorkoutDayForm(request.POST, instance=day_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Day updated.")
            return redirect('app/workout_plan')
    else:
        form = WorkoutDayForm(instance=day_obj)
    return render(request, 'app/edit_day.html', {'form': form, 'day': day_obj})


@login_required
def delete_workout_day(request, day_id):
    day_obj = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    day_obj.delete()
    messages.success(request, "Day removed from your plan.")
    return redirect('app/workout_plan')


@login_required
def add_exercise(request, day_id):
    day_obj = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.day = day_obj
            exercise.order = day_obj.exercises.count()
            exercise.save()
            messages.success(request, "Exercise added.")
    return redirect('app/workout_plan')


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, day__plan__user=request.user)
    exercise.delete()
    return redirect('app/workout_plan')

@login_required
def feedback_view(request):
    pass


@login_required
def profile_view(request):
    pass



@login_required
def settings_view(request):
    pass


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# # views.py

@login_required
def notices_view(request):
    notices = Notice.objects.all()
    paginator = Paginator(notices, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/notices.html', {
        'notices': page_obj,
        'page_obj': page_obj,
    })

