from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsRegistrationTokenAuthenticated(BasePermission):
    """
    Allows access only to users with a valid registration_token.
    """
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        try:
            # Manually authenticate the token from the header
            header = auth.get_header(request)
            if header is None:
                print("DEBUG: Registration attempt missing Authorization header")
                return False
            
            raw_token = auth.get_raw_token(header)
            validated_token = auth.get_validated_token(raw_token)
            
            # Check for our custom claim
            purpose = validated_token.get('purpose')
            print(f"DEBUG: Token purpose: {purpose}")
            return purpose == 'registration'
        except Exception as e:
            print(f"DEBUG: Registration token validation failed: {str(e)}")
            return False