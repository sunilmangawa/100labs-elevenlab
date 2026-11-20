from django.contrib import admin

from .models import DeliveryStyle, Language, Project, TTSModel, Voice


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = ("name", "accent", "gender", "category", "provider_voice_id", "is_active")
    list_filter = ("is_active", "gender", "category")
    search_fields = ("name", "description", "accent", "provider_voice_id")
    list_editable = ("is_active",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "native_name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "native_name", "code")
    list_editable = ("is_active",)


@admin.register(TTSModel)
class TTSModelAdmin(admin.ModelAdmin):
    list_display = ("name", "provider_model_id", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "provider_model_id")
    list_editable = ("is_active",)


@admin.register(DeliveryStyle)
class DeliveryStyleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    list_editable = ("is_active",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "voice", "model", "updated_at")
    list_filter = ("model", "style", "language")
    search_fields = ("name", "script", "user__username")
    readonly_fields = ("id", "created_at", "updated_at")
