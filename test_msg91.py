import os
import django
from dotenv import load_dotenv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
load_dotenv()
django.setup()

from accounts.services import send_otp_via_msg91

phone = '9872180369'
otp = '4321'
print(f"Re-testing MSG91 API call for {phone}...")
success = send_otp_via_msg91(phone, otp)
print(f"MSG91 API CALL SUCCESS: {success}")
