import uuid

from django.conf import settings
from django.db import models


class Voice(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=160)
    accent = models.CharField(max_length=80, default="English (US)")
    gender = models.CharField(max_length=40, default="Neutral")
    sample_color = models.CharField(max_length=30, default="#aa8cff")
    provider_voice_id = models.CharField(max_length=120, blank=True, help_text="Voice ID used by the configured speech provider.")
    category = models.CharField(max_length=80, default="premade", blank=True)
    labels = models.JSONField(default=dict, blank=True)
    preview_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Language(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=80)
    native_name = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class TTSModel(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    provider_model_id = models.CharField(max_length=120, blank=True)
    description = models.CharField(max_length=180, blank=True)
    languages = models.JSONField(default=list, blank=True, help_text="Language codes supported by this model.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DeliveryStyle(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="voice_projects")
    name = models.CharField(max_length=120, default="Untitled project")
    script = models.TextField(blank=True)
    voice = models.CharField(max_length=80, default="Ava")
    language = models.CharField(max_length=80, default="English (US)")
    model = models.CharField(max_length=80, default="Sonora Natural")
    style = models.CharField(max_length=80, default="Conversational")
    controls = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
