from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db import transaction
from .serializers import SendOTPSerializer,VerifyOTPSerializer, RegistrationSerializer, UserSerializer
from .services import send_otp_to_phone
from .models import OTPSession, User
from .permissions import IsRegistrationTokenAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status, permissions
class SendOTPView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_send'
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            session_id = send_otp_to_phone(phone)
            
            return Response({
                "session_id": session_id,
                "message": "OTP sent successfully"
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    throttle_scope = 'otp_verify'
    def post(self, request):
        
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        session_id = serializer.validated_data['session_id']
        otp_code = serializer.validated_data['otp_code']
        
        # 1. Fetch and Validate Session
        session = get_object_or_404(OTPSession, session_id=session_id)

        if session.attempts >= 3:
            return Response({"error": "Too many failed attempts. Request a new code."}, 
                    status=status.HTTP_403_FORBIDDEN)

        if session.otp_code != otp_code:
            session.attempts += 1
            session.save()
            return Response({"error": f"Invalid OTP. {3 - session.attempts} attempts remaining."}, 
                    status=status.HTTP_400_BAD_REQUEST)
        
        if not session.is_valid():
            return Response({"error": "OTP Expired"}, status=status.HTTP_400_BAD_REQUEST)
            
        if session.otp_code != otp_code:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Branching Logic
        phone = session.phone
        user_exists = User.objects.filter(phone=phone).exists()
        
        if user_exists:
            user = User.objects.get(phone=phone)
            # Standard SimpleJWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "LOGIN",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_profile_complete": user.is_profile_complete
            }, status=status.HTTP_200_OK)
        else:
            # New User: Generate a temporary "Registration Token"
            # We add the phone to the payload so the next endpoint knows who to register
            temp_token = RefreshToken()
            temp_token['phone'] = phone
            temp_token['purpose'] = 'registration'
            
            # Mark session as verified so it can't be reused for other phones
            session.is_verified = True
            session.save()
            
            return Response({
                "status": "SIGNUP",
                "registration_token": str(temp_token.access_token),
                "message": "Phone verified. Please complete registration."
            }, status=status.HTTP_200_OK)
    


class CompleteRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [IsRegistrationTokenAuthenticated]

    def post(self, request):
        # 1. Get the phone from the token
        auth = JWTAuthentication()
        header = auth.get_header(request)
        raw_token = auth.get_raw_token(header)
        validated_token = auth.get_validated_token(raw_token)
        phone = validated_token.get('phone')

        print(f"DEBUG: Registration attempt for phone {phone} with data: {request.data}")
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Registration validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # 2. Create the user
            user = User.objects.create_user(
                phone=phone,
                full_name=serializer.validated_data['full_name'],
                email=serializer.validated_data.get('email',''),
                city=serializer.validated_data['city'],
                address=serializer.validated_data['address'],
                is_profile_complete=True
            )

            # 3. Generate final production tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "status": "SUCCESS",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "phone": user.phone,
                    "full_name": user.full_name
                }
            }, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # DEBUG: Print this to your terminal to see what the backend receives
        print("LOGOUT DATA RECEIVED:", request.data) 
        
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        print(f"DEBUG: Returning profile for user {request.user.phone}: {serializer.data}")
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        # For a dummy view, we can deactivate the user instead of actual deletion
        user.is_active = False
        user.save()
        return Response({"message": "Account deactivated successfully."}, status=status.HTTP_204_NO_CONTENT)