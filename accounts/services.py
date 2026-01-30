import random
import os
from .models import OTPSession
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_via_email(otp):
    """
    Sends OTP to a fixed test email address for development/testing.
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
    
    # Rerouted Delivery to Email
    success = send_otp_via_email(otp)
    
    # Fallback to console for development/debugging if Email fails or is not configured
    if not success or os.getenv('DEBUG', 'False') == 'True':
        print(f"\n--- OTP LOG (Email Success: {success}) ---")
        print(f"FOR PHONE: {phone}")
        print(f"RE-ROUTED TO: {os.getenv('TEST_OTP_EMAIL', 'NOT CONFIGURED')}")
        print(f"CODE: {otp}")
        print(f"SESSION_ID: {session.session_id}")
        print("---------------------------\n")
    
    return session.session_id