"""
Place at: app/management/commands/send_expiry_reminders.py
(also create empty __init__.py files in app/management/ and app/management/commands/)

Usage:
    python manage.py send_expiry_reminders --dry-run   # show who would be emailed
    python manage.py send_expiry_reminders             # actually send

Sends at most two emails per membership period:
    - first reminder when 5 days or fewer are left (matches the online renewal rule)
    - final reminder when 1 day or fewer is left
"""
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Subscription, ExpiryReminder

# ---- EDIT HERE if your Subscription model uses different names ----
END_FIELD = 'end_date'        # DateField holding the membership expiry date
REMIND_WITHIN_DAYS = 5
# -------------------------------------------------------------------


class Command(BaseCommand):
    help = "Email members whose membership expires within the next few days."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="List the emails that would be sent without sending or logging anything.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.localdate()
        window_end = today + timedelta(days=REMIND_WITHIN_DAYS)

        subscriptions = Subscription.objects.select_related('user').filter(**{
            f'{END_FIELD}__gte': today,
            f'{END_FIELD}__lte': window_end,
        })

        sent = skipped = failed = 0

        for sub in subscriptions:
            user = sub.user
            expiry = getattr(sub, END_FIELD)

            # Skip: no email address or inactive account
            if not user.email or not user.is_active:
                skipped += 1
                continue

            # Skip: member already renewed (a later subscription exists)
            if Subscription.objects.filter(user=user, **{f'{END_FIELD}__gt': expiry}).exists():
                skipped += 1
                continue

            days_left = (expiry - today).days
            stage = 1 if days_left <= 1 else 5

            # Skip: this reminder was already sent for this expiry date
            if ExpiryReminder.objects.filter(subscription=sub, stage=stage, expiry_date=expiry).exists():
                skipped += 1
                continue

            subject, body = self.build_message(user, sub, expiry, days_left)

            if dry_run:
                self.stdout.write(f"[dry-run] would email {user.email} ({days_left} day(s) left, stage {stage})")
                sent += 1
                continue

            try:
                send_mail(
                    subject, body, settings.DEFAULT_FROM_EMAIL, [user.email],
                    fail_silently=False,
                )
                ExpiryReminder.objects.create(subscription=sub, stage=stage, expiry_date=expiry)
                sent += 1
            except Exception as exc:   # SMTP errors, bad address, etc.
                failed += 1
                self.stderr.write(f"Could not email {user.email}: {exc}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. sent={sent}, skipped={skipped}, failed={failed}"
        ))

    @staticmethod
    def build_message(user, sub, expiry, days_left):
        name = user.get_full_name() or user.username
        package = getattr(getattr(sub, 'package', None), 'name', None) or 'membership'
        site = getattr(settings, 'SITE_URL', '').rstrip('/')

        if days_left <= 0:
            when = "today"
            subject = "Your FitTrack membership expires today"
        elif days_left == 1:
            when = "tomorrow"
            subject = "Your FitTrack membership expires tomorrow"
        else:
            when = f"in {days_left} days"
            subject = f"Your FitTrack membership expires in {days_left} days"

        body = (
            f"Hi {name},\n\n"
            f"Your {package} at FitTrack expires {when} ({expiry:%d %b %Y}).\n\n"
            f"You can renew online from your account now, so your access is not interrupted. "
            f"After expiry there is a short grace period, then your account becomes inactive.\n\n"
            f"Log in to renew: {site}/\n\n"
            f"See you at the gym!\n"
            f"FitTrack Team"
        )
        return subject, body
