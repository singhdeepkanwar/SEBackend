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

def send_otp_via_whatsapp(phone, otp):
    """
    Sends OTP via Meta WhatsApp Cloud API.
    """
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    template_name = os.getenv('WHATSAPP_OTP_TEMPLATE_ID', 'otp_verification')

    if not access_token or not phone_number_id:
        print("WARNING: WhatsApp credentials not configured. Skipping WhatsApp.")
        return False

    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Ensure phone number is in E.164 format (e.g., 91XXXXXXXXXX)
    # Simple cleanup for Indian numbers if they don't have code
    clean_phone = phone.strip()
    if len(clean_phone) == 10:
        clean_phone = f"91{clean_phone}"
    elif clean_phone.startswith('+'):
        clean_phone = clean_phone[1:]

    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": otp}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {"type": "text", "text": otp}
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"WhatsApp API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"WhatsApp Exception: {e}")
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
    
    # Try WhatsApp first
    whatsapp_success = send_otp_via_whatsapp(phone, otp)
    
    # Rerouted Delivery to Email (Fallback/Dev)
    email_success = send_otp_via_email(otp)
    
    # Fallback to console for development/debugging if both fail or is DEBUG
    if (not whatsapp_success and not email_success) or os.getenv('DEBUG', 'False') == 'True':
        print(f"\n--- OTP LOG ---")
        print(f"FOR PHONE: {phone}")
        print(f"WHATSAPP SUCCESS: {whatsapp_success}")
        print(f"EMAIL SUCCESS: {email_success}")
        print(f"CODE: {otp}")
        print(f"SESSION_ID: {session.session_id}")
        print("---------------------------\n")
    
    return session.session_id