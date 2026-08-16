from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=15)
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