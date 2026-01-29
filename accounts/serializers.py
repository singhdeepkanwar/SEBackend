from rest_framework import serializers
from .models import User

class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    otp_code = serializers.CharField(max_length=6)

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'city','address']
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': False},
            'city': {'required': False},
            'address': {'required': False},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'email', 'city', 'address', 'is_profile_complete', 'date_joined']
        read_only_fields = ['id', 'phone', 'date_joined', 'is_profile_complete']