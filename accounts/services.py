import random
import requests
import os
from .models import OTPSession
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_via_msg91(phone, otp):
    """
    Sends OTP using MSG91 API.
    """
    auth_key = os.getenv('MSG91_AUTH_KEY')
    template_id = os.getenv('MSG91_OTP_TEMPLATE_ID')
    
    if not auth_key or not template_id:
        print("WARNING: MSG91 credentials missing. Falling back to console log.")
        return False

    url = "https://control.msg91.com/api/v5/otp"
    
    # Remove any non-digit characters from phone
    clean_phone = ''.join(filter(str.isdigit, phone))
    # Ensure it has country code (default to 91 if 10 digits)
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    payload = {
        "template_id": template_id,
        "mobile": clean_phone,
        "authkey": auth_key,
        "otp": otp
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_data = response.json()
        if res_data.get("type") == "success":
            return True
        else:
            print(f"MSG91 Error: {res_data}")
            return False
    except Exception as e:
        print(f"MSG91 Exception: {e}")
        return False

def send_otp_to_phone(phone):
    try:
        one_minute_ago = timezone.now() - timedelta(seconds=60)
        recent_session = OTPSession.objects.filter(
            phone=phone, 
            created_at__gte=one_minute_ago
        ).first()
        if recent_session:
            raise ValidationError("Please wait 60 seconds before requesting a new code.")
    except ValidationError:
        raise
    except:
        pass
    
    otp = generate_otp()
    session = OTPSession.objects.create(
        phone=phone,
        otp_code=otp
    )
    
    # Live Integration
    success = send_otp_via_msg91(phone, otp)
    
    # Fallback to console for development/debugging if MSG91 fails or is not configured
    if not success or os.getenv('DEBUG', 'False') == 'True':
        print(f"\n--- SMS LOG (Success: {success}) ---")
        print(f"TO: {phone}")
        print(f"CODE: {otp}")
        print(f"SESSION_ID: {session.session_id}")
        print("---------------------------\n")
    
    return session.session_id