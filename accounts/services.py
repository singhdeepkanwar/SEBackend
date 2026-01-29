import random
from .models import OTPSession
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_to_phone(phone):
    try:
        one_minute_ago = timezone.now() - timedelta(seconds=60)
        recent_session = OTPSession.objects.filter(
            phone=phone, 
            created_at__gte=one_minute_ago
        ).first()
        if recent_session:
            raise ValidationError("Please wait 60 seconds before requesting a new code.")
    except:
        pass
    
    otp = generate_otp()
    session = OTPSession.objects.create(
        phone=phone,
        otp_code=otp
    )
    
    # LOGIC: Integrate Twilio/SMS Gateway here. 
    # For now, we print to console for development.
    print(f"\n--- SMS SENT TO {phone} ---")
    print(f"CODE: {otp}")
    print(f"SESSION_ID: {session.session_id}")
    print("---------------------------\n")
    
    return session.session_id