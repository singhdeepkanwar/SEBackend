import os
import django
from dotenv import load_dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
load_dotenv()
django.setup()

from accounts.services import send_otp_to_phone

phone = '9872180369'
print(f"Testing WhatsApp OTP flow for {phone}...")
print("Note: This will log to console if WhatsApp/Email credentials are not set or if DEBUG is True.")

# Trigger the flow
session_id = send_otp_to_phone(phone)

print(f"\nFlow complete. Session ID: {session_id}")
print("Check the console output above for the OTP log or API results.")
