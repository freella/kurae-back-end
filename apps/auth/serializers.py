from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator

from apps.core.validators import validar_nome, validar_senha


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Este email já está em uso."
            )
        ]
    )
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate_first_name(self, value):
        validar_nome(value)
        return value

    def validate_last_name(self, value):
        validar_nome(value)
        return value

    def validate_password(self, value):
        validar_senha(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"non_field_errors": ["As senhas não coincidem."]}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        validated_data["password"] = make_password(validated_data["password"])
        return User.objects.create_user(**validated_data)


class PasswordResetRequestSerializer(serializers.Serializer):

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validar_senha(value)
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"non_field_errors": ["As senhas não coincidem."]}
            )
        return attrs
