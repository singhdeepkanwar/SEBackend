import random
import os
import requests
from .models import OTPSession
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(1000, 9999))

def _send_otp_email_logic(otp):
    """
    Internal logic to send OTP to a fixed test email address.
    """
    test_email = os.getenv('TEST_OTP_EMAIL')
    if not test_email:
        print("WARNING: TEST_OTP_EMAIL not configured. Falling back to console log.")
        return False

    subject = "Dynamic OTP Verification"
    message = f"Your OTP for verification is: {otp}. It is valid for 5 minutes."
    from_email = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@sangrurestate.com')

    try:
        send_mail(subject, message, from_email, [test_email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Email Exception: {e}")
        return False

def send_otp_via_email(phone):
    """
    High-level service for SendOTPView that creates a session and sends OTP via email.
    """
    otp = generate_otp()
    session = OTPSession.objects.create(
        phone=phone,
        otp_code=otp
    )
    _send_otp_email_logic(otp)
    return session.session_id

def send_otp_via_twilio(phone, otp):
    """
    Sends OTP via Twilio SMS.
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')

    if not account_sid or not auth_token or not from_number:
        print("WARNING: Twilio credentials not configured. Skipping SMS.")
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    # Ensure phone number is in E.164 format (e.g., +91XXXXXXXXXX)
    clean_phone = phone.strip()
    if not clean_phone.startswith('+'):
        if len(clean_phone) == 10:
            clean_phone = f"+91{clean_phone}"
        else:
            clean_phone = f"+{clean_phone}"

    payload = {
        "To": clean_phone,
        "From": from_number,
        "Body": f"Your Sangrur Estate verification code is: {otp}. Valid for 5 minutes."
    }

    try:
        response = requests.post(url, data=payload, auth=(account_sid, auth_token), timeout=10)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Twilio API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Twilio Exception: {e}")
        return False

def send_otp_to_phone(phone):
    """
    Primary OTP delivery service. Generates code, creates session,
    and delivers via Twilio SMS (with optional test-email logging).
    """
    try:
        # Rate limiting: 60 seconds between requests
        one_minute_ago = timezone.now() - timedelta(seconds=60)
        recent_session = OTPSession.objects.filter(
            phone=phone, 
            created_at__gte=one_minute_ago
        ).first()
        if recent_session:
            raise ValidationError("Please wait 60 seconds before requesting a new code.")
    except ValidationError:
        raise
    except Exception as e:
        print(f"Session Check Error: {e}")
    
    otp = generate_otp()
    session = OTPSession.objects.create(
        phone=phone,
        otp_code=otp
    )
    
    # Try Twilio delivery
    twilio_success = send_otp_via_twilio(phone, otp)
    
    # Fallback/Parallel delivery to test email if configured
    email_success = False
    # email_success = _send_otp_email_logic(otp)
    
    # Log for local development if Twilio fails or DEBUG is on
    if not twilio_success or os.getenv('DEBUG', 'False') == 'True':
        print(f"\n--- OTP DELIVERY LOG ---")
        print(f"PHONE: {phone}")
        print(f"CODE: {otp}")
        print(f"TWILIO: {'SUCCESS' if twilio_success else 'FAILED'}")
        print(f"EMAIL: {'SUCCESS' if email_success else 'SKIPPED/FAILED'}")
        print(f"SESSION_ID: {session.session_id}")
        print("--------------------------\n")
    
    return session.session_id