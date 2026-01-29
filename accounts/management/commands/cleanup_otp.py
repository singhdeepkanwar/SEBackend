from django.core.management.base import BaseCommand
from accounts.models import OTPSession
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes expired OTP sessions from the database'

    def handle(self, *args, **kwargs):
        # Delete anything older than 24 hours (or your preferred duration)
        count, _ = OTPSession.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=1)
        ).delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired sessions'))