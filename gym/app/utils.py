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

GRACE_DAYS = 2

def get_member_status(user):
    latest = Subscription.objects.filter(user=user).order_by('-end_date').first()
    if latest is None:
        return {'status': 'pending', 'latest': None, 'days_left': None, 'in_grace': False}

    days_left = (latest.end_date - timezone.localdate()).days
    days_expired = max(-days_left, 0)
    status = 'inactive' if days_expired > GRACE_DAYS else 'active'

    return {
        'status': status,
        'latest': latest,
        'days_left': days_left,
        'days_expired': days_expired,
        'in_grace': days_left < 0 and status == 'active',
    }


from datetime import timedelta

RENEWAL_WINDOW_DAYS = 5

def get_renewal_info(user):
    status = get_subscription_status(user)
    if not status['has_sub']:
        return {'can_renew': True, 'opens_on': None, 'days_left': None}

    days_left = status['days_left']
    return {
        'can_renew': days_left <= RENEWAL_WINDOW_DAYS,   # includes expired / grace-period members
        'opens_on': status['latest'].end_date - timedelta(days=RENEWAL_WINDOW_DAYS),
        'days_left': days_left,
    }