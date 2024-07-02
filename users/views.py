
# views.py
import logging 
from datetime import datetime
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt import views as auth_views
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate, get_user_model, login
from django.db import transaction
from rest_framework.serializers import ValidationError

from .serializers import UserSerializer, UserRegistrationSerializer, JwtTokenObtainPair, UserSerializer
from .models import BlacklistedAccessToken
from .authentication import CustomJWTAuthentication
from .logs import log_user_logged_in_failure, log_user_logged_out, log_user_login_success

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(auth_views.TokenObtainPairView):
    permission_classes = []
    serializer_class = JwtTokenObtainPair

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            log_user_logged_in_failure(sender=request.data["email"], request=request)
            raise InvalidToken(e.args[0])
        except AuthenticationFailed as e:
            log_user_logged_in_failure(email=request.data["email"], request=request)
            raise ValidationError(dict(detail=e.args[0]))

        user = authenticate(
            request, username=request.data["email"], password=request.data["password"]
        )
        if user is not None:
            # If the user is authenticated, log them in using Django's login method
            # this is required to keep track of user logins activity
            login(request, user)
            log_user_login_success(request)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.user.email)
        except User.DoesNotExist as err:
            logging.debug(err)
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [CustomJWTAuthentication] #required to check accesstoken

    def post(self, request):
        
        with transaction.atomic():
            try:
                refresh_token = request.data["refresh_token"]
                access_token = request.auth

                # Blacklist the refresh token
                refresh_token_obj = RefreshToken(refresh_token)
                refresh_token_obj.blacklist()

                # Blacklist the access token
                BlacklistedAccessToken.objects.create(token=str(access_token), user=request.user)
                log_user_logged_out(request)
                return Response(status=status.HTTP_200_OK)
            except TokenError as e:
                return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
