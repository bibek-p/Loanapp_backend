from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def validate_access_token(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        if not access_token:
            return Response({"error": "Access token is required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Here you would validate the access token
        # For example, check if it exists in the database or cache
        # This is a placeholder for actual validation logic
        if access_token != "expected_token":  # Replace with actual validation logic
            return Response({"error": "Invalid access token."}, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view 