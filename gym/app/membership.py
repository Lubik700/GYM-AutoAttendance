"""
Place at: app/membership.py

Rule: a member keeps full access until end_date + GRACE_DAYS.
After that the account is blocked: they can only renew, nothing else.
Staff/superusers and users with no subscription history are never blocked.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

GRACE_DAYS = getattr(settings, 'MEMBERSHIP_GRACE_DAYS', 5)
RENEWAL_WINDOW_SECONDS = 10 * 60   # how long the "Renew" button stays valid after login attempt


def latest_subscription(user):
    return user.subscriptions.order_by('-end_date').first()


def is_membership_blocked(user):
    """True when the member's last subscription ended more than GRACE_DAYS ago."""
    if not user.is_authenticated or user.is_staff or user.is_superuser:
        return False
    latest = latest_subscription(user)
    if latest is None:
        return False
    return latest.end_date + timedelta(days=GRACE_DAYS) < timezone.localdate()


def mark_for_renewal(request, user):
    """Called after the password was verified but the membership is blocked.
    Remembers who it was for a few minutes so the Renew button can continue,
    without logging them in."""
    request.session['renew_user_id'] = user.pk
    request.session['renew_started_at'] = timezone.now().timestamp()


def pop_renewal_user(request):
    """Returns the user waiting to renew (and clears the marker), or None."""
    user_id = request.session.pop('renew_user_id', None)
    started = request.session.pop('renew_started_at', None)
    if not user_id or not started:
        return None
    if timezone.now().timestamp() - started > RENEWAL_WINDOW_SECONDS:
        return None
    return get_user_model().objects.filter(pk=user_id, is_active=True).first()