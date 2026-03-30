# qubitgyanpro\apps\admission\serializers.py

from rest_framework import serializers
from django.contrib.auth.base_user import BaseUserManager

from apps.admission.models import Admission, AdmissionStatus


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = [
            'id',
            'email',
            'full_name',
            'phone_number',
            'telegram_user_id',
            'telegram_username',
            'telegram_verified',
            'target_exam',
            'preferred_language',
            'status',
            'source',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'status',
            'source',
            'created_at',
            'updated_at'
        ]


class CreateAdmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    telegram_user_id = serializers.CharField(max_length=100)
    telegram_username = serializers.CharField(required=False, allow_blank=True)

    target_exam = serializers.CharField(required=False, allow_blank=True)
    preferred_language = serializers.CharField(required=False, default="English")

    def validate_email(self, value):
        return BaseUserManager().normalize_email(value.strip())

    def validate(self, attrs):
        email = attrs.get("email")
        telegram_user_id = attrs.get("telegram_user_id")

        if Admission.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Admission already exists for this email."})

        if Admission.objects.filter(telegram_user_id=telegram_user_id).exists():
            raise serializers.ValidationError({"telegram_user_id": "Admission already exists for this Telegram account."})

        return attrs


class ReviewAdmissionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject", "under_review"])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        action = attrs.get("action")
        reason = attrs.get("rejection_reason")

        if action == "reject" and not reason:
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required."})

        return attrs
    
    