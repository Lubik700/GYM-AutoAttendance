from django.utils import timezone
from .models import Subscription

def get_subscription_status(user):
    latest = Subscription.objects.filter(user=user).order_by('-end_date').first()
    if latest is None:
        return {'has_sub': False, 'is_active': False, 'days_left': None, 'days_expired': None, 'latest': None}

    today = timezone.localdate()
    days_left = (latest.end_date - today).days
    days_expired = (today - latest.end_date).days

    return {
        'has_sub': True,
        'is_active': days_left >= 0,
        'days_left': days_left,
        'days_expired': days_expired,
        'latest': latest,
    }