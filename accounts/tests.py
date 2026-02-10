from django.test import TestCase
from unittest.mock import patch
from accounts.services import send_otp_to_phone
from accounts.models import OTPSession

class TwilioOTPTests(TestCase):
    @patch('accounts.services.requests.post')
    def test_twilio_otp_trigger(self, mock_post):
        # Mock successful Twilio response
        mock_post.return_value.status_code = 201
        
        phone = "9872663031"
        session_id = send_otp_to_phone(phone)
        
        # Check session creation
        session = OTPSession.objects.get(session_id=session_id)
        self.assertEqual(session.phone, phone)
        self.assertFalse(session.is_verified)
        
        # Check Twilio API call
        self.assertTrue(mock_post.called)
        call_args = mock_post.call_args
        self.assertIn('twilio.com', call_args[0][0])
        
        # Verify clean phone logic (E.164)
        payload = call_args[1].get('data', {})
        self.assertEqual(payload.get('To'), f"+91{phone}")

class WhatsAppWebhookTests(TestCase):
    def test_webhook_verification_success(self):
        challenge = "CHALLENGE_ACCEPTED"
        url = "/api/auth/whatsapp/webhook/"
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "check",  # Default in view if ENV not set
            "hub.challenge": challenge
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), challenge)

    def test_webhook_verification_failure(self):
        url = "/api/auth/whatsapp/webhook/"
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "fail"
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 403)
