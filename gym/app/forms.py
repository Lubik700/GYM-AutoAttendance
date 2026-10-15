from django import forms
from django.contrib.auth.models import User
from .models import Profile,BMIRecord
from . import models
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from .models import MembershipPackage
class RegisterForm(forms.Form):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'file-input-hidden',
            'accept': 'image/jpeg,image/png,image/webp',
            'onchange': 'previewAvatar(this)',
        })
    )
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
            "id":"id_name"
        })
    )
    contact = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'e.g. 98XXXXXXXX',
            'autocomplete': 'tel',
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'input-field resize-none',
            'rows': 2,
            'placeholder': 'Enter your full address',
            'id':"id_address"
        })
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'id': 'id_dob',   # keep matching your existing JS which targets id_dob
        })
    )
    gender = forms.ChoiceField(
        choices=Profile._meta.get_field('gender').choices,
        widget=forms.RadioSelect
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
            'id':"id_email",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field pr-11',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
            'id':"id_password",
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-field pr-11',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
            'id':"id_confirm_password",
        })
    )
    package = forms.ModelChoiceField(
        queryset=MembershipPackage.objects.filter(is_active=True),
        empty_label="Select a membership package",
        widget=forms.Select(attrs={'class': 'input-field'})
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms & Conditions to continue.'}
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise forms.ValidationError(e.messages)
        return password
    def clean_contact(self):
            contact = self.cleaned_data.get('contact', '').strip()
            if not re.match(r'^(97|98)\d{8}$', contact):
                raise forms.ValidationError("Enter a valid 10-digit number starting with 97 or 98.")
            return contact
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data
    
  






# Shared Tailwind classes so inputs keep their current look
INPUT_CLASSES = (
    "w-full bg-dark-bg border border-dark-secondary text-white rounded-xl "
    "pl-11 pr-4 py-3 text-sm placeholder-gray-500 focus-primary "
    "transition-all duration-200 hover:border-gray-500"
)

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your username or email',
            'autofocus': True,
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES.replace('pr-4', 'pr-12'),
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 rounded border-dark-secondary bg-dark-bg text-primary '
                     'focus:ring-primary focus:ring-offset-0 focus:ring-2 cursor-pointer'
        })
    )

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = models.Exercise
        fields = ['name', 'sets', 'reps', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Exercise name'}),
            'sets': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Sets'}),
            'reps': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Reps (e.g. 12)'}),
            'notes': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Notes (optional)'}),
        }


class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = models.WorkoutDay
        fields = ['focus', 'is_rest_day']
        widgets = {
            'focus': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'e.g. Chest & Triceps'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = ['subject', 'message', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'What is this about?',
            }),
            'message': forms.Textarea(attrs={
                'class': 'input-field resize-none',
                'rows': 5,
                'placeholder': 'Tell us what you think...',
            }),
            'rating': forms.Select(attrs={'class': 'input-field'}),
        }


from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'name', 'contact', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'contact': forms.TextInput(attrs={'class': 'input-field'}),
            'address': forms.Textarea(attrs={'class': 'input-field resize-none', 'rows': 2}),
        }


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-field'})


class BMIForm(forms.ModelForm):
    class Meta:
        model = BMIRecord
        fields = ['height_cm', 'weight_kg', 'age', 'activity_level', 'goal']
        widgets = {
            'height_cm': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'e.g. 170', 'step': '0.1'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'e.g. 65', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'e.g. 25'}),
            'activity_level': forms.Select(attrs={'class': 'input-field'}),
            'goal': forms.Select(attrs={'class': 'input-field'}),
        }



from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description', 'is_important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-input', 'rows': 4}),
        }



from .models import Trainer, MembershipPackage
from django import forms
class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['name', 'photo', 'specialization', 'experience_years', 'bio',
                  'certifications', 'contact', 'email', 'available_days', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'admin-input'}),
            'specialization': forms.Select(attrs={'class': 'admin-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'admin-input'}),
            'bio': forms.Textarea(attrs={'class': 'admin-input', 'rows': 3}),
            'certifications': forms.TextInput(attrs={'class': 'admin-input'}),
            'contact': forms.TextInput(attrs={'class': 'admin-input'}),
            'email': forms.EmailInput(attrs={'class': 'admin-input'}),
            'available_days': forms.TextInput(attrs={'class': 'admin-input'}),
        }


class MembershipPackageForm(forms.ModelForm):
    class Meta:
        model = MembershipPackage
        fields = ['name', 'price', 'duration_days', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'admin-input'}),
            'price': forms.NumberInput(attrs={'class': 'admin-input'}),
            'duration_days': forms.NumberInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-input', 'rows': 3}),
        }


from django.contrib.auth.models import User
from .models import MembershipPackage

class AssignSubscriptionForm(forms.Form):
    package = forms.ModelChoiceField(
        queryset=MembershipPackage.objects.filter(is_active=True),
        empty_label="Select membership package",
        widget=forms.Select(attrs={'class': 'admin-input'})
    )
    payment_method = forms.ChoiceField(
        choices=[('', 'Select payment method'), ('cash', 'Cash (In-Person)'), ('esewa', 'eSewa')],
        widget=forms.Select(attrs={'class': 'admin-input'})
    )
    start_from_today = forms.BooleanField(
        required=False,
        label="Start from today (instead of extending current expiry)"
    )


class AdminCreateMemberForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'admin-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'admin-input'}))
    contact = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'admin-input'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'admin-input', 'rows': 2}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'admin-input'}))
    gender = forms.ChoiceField(choices=(('male', 'Male'), ('female', 'Female'), ('other', 'Other')),
                                widget=forms.Select(attrs={'class': 'admin-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'admin-input'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_contact(self):
        import re
        contact = self.cleaned_data.get('contact', '').strip()
        if not re.match(r'^(97|98)\d{8}$', contact):
            raise forms.ValidationError("Enter a valid 10-digit number starting with 97 or 98.")
        return contact