from django.core.management.base import BaseCommand

from voice_api.models import DeliveryStyle, Language, TTSModel, Voice


VOICE_DATA = [
    ("ava", "Ava", "Warm and conversational", "English (US)", "Female", "#f2aa91", "premade"),
    ("theo", "Theo", "Clear and confident", "English (US)", "Male", "#8db7ef", "premade"),
    ("mira", "Mira", "Bright and energetic", "English (UK)", "Female", "#7dd3b2", "premade"),
    ("sam", "Sam", "Calm and grounded", "English (US)", "Neutral", "#c2a5f4", "premade"),
    ("aria", "Aria", "Expressive audiobook narrator", "English (US)", "Female", "#f0b8d2", "premade"),
    ("atlas", "Atlas", "Deep documentary narrator", "English (US)", "Male", "#9aa9e8", "premade"),
    ("luna", "Luna", "Soft and reassuring", "Spanish", "Female", "#d7b1f3", "premade"),
    ("nora", "Nora", "Friendly and clear", "German", "Female", "#f3c188", "premade"),
    ("leo", "Leo", "Upbeat social narrator", "English (US)", "Male", "#8cced5", "premade"),
    ("elena", "Elena", "Warm Latin American voice", "Spanish", "Female", "#e9a68c", "premade"),
    ("henrik", "Henrik", "Measured Nordic tone", "Swedish", "Male", "#88b9dc", "premade"),
    ("claire", "Claire", "Elegant French delivery", "French", "Female", "#c6a4ea", "premade"),
    ("ravi", "Ravi", "Natural Indian English", "English (IN)", "Male", "#e8b476", "premade"),
    ("sora", "Sora", "Bright Japanese narration", "Japanese", "Female", "#9bcfc4", "premade"),
    ("noah", "Noah", "Grounded conversational voice", "English (UK)", "Male", "#a8b3e7", "premade"),
    ("ivy", "Ivy", "Young and lively", "English (US)", "Female", "#d4e38b", "premade"),
]

LANGUAGES = [
    ("en-US", "English (US)", "English (US)"), ("en-GB", "English (UK)", "English (UK)"),
    ("en-IN", "English (India)", "English (India)"), ("es", "Spanish", "Español"),
    ("fr", "French", "Français"), ("de", "German", "Deutsch"), ("it", "Italian", "Italiano"),
    ("pt-BR", "Portuguese (Brazil)", "Português (Brasil)"), ("pl", "Polish", "Polski"),
    ("hi", "Hindi", "हिन्दी"), ("ar", "Arabic", "العربية"), ("zh", "Chinese", "中文"),
    ("ko", "Korean", "한국어"), ("ja", "Japanese", "日本語"), ("ru", "Russian", "Русский"),
    ("nl", "Dutch", "Nederlands"), ("tr", "Turkish", "Türkçe"), ("sv", "Swedish", "Svenska"),
    ("da", "Danish", "Dansk"), ("fi", "Finnish", "Suomi"), ("uk", "Ukrainian", "Українська"),
    ("cs", "Czech", "Čeština"), ("ro", "Romanian", "Română"), ("el", "Greek", "Ελληνικά"),
]

MODEL_DATA = [
    ("sonora-natural", "Sonora Natural", "eleven_v3", "Most expressive and natural delivery", ["en-US", "en-GB", "es", "fr", "de", "it", "pt-BR", "ja", "ko", "hi"]),
    ("sonora-studio", "Sonora Studio", "eleven_multilingual_v2", "Consistent multilingual production voice", [code for code, _, _ in LANGUAGES]),
    ("sonora-express", "Sonora Express", "eleven_flash_v2_5", "Low-latency voice for conversations", [code for code, _, _ in LANGUAGES]),
    ("sonora-turbo", "Sonora Turbo", "eleven_turbo_v2_5", "Fast high-quality narration", [code for code, _, _ in LANGUAGES]),
    ("sonora-standard", "Sonora Standard", "eleven_monolingual_v1", "Simple English voice generation", ["en-US", "en-GB"]),
]

STYLE_DATA = [
    ("conversational", "Conversational", "Natural, relaxed and human."),
    ("narrative", "Narrative", "Structured storytelling with clear pacing."),
    ("energetic", "Energetic", "Bright, upbeat and attention-grabbing."),
    ("calm", "Calm", "Gentle, measured and reassuring."),
    ("authoritative", "Authoritative", "Confident and direct."),
    ("warm", "Warm", "Friendly, intimate and welcoming."),
    ("dramatic", "Dramatic", "Expressive with stronger emotional movement."),
    ("whisper", "Whisper", "Soft and close-mic delivery."),
]


class Command(BaseCommand):
    help = "Seed Sonora's starter voice catalog."

    def handle(self, *args, **options):
        for slug, name, description, accent, gender, color, category in VOICE_DATA:
            Voice.objects.update_or_create(slug=slug, defaults={"name": name, "description": description, "accent": accent, "gender": gender, "sample_color": color, "category": category})
        for code, name, native_name in LANGUAGES:
            Language.objects.update_or_create(code=code, defaults={"name": name, "native_name": native_name})
        for slug, name, provider_model_id, description, languages in MODEL_DATA:
            TTSModel.objects.update_or_create(slug=slug, defaults={"name": name, "provider_model_id": provider_model_id, "description": description, "languages": languages})
        for slug, name, description in STYLE_DATA:
            DeliveryStyle.objects.update_or_create(slug=slug, defaults={"name": name, "description": description})
        self.stdout.write(self.style.SUCCESS("Seeded voices, languages, models and delivery styles."))
