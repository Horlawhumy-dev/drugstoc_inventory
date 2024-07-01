# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import BlacklistedAccessToken

class CustomJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # Extract the header from the request
        header = self.get_header(request)
        if header is None:
            return None

        # Extract the raw token from the header
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Check if the raw token is blacklisted
        is_token_blacklisted = BlacklistedAccessToken.objects.filter(token=raw_token).exists()
        if is_token_blacklisted:
            raise InvalidToken('You are logged out!')

        # Validate the token
        validated_token = self.get_validated_token(raw_token)

        # Return the user and validated token
        return self.get_user(validated_token), validated_token

    def get_header(self, request):
        """
        Extracts the header containing the token from the request.
        """
        return request.META.get('HTTP_AUTHORIZATION')

    def get_raw_token(self, header):
        """
        Extracts the raw token from the header.
        """
        parts = header.split()
        if len(parts) == 0 or parts[0] != 'Bearer':
            return None
        if len(parts) != 2:
            return None
        return parts[1]
