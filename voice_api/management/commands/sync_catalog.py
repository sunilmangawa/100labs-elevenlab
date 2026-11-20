import json
import os
import urllib.request

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from voice_api.models import Language, TTSModel, Voice


class Command(BaseCommand):
    help = "Import the available voices and models from the configured ElevenLabs-compatible provider."

    def handle(self, *args, **options):
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise CommandError("Set ELEVENLABS_API_KEY before syncing the provider catalog.")
        voices = self.fetch("https://api.elevenlabs.io/v1/voices", api_key).get("voices", [])
        models = self.fetch("https://api.elevenlabs.io/v1/models", api_key)
        for item in voices:
            name = item.get("name") or item.get("voice_id")
            Voice.objects.update_or_create(
                provider_voice_id=item["voice_id"],
                defaults={
                    "slug": self.unique_slug(name, item["voice_id"]),
                    "name": name[:80],
                    "description": (item.get("description") or item.get("category") or "Provider voice")[:160],
                    "accent": (item.get("labels") or {}).get("accent", "Provider voice")[:80],
                    "gender": (item.get("labels") or {}).get("gender", "Unknown")[:40],
                    "category": (item.get("category") or "provider")[:80],
                    "labels": item.get("labels") or {},
                    "preview_url": item.get("preview_url") or "",
                    "is_active": True,
                },
            )
        for item in models:
            provider_id = item.get("model_id") or item.get("modelId")
            if not provider_id:
                continue
            supported_languages = item.get("languages") or []
            language_codes = []
            for language in supported_languages:
                if isinstance(language, dict):
                    code = language.get("language_id") or language.get("code") or language.get("language_code")
                    name = language.get("name") or language.get("language") or code
                else:
                    code = str(language)
                    name = code
                if code:
                    language_codes.append(code)
                    Language.objects.update_or_create(code=code[:20], defaults={"name": str(name)[:80], "native_name": str(name)[:80]})
            TTSModel.objects.update_or_create(
                provider_model_id=provider_id,
                defaults={
                    "slug": self.unique_slug(item.get("name") or provider_id, provider_id),
                    "name": (item.get("name") or provider_id)[:100],
                    "description": (item.get("description") or "Provider text-to-speech model")[:180],
                    "languages": language_codes,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Synced {len(voices)} voices and {len(models)} models."))

    @staticmethod
    def fetch(url, api_key):
        request = urllib.request.Request(url, headers={"xi-api-key": api_key, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())
        except Exception as error:
            raise CommandError(f"Could not fetch {url}: {error}") from error

    @staticmethod
    def unique_slug(name, provider_id):
        return f"{slugify(name)[:40]}-{slugify(provider_id)[:30]}".strip("-")
