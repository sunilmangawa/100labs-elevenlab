from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Project, Voice


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ["slug", "name", "description", "accent", "gender", "sample_color", "provider_voice_id", "category", "labels", "preview_url"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "script", "voice", "language", "model", "style", "controls", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_script(self, value):
        if len(value) > 5000:
            raise serializers.ValidationError("Scripts are limited to 5,000 characters.")
        return value


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


class GenerateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)
    voice = serializers.CharField(max_length=80, default="Ava")
    model = serializers.CharField(max_length=80, default="Sonora Natural")
    controls = serializers.DictField(required=False, default=dict)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Text is required.")
        return value
