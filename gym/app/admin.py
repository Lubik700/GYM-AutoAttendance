# from django.contrib import admin
# from .models import Profile

# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('name', 'user', 'contact', 'gender', 'date_of_birth')
#     search_fields = ('name', 'user__username', 'user__email', 'contact')
#     list_filter = ('gender',)

# from django.contrib import admin
# from django.contrib.auth.models import User
# from django.contrib.auth.admin import UserAdmin
# from .models import Profile

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'

# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)

# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from .models import Notice
from .models import Equipment
# --- Inline profile shown on User admin page ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# --- Regular User admin (active clients) ---
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_active', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# --- Proxy model just for the "Pending Registrations" admin section ---
class PendingRegistration(User):
    class Meta:
        proxy = True
        verbose_name = 'Pending Registration'
        verbose_name_plural = 'Pending Registrations'


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_name', 'get_contact', 'date_joined')
    actions = ['approve_registrations']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_active=False)

    def get_name(self, obj):
        return obj.profile.name if hasattr(obj, 'profile') else '-'
    get_name.short_description = 'Name'

    def get_contact(self, obj):
        return obj.profile.contact if hasattr(obj, 'profile') else '-'
    get_contact.short_description = 'Contact'

    def approve_registrations(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} registration(s) approved. They can now log in.")
    approve_registrations.short_description = "Approve selected registrations"

    def has_add_permission(self, request):
        return False  # pending users are only created via registration flow





@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_important', 'uploaded_at')
    list_filter = ('is_important',)
    search_fields = ('title', 'description')
    ordering = ('-uploaded_at',)




@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'condition', 'quantity', 'added_at')
    list_filter = ('condition', 'brand')
    search_fields = ('name', 'brand', 'specification')
    ordering = ('name',)


from .models import Trainer

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'experience_years', 'contact', 'is_active')
    list_filter = ('specialization', 'is_active')
    search_fields = ('name', 'bio', 'certifications')
    ordering = ('name',)

from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'rating', 'submitted_at')
    list_filter = ('rating', 'submitted_at')
    search_fields = ('subject', 'message', 'user__username', 'user__email')
    readonly_fields = ('user', 'subject', 'message', 'rating', 'submitted_at')

    def has_add_permission(self, request):
        return False  # admin shouldn't create fake feedback




from .models import MembershipPackage, Subscription

@admin.register(MembershipPackage)
class MembershipPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'start_date', 'end_date', 'payment_method', 'is_active')
    list_filter = ('payment_method', 'package')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ['user']

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True