from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_profile_complete', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone


class OTPSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'created_at']),
            models.Index(fields=['session_id']),
        ]
        
    def is_valid(self):
        # OTP valid for 5 minutes
        return self.created_at >= timezone.now() - timedelta(minutes=5)
    
    def can_retry(self):
        """Allow a retry only if the last attempt was more than 60 seconds ago."""
        if self.attempts >= 3: # Max 3 tries per session
            return False
        return True
    
    def __str__(self):
        return f"{self.phone} - {self.otp_code}"