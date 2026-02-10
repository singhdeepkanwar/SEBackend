import os
import logging
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class WhatsAppWebhookView(APIView):
    """
    Handle WhatsApp Cloud API webhooks.
    GET: Verification challenge from Meta.
    POST: Handling incoming messages/events.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Verification process for WhatsApp Cloud API.
        """
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')

        # Use the token from environment or fallback to 'check' as seen in user screenshot
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'check')

        if mode == 'subscribe' and token == verify_token:
            logger.info("WhatsApp webhook verified successfully.")
            return HttpResponse(challenge, status=200)
        
        logger.warning(f"WhatsApp webhook verification failed. Token mismatch: {token} != {verify_token}")
        return HttpResponse("Verification failed", status=403)

    def post(self, request):
        """
        Handle incoming messages and status updates.
        """
        data = request.data
        logger.info(f"WhatsApp Webhook received: {data}")
        
        # We will implement logic here later to handle incoming messages
        # For now, just acknowledge receipt
        return Response({"status": "received"}, status=status.HTTP_200_OK)
