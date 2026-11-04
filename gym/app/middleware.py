"""
Place at: app/middleware.py
Register in settings.MIDDLEWARE AFTER AuthenticationMiddleware and MessageMiddleware.
"""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

from .membership import is_membership_blocked

# ---- EDIT HERE ------------------------------------------------------------
# URL names a blocked member may still open. Must include every page of the
# renewal and payment flow (package list, start payment, eSewa success AND
# failure return URLs), otherwise the payment cannot complete.
ALLOWED_URL_NAMES = {
    'membership',
    'logout',
    'download_receipt',
    'esewa_initiate',    # Pay with eSewa button
    'esewa_success',     # eSewa return URL after payment
    'esewa_failure',     # eSewa return URL after cancel/failure
}
RENEW_REDIRECT = 'membership'
# ---------------------------------------------------------------------------


class MembershipLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and is_membership_blocked(user):
            path = request.path_info
            static_prefixes = tuple(
                p for p in (getattr(settings, 'STATIC_URL', ''), getattr(settings, 'MEDIA_URL', '')) if p
            )
            if not (static_prefixes and path.startswith(static_prefixes)):
                try:
                    url_name = resolve(path).url_name
                except Resolver404:
                    url_name = None

                if url_name not in ALLOWED_URL_NAMES:
                    messages.warning(
                        request,
                        "Your membership has expired. Please renew to regain access."
                    )
                    return redirect(RENEW_REDIRECT)

        return self.get_response(request)