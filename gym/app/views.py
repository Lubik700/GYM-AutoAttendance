# views.py



from .recommendation import get_recommendation, get_recommendation_by_type
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
from .models import Profile,MembershipPackage,Subscription
from .decorators import staff_required

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
from .utils import get_subscription_status


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
                    form.add_error(None, "Your account isn't active yet. If you didn't complete payment during registration, please register again or contact the gym.")

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

from django.utils import timezone
from .models import BMIRecord, WorkoutPlan, Notice
from .utils import get_subscription_status  # your existing helper

@login_required
def home(request):
    today_name = timezone.localdate().strftime('%A').lower()  # e.g. 'monday'

    # Subscription status
    sub_status = get_subscription_status(request.user)

    # Latest BMI record + trend (compare latest vs previous)
    bmi_records = BMIRecord.objects.filter(user=request.user).order_by('-recorded_at')[:2]
    latest_bmi = bmi_records[0] if bmi_records else None
    bmi_trend = None
    if len(bmi_records) == 2:
        diff = round(bmi_records[0].bmi - bmi_records[1].bmi, 1)
        bmi_trend = diff  # negative = lost BMI, positive = gained

    # Today's workout
    plan = WorkoutPlan.objects.filter(user=request.user).first()
    today_workout = None
    if plan:
        today_workout = plan.days.prefetch_related('exercises').filter(day=today_name).first()

    # Workout plan completion stat (days filled vs 7)
    days_planned = plan.days.count() if plan else 0

    # Notices
    important_notices = Notice.objects.filter(is_important=True)[:3]

    context = {
        'sub_status': sub_status,
        'latest_bmi': latest_bmi,
        'bmi_trend': bmi_trend,
        'today_workout': today_workout,
        'today_name': today_name,
        'days_planned': days_planned,
        'has_plan': plan is not None and days_planned > 0,
        'important_notices': important_notices,
        'member_since_days': (timezone.localdate() - request.user.date_joined.date()).days,
    }
    return render(request, 'app/home.html', context)

# def register_view(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             data = form.cleaned_data
#             base_username = data['email'].split('@')[0]
#             username = base_username
#             counter = 1
#             while User.objects.filter(username=username).exists():
#                 username = f"{base_username}{counter}"
#                 counter += 1

#             user = User.objects.create_user(
#                 username=username,
#                 email=data['email'],
#                 password=data['password'],
#             )
#             user.is_active = False   # pending approval
#             user.save()

#             Profile.objects.create(
#                 user=user,
#                 profile_picture=data.get('profile_picture'),
#                 name=data['name'],
#                 contact=data['contact'],
#                 address=data['address'],
#                 date_of_birth=data['date_of_birth'],
#                 gender=data['gender'],
#             )
#             return redirect('registration_success')
#     else:
#         form = RegisterForm()
#     return render(request, 'app/register.html', {'form': form})


# def registration_success_view(request):
#     return render(request, 'app/registration_success.html')



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
            user.is_active = False   # stays inactive until payment succeeds
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

            # Store the new user's id + chosen package so eSewa flow knows what to do after payment
            request.session['registration_user_id'] = user.id
            request.session['registration_package_id'] = data['package'].id

            return redirect('esewa_initiate_registration')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

from .utils import get_subscription_status, get_renewal_info
@login_required
def membership_view(request):
    packages = MembershipPackage.objects.filter(is_active=True)
    status = get_subscription_status(request.user)
    history = Subscription.objects.filter(user=request.user)
    return render(request, 'app/membership.html', {
        'packages': packages,
        'sub_status': status,
        'history': history,
        'renewal': get_renewal_info(request.user),
    })


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
    day_order = [d[0] for d in DAY_CHOICES]
    days = sorted(plan.days.prefetch_related('exercises'), key=lambda d: day_order.index(d.day))

    return render(request, 'app/workout_plan.html', {
        'plan': plan,
        'days': days,
        'has_days': plan.days.exists(),
        'DAY_CHOICES': DAY_CHOICES,
        'days_present': [d.day for d in days],
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
    return redirect('workout_plan')


@login_required
def add_workout_day(request, day_key):
    plan, _ = WorkoutPlan.objects.get_or_create(user=request.user)
    day_obj, created = WorkoutDay.objects.get_or_create(plan=plan, day=day_key)
    if not created:
        messages.info(request, f"{day_obj.get_day_display()} already exists in your plan.")
    return redirect('workout_plan')


@login_required
def edit_workout_day(request, day_id):
    day_obj = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    if request.method == 'POST':
        form = WorkoutDayForm(request.POST, instance=day_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Day updated.")
            return redirect('workout_plan')
    else:
        form = WorkoutDayForm(instance=day_obj)
    return render(request, 'app/edit_day.html', {'form': form, 'day': day_obj})


@login_required
def delete_workout_day(request, day_id):
    day_obj = get_object_or_404(WorkoutDay, id=day_id, plan__user=request.user)
    day_obj.delete()
    messages.success(request, "Day removed from your plan.")
    return redirect('workout_plan')


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
    return redirect('workout_plan')


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, day__plan__user=request.user)
    exercise.delete()
    return redirect('workout_plan')

from .models import Feedback
from .forms import FeedbackForm

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.user = request.user
            fb.save()
            messages.success(request, "Thanks for your feedback!")
            return redirect('feedback')
    else:
        form = FeedbackForm()

    my_feedback = Feedback.objects.filter(user=request.user)
    return render(request, 'app/feedback.html', {'form': form, 'my_feedback': my_feedback})

from .models import Profile

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'app/profile.html', {'profile': profile})



@login_required
def settings_view(request):
    pass


@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

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


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, CustomPasswordChangeForm

@login_required
def settings_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            password_form = CustomPasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('settings')

        elif 'change_password' in request.POST:
            profile_form = ProfileUpdateForm(instance=profile)
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # keeps user logged in after password change
                messages.success(request, "Password changed successfully.")
                return redirect('settings')
    else:
        profile_form = ProfileUpdateForm(instance=profile)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'app/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })


# views.py









from .models import BMIRecord, WorkoutPlan, WorkoutDay, Exercise
from .forms import BMIForm
from .recommendation import get_recommendation

@login_required
def bmi_calculator_view(request):
    recommendation = None
    latest_record = BMIRecord.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = BMIForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            predicted_type = predict_workout_type(
              age=record.age,
              gender=request.user.profile.gender,   # stored as 'male'/'female', normalized inside predict_workout_type
              bmi=record.bmi,
              experience_level=record.experience_level,
                )
            recommendation = get_recommendation_by_type(predicted_type)
            # recommendation = get_recommendation(record.bmi_category, record.goal)
            request.session['pending_recommendation'] = recommendation
            latest_record = record
    else:
        form = BMIForm()

    return render(request, 'app/bmi_calculator.html', {
        'form': form,
        'latest_record': latest_record,
        'recommendation': recommendation,
        'history': BMIRecord.objects.filter(user=request.user)[1:6],  # past records excluding latest
    })


from .ml_utils import predict_workout_type

# @login_required
# def bmi_calculator_view(request):
#     recommendation = None
#     latest_record = BMIRecord.objects.filter(user=request.user).first()

#     if request.method == 'POST':
#         form = BMIForm(request.POST)
#         if form.is_valid():
#             record = form.save(commit=False)
#             record.user = request.user
#             record.save()

#             predicted_type = predict_workout_type(
#                 age=record.age,
#                 gender=request.user.profile.get_gender_display(),  # must match 'Male'/'Female' from dataset
#                 bmi=record.bmi,
#                 experience_level=1  # or pull from a new form field, see note below
#             )

#             recommendation = get_recommendation_by_type(predicted_type)  # map predicted type to your routine dict
#             request.session['pending_recommendation'] = recommendation
#             latest_record = record
#     else:
#         form = BMIForm()

#     return render(request, 'app/bmi_calculator.html', {
#         'form': form,
#         'latest_record': latest_record,
#         'recommendation': recommendation,
#     })

@login_required
def apply_recommended_plan(request):
    recommendation = request.session.get('pending_recommendation')
    if not recommendation:
        messages.error(request, "No recommendation found. Please calculate your BMI first.")
        return redirect('bmi_calculator')

    plan, _ = WorkoutPlan.objects.get_or_create(user=request.user)

    if plan.days.exists():
        messages.warning(request, "You already have a workout plan. Clear it first to apply a new recommendation.")
        return redirect('workout_plan')

    for day_key, (focus, exercises) in recommendation['routine'].items():
        is_rest = focus is None
        day_obj = WorkoutDay.objects.create(plan=plan, day=day_key, focus=focus or '', is_rest_day=is_rest)
        if exercises:
            for i, (name, sets, reps) in enumerate(exercises):
                Exercise.objects.create(day=day_obj, name=name, sets=sets, reps=reps, order=i)

    messages.success(request, f"{recommendation['plan_name']} applied to your workout plan!")
    return redirect('workout_plan')


import hmac, hashlib, base64, uuid, json
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import MembershipPackage, Subscription

ESEWA_MERCHANT_CODE = "EPAYTEST"
ESEWA_SECRET_KEY = "8gBm/:&EnhH.1/q"
ESEWA_PAYMENT_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"

def generate_esewa_signature(total_amount, transaction_uuid, product_code):
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    hmac_obj = hmac.new(ESEWA_SECRET_KEY.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(hmac_obj.digest()).decode()



def esewa_initiate_registration(request):
    user_id = request.session.get('registration_user_id')
    package_id = request.session.get('registration_package_id')

    if not (user_id and package_id):
        messages.error(request, "Registration session expired. Please register again.")
        return redirect('register')

    package = get_object_or_404(MembershipPackage, id=package_id, is_active=True)
    transaction_uuid = f"reg-{user_id}-{uuid.uuid4().hex[:10]}"
    amount = package.price

    request.session['registration_txn_uuid'] = transaction_uuid

    signature = generate_esewa_signature(amount, transaction_uuid, ESEWA_MERCHANT_CODE)

    context = {
        'amount': amount,
        'tax_amount': 0,
        'total_amount': amount,
        'transaction_uuid': transaction_uuid,
        'product_code': ESEWA_MERCHANT_CODE,
        'product_service_charge': 0,
        'product_delivery_charge': 0,
        'success_url': request.build_absolute_uri('/register/esewa/success/'),
        'failure_url': request.build_absolute_uri('/register/esewa/failure/'),
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
        'payment_url': ESEWA_PAYMENT_URL,
    }
    return render(request, 'app/esewa_redirect.html', context)


def esewa_registration_success(request):
    user_id = request.session.pop('registration_user_id', None)
    package_id = request.session.pop('registration_package_id', None)
    txn_uuid = request.session.pop('registration_txn_uuid', None)
    encoded_data = request.GET.get('data')

    if not (user_id and package_id and txn_uuid and encoded_data):
        messages.error(request, "Payment verification failed. Please try registering again.")
        return redirect('register')

    decoded = json.loads(base64.b64decode(encoded_data))
    if decoded.get('status') != 'COMPLETE' or decoded.get('transaction_uuid') != txn_uuid:
        messages.error(request, "Payment could not be verified.")
        return redirect('register')

    user = get_object_or_404(User, id=user_id)
    package = get_object_or_404(MembershipPackage, id=package_id)

    start = timezone.localdate()
    Subscription.objects.create(
        user=user,
        package=package,
        start_date=start,
        end_date=start + timedelta(days=package.duration_days),
        amount_paid=package.price,
        payment_method='esewa',
        transaction_id=txn_uuid,
    )

    user.is_active = True
    user.save()

    messages.success(request, "Registration and payment successful! You can now log in.")
    return redirect('login')


def esewa_registration_failure(request):
    user_id = request.session.get('registration_user_id')
    messages.error(request, "Payment failed or was cancelled. You can retry payment or contact the gym for assistance.")
    if user_id:
        return redirect('esewa_initiate_registration')  # let them retry
    return redirect('register')


@login_required
def esewa_initiate(request, package_id):
    renewal = get_renewal_info(request.user)
    if not renewal['can_renew']:
        messages.error(
            request,
            f"Your membership is still active. You can renew from {renewal['opens_on']:%d %b %Y}."
        )
        return redirect('membership')
    package = get_object_or_404(MembershipPackage, id=package_id, is_active=True)
    transaction_uuid = f"{request.user.id}-{uuid.uuid4().hex[:10]}"
    amount = package.price

    request.session['pending_package_id'] = package.id
    request.session['pending_txn_uuid'] = transaction_uuid

    signature = generate_esewa_signature(amount, transaction_uuid, ESEWA_MERCHANT_CODE)

    context = {
        'amount': amount,
        'tax_amount': 0,
        'total_amount': amount,
        'transaction_uuid': transaction_uuid,
        'product_code': ESEWA_MERCHANT_CODE,
        'product_service_charge': 0,
        'product_delivery_charge': 0,
        'success_url': request.build_absolute_uri('/membership/esewa/success/'),
        'failure_url': request.build_absolute_uri('/membership/esewa/failure/'),
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
        'payment_url': ESEWA_PAYMENT_URL,
    }
    return render(request, 'app/esewa_redirect.html', context)


@login_required
def esewa_success(request):
    package_id = request.session.pop('pending_package_id', None)
    txn_uuid = request.session.pop('pending_txn_uuid', None)
    encoded_data = request.GET.get('data')

    if not (package_id and txn_uuid and encoded_data):
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect('membership')

    decoded = json.loads(base64.b64decode(encoded_data))

    if decoded.get('status') != 'COMPLETE' or decoded.get('transaction_uuid') != txn_uuid:
        messages.error(request, "Payment could not be verified.")
        return redirect('membership')

    package = get_object_or_404(MembershipPackage, id=package_id)
    latest = Subscription.objects.filter(user=request.user).order_by('-end_date').first()
    start = latest.end_date if (latest and latest.end_date >= timezone.localdate()) else timezone.localdate()

    Subscription.objects.create(
        user=request.user,
        package=package,
        start_date=start,
        end_date=start + timedelta(days=package.duration_days),
        amount_paid=package.price,
        payment_method='esewa',
        transaction_id=txn_uuid,
    )
    messages.success(request, "Payment successful! Your membership has been renewed.")
    return redirect('membership')


@login_required
def esewa_failure(request):
    messages.error(request, "Payment was cancelled or failed.")
    return redirect('membership')


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'app/landing.html')


import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def bmi_progress_view(request):
    records = BMIRecord.objects.filter(user=request.user).order_by('recorded_at')

    chart_data = {
        'labels': [r.recorded_at.strftime('%d %b') for r in records],
        'bmi_values': [r.bmi for r in records],
        'weight_values': [r.weight_kg for r in records],
    }

    return render(request, 'app/bmi_progress.html', {
        'records': records,
        'chart_data': json.dumps(chart_data, cls=DjangoJSONEncoder),
        'latest': records.last(),
    })


