from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class PhoneNumberTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        phone_number = request.headers.get('Authorization')  # Expecting phone number in the Authorization header
        access_token = request.headers.get('Access-Token')  # Expecting access token in a custom header

        if not phone_number or not access_token:
            return None  # No authentication provided

        try:
            user = User.objects.get(phone_number=phone_number)
            # Here you would validate the access token (e.g., check if it's valid, not expired, etc.)
            # This is a placeholder for actual validation logic
            if access_token != "expected_token":  # Replace with actual validation logic
                raise AuthenticationFailed('Invalid access token.')

            return (user, None)  # Return the user and None for the auth token
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.') 