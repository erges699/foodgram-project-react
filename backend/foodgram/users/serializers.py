from rest_framework import serializers

from .models import User
from .validators import username_validator


class UsernameValidationMixin():

    def validate_username(self, value):
        username_validator(value)
        return value


class SignUpSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )


class TokenSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User
