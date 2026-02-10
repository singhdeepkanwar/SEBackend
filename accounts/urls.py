from django.urls import path
from .views import (
    SendOTPView,
    VerifyOTPView,
    CompleteRegistrationView,
    LogoutView,
    UserProfileView,
    DeleteAccountView,
)


urlpatterns = [
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("register/", CompleteRegistrationView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]