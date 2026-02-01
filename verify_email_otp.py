import os
import django
from dotenv import load_dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
load_dotenv()
django.setup()

from accounts.services import send_otp_via_email

phone = '9872180369'
print(f"Testing Email OTP flow for {phone}...")

# Trigger the email-only flow
session_id = send_otp_via_email(phone)

print(f"\nFlow complete. Session ID: {session_id}")
print("Check the console output above for the OTP log or email results.")
