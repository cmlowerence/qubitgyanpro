# qubitgyanpro/apps/core/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.base_user import BaseUserManager

from apps.core.models import User
from apps.core.selectors import get_user_by_email
from apps.core.constants import UserStatus


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'role',
            'status',
            'is_verified',
            'is_onboarded'
        ]


class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = BaseUserManager().normalize_email(attrs.get('email', '').strip())
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Invalid credentials.")

        user = get_user_by_email(email)

        if not user or user.is_deleted:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active or user.status != UserStatus.ACTIVE:
            raise serializers.ValidationError("Account is inactive.")

        if user.is_account_locked():
            raise serializers.ValidationError("Account is locked. Try again later.")

        attrs['user'] = user
        attrs['email'] = email
        return attrs


class RequestResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return BaseUserManager().normalize_email(value.strip())


class VerifyResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    def validate_email(self, value):
        return BaseUserManager().normalize_email(value.strip())

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Invalid OTP.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value