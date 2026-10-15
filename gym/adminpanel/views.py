from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import staff_required
from django.db.models import Q

# Import models/forms from the main app - adminpanel doesn't own its own models
from app.models import Notice
from app.forms import NoticeForm


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            auth_login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, "Invalid credentials or not authorized.")
    return render(request, 'adminpanel/login.html')


@staff_required
def admin_dashboard(request):
    counts = {'pending': 0, 'active': 0, 'inactive': 0}
    for user in User.objects.filter(is_staff=False):
        counts[get_member_status(user)['status']] += 1

    return render(request, 'adminpanel/dashboard.html', {
        'pending_count': counts['pending'],
        'active_members': counts['active'],
        'inactive_members': counts['inactive'],
        'total_notices': Notice.objects.count(),
    })

from app.utils import get_member_status

@staff_required
def admin_pending(request):
    pending_users = (User.objects
                     .filter(is_staff=False, subscriptions__isnull=True)
                     .select_related('profile')
                     .order_by('-date_joined'))
    return render(request, 'adminpanel/pending.html', {'pending_users': pending_users})

@staff_required
def admin_approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=False)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.username} has been approved.")
    return redirect('admin_pending')


@staff_required
def admin_reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_active=False)
    user.delete()
    messages.success(request, "Registration rejected and removed.")
    return redirect('admin_pending')


@staff_required
def admin_notices(request):
    notices = Notice.objects.all()
    return render(request, 'adminpanel/notices.html', {'notices': notices})


@staff_required
def admin_notice_add(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice added.")
            return redirect('admin_notices')
    else:
        form = NoticeForm()
    return render(request, 'adminpanel/notice_form.html', {'form': form, 'title': 'Add Notice'})


@staff_required
def admin_notice_edit(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice updated.")
            return redirect('admin_notices')
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'adminpanel/notice_form.html', {'form': form, 'title': 'Edit Notice'})


@staff_required
def admin_notice_delete(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    messages.success(request, "Notice deleted.")
    return redirect('admin_notices')


from app.models import Trainer, MembershipPackage, Subscription, Feedback, BMIRecord, WorkoutPlan
from app.forms import TrainerForm, MembershipPackageForm  # defined below

# ---------- MEMBERS ----------

@staff_required
def admin_members(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    members = User.objects.filter(is_staff=False).select_related('profile').order_by('-date_joined')
    if query:
        members = members.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(profile__name__icontains=query) | Q(profile__contact__icontains=query)
        )

    member_data = []
    for user in members:
        info = get_member_status(user)
        if status_filter and info['status'] != status_filter:
            continue
        member_data.append({'user': user, 'info': info})

    return render(request, 'adminpanel/members.html', {
        'member_data': member_data, 'query': query, 'status_filter': status_filter,
    })


@staff_required
def admin_member_detail(request, user_id):
    member = get_object_or_404(User, id=user_id, is_staff=False)
    profile = getattr(member, 'profile', None)
    subscriptions = Subscription.objects.filter(user=member).order_by('-start_date')
    feedbacks = Feedback.objects.filter(user=member).order_by('-submitted_at')
    bmi_records = BMIRecord.objects.filter(user=member).order_by('-recorded_at')[:5]
    workout_plan = WorkoutPlan.objects.filter(user=member).first()

    return render(request, 'adminpanel/member_detail.html', {
        'member': member,
        'profile': profile,
        'subscriptions': subscriptions,
        'feedbacks': feedbacks,
        'bmi_records': bmi_records,
        'workout_plan': workout_plan,
    })


# ---------- TRAINERS ----------

@staff_required
def admin_trainers(request):
    query = request.GET.get('q', '').strip()
    trainers = Trainer.objects.all()

    if query:
        trainers = trainers.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(certifications__icontains=query)
        )

    return render(request, 'adminpanel/trainers.html', {'trainers': trainers, 'query': query})


@staff_required
def admin_trainer_add(request):
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer added.")
            return redirect('admin_trainers')
    else:
        form = TrainerForm()
    return render(request, 'adminpanel/trainer_form.html', {'form': form, 'title': 'Add Trainer'})


@staff_required
def admin_trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer updated.")
            return redirect('admin_trainers')
    else:
        form = TrainerForm(instance=trainer)
    return render(request, 'adminpanel/trainer_form.html', {'form': form, 'title': 'Edit Trainer'})


@staff_required
def admin_trainer_delete(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    trainer.delete()
    messages.success(request, "Trainer removed.")
    return redirect('admin_trainers')


# ---------- MEMBERSHIP PACKAGES ----------

@staff_required
def admin_packages(request):
    query = request.GET.get('q', '').strip()
    packages = MembershipPackage.objects.all()
    if query:
            packages = packages.filter(
                Q(name__icontains=query) 
            )
    
    return render(request, 'adminpanel/packages.html', {'packages': packages,'query': query})


@staff_required
def admin_package_add(request):
    if request.method == 'POST':
        form = MembershipPackageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Package added.")
            return redirect('admin_packages')
    else:
        form = MembershipPackageForm()
    return render(request, 'adminpanel/package_form.html', {'form': form, 'title': 'Add Package'})


@staff_required
def admin_package_edit(request, package_id):
    package = get_object_or_404(MembershipPackage, id=package_id)
    if request.method == 'POST':
        form = MembershipPackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, "Package updated.")
            return redirect('admin_packages')
    else:
        form = MembershipPackageForm(instance=package)
    return render(request, 'adminpanel/package_form.html', {'form': form, 'title': 'Edit Package'})


@staff_required
def admin_package_delete(request, package_id):
    package = get_object_or_404(MembershipPackage, id=package_id)
    package.delete()
    messages.success(request, "Package deleted.")
    return redirect('admin_packages')


# ---------- SUBSCRIPTIONS (view-only list, assignment happens per-member or via Django admin for now) ----------

@staff_required
def admin_subscriptions(request):
    subscriptions = Subscription.objects.select_related('user', 'package').order_by('-start_date')
    return render(request, 'adminpanel/subscriptions.html', {'subscriptions': subscriptions})


# ---------- FEEDBACK (read-only) ----------

@staff_required
def admin_feedback(request):
    feedbacks = Feedback.objects.select_related('user').order_by('-submitted_at')
    return render(request, 'adminpanel/feedback.html', {'feedbacks': feedbacks})


from datetime import timedelta
from django.utils import timezone
from app.forms import AssignSubscriptionForm, AdminCreateMemberForm
from app.models import Profile, Subscription

@staff_required
def admin_assign_subscription(request, user_id):
    member = get_object_or_404(User, id=user_id, is_staff=False)

    if request.method == 'POST':
        form = AssignSubscriptionForm(request.POST)
        if form.is_valid():
            package = form.cleaned_data['package']
            payment_method = form.cleaned_data['payment_method']
            start_from_today = form.cleaned_data['start_from_today']

            latest = Subscription.objects.filter(user=member).order_by('-end_date').first()
            if latest and latest.end_date >= timezone.localdate() and not start_from_today:
                start = latest.end_date
            else:
                start = timezone.localdate()

            Subscription.objects.create(
                user=member,
                package=package,
                start_date=start,
                end_date=start + timedelta(days=package.duration_days),
                amount_paid=package.price,
                payment_method=payment_method,
            )

            # Activate the member now that they have a subscription
            if not member.is_active:
                member.is_active = True
                member.save()
                messages.success(request, f"{package.name} assigned. {member.username}'s account is now active.")
            else:
                messages.success(request, f"{package.name} assigned to {member.username}.")

            return redirect('admin_member_detail', user_id=member.id)
    else:
        form = AssignSubscriptionForm()

        return render(request, 'adminpanel/assign_subscription.html', {
        'form': form,
        'member': member,
        'member_status': get_member_status(member),
    })



@staff_required
def admin_add_member(request):
    if request.method == 'POST':
        form = AdminCreateMemberForm(request.POST)
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
            user.is_active = False   # stays inactive until a subscription is assigned
            user.save()

            Profile.objects.create(
                user=user,
                name=data['full_name'],
                contact=data['contact'],
                address=data['address'],
                date_of_birth=data['date_of_birth'],
                gender=data['gender'],
            )
            messages.success(request, f"{user.username} created. Assign a membership to activate their account.")
            return redirect('admin_assign_subscription', user_id=user.id)   # redirect straight to membership assignment
    else:
        form = AdminCreateMemberForm()

    return render(request, 'adminpanel/add_member.html', {'form': form})