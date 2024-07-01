from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http.request import HttpRequest
from rest_framework.request import Request
from django.utils.translation import gettext_lazy as _
from django.db.models import Q



User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'password2', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            address=validated_data.get('address', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'metadata')


class JwtTokenObtainPair(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": _("Incorrect login credentials.")}

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["roles"] = list(user.groups.values_list("name", flat=True))
        # ...

        return token

    def validate(self, attrs):
        request: HttpRequest or Request = self.context.get("request")  # noqa
        credentials = {"email": attrs.get("email"), "password": attrs.get("password")}

        user_obj = User.objects.filter(Q(email=str(attrs.get("email")).lower())).first()

        res = super().validate(credentials)
        # attach user to the serializer
        user_data = UserLoginSerializer(user_obj, context=self.context).data

        return {
            **user_data,
            **res,
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'username', 'address', 'metadata')
