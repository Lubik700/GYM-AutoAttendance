from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)
phone_validator = RegexValidator(
    regex=r'^(97|98)\d{8}$',
    message="Phone number must start with 97 or 98 and be exactly 10 digits."
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=10, validators=[phone_validator])
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name


#notices
class Notice(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_important = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


#equipments
class Equipment(models.Model):
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('needs_repair', 'Needs Repair'),
    )

    name = models.CharField(max_length=150)
    specification = models.TextField(blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    quantity = models.PositiveIntegerField(default=1)
    brand = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='equipment_pics/', blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


#trainer
class Trainer(models.Model):
    SPECIALIZATION_CHOICES = (
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('yoga', 'Yoga'),
        ('crossfit', 'CrossFit'),
        ('nutrition', 'Nutrition Coaching'),
        ('rehab', 'Rehabilitation'),
        ('general', 'General Fitness'),
    )

    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='trainer_pics/', blank=True, null=True)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, default='general')
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    certifications = models.CharField(max_length=255, blank=True, help_text="Comma-separated, e.g. ACE, NASM")
    contact = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    available_days = models.CharField(max_length=100, blank=True, help_text="e.g. Mon-Fri, 6AM-8PM")
    is_active = models.BooleanField(default=True, help_text="Uncheck if trainer is no longer with the gym")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


from django.conf import settings

DAY_CHOICES = (
    ('sunday', 'Sunday'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
)

class WorkoutPlan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_plan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Workout Plan"


class WorkoutDay(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='days')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    is_rest_day = models.BooleanField(default=False)
    focus = models.CharField(max_length=100, blank=True, help_text="e.g. Chest & Triceps")

    class Meta:
        unique_together = ('plan', 'day')
        ordering = ['id']

    def __str__(self):
        return f"{self.get_day_display()} - {self.plan.user.username}"


class Exercise(models.Model):
    day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=150)
    sets = models.PositiveIntegerField(blank=True, null=True)
    reps = models.CharField(max_length=50, blank=True, help_text="e.g. 12 or 30 sec")
    notes = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name



class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=150)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5,
        help_text="1 = Poor, 5 = Excellent"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.subject} - {self.user.username}"


from django.utils import timezone
from datetime import timedelta

class MembershipPackage(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField(help_text="e.g. 30 for monthly, 365 for yearly")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to stop offering this package")

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - Rs. {self.price} ({self.duration_days} days)"


class Subscription(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Cash (In-Person)'),
        ('esewa', 'eSewa'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(MembershipPackage, on_delete=models.PROTECT)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.package.duration_days)
        if not self.amount_paid:
            self.amount_paid = self.package.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.package.name} ({self.start_date} to {self.end_date})"

    @property
    def is_active(self):
        return self.end_date >= timezone.localdate()

    @property
    def days_left(self):
        return (self.end_date - timezone.localdate()).days




class BMIRecord(models.Model):
    EXPERIENCE_CHOICES = (
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Expert'),
    )
    ACTIVITY_CHOICES = (
        ('sedentary', 'Sedentary (little/no exercise)'),
        ('light', 'Lightly active (1-3 days/week)'),
        ('moderate', 'Moderately active (3-5 days/week)'),
        ('active', 'Very active (6-7 days/week)'),
    )
    GOAL_CHOICES = (
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Muscle'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bmi_records')
    height_cm = models.FloatField(help_text="Height in centimeters")
    weight_kg = models.FloatField(help_text="Weight in kilograms")
    age = models.PositiveIntegerField()
    activity_level = models.CharField(max_length=10, choices=ACTIVITY_CHOICES, default='moderate')
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain')
    experience_level = models.PositiveSmallIntegerField(choices=EXPERIENCE_CHOICES, default=1)   # <-- belongs here
    bmi = models.FloatField(editable=False)
    bmi_category = models.CharField(max_length=20, editable=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def calculate_bmi(self):
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m ** 2), 1)

    def get_category(self, bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def save(self, *args, **kwargs):
        self.bmi = self.calculate_bmi()
        self.bmi_category = self.get_category(self.bmi)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - BMI {self.bmi} ({self.bmi_category})"