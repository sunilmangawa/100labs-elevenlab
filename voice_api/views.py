from django.contrib.auth import login, logout
import json
import os
import urllib.error
import urllib.request

from django.db import IntegrityError
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeliveryStyle, Language, Project, TTSModel, Voice
from .serializers import GenerateSerializer, LoginSerializer, ProjectSerializer, RegisterSerializer, VoiceSerializer


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "sonora-api"})


class VoiceListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VoiceSerializer
    queryset = Voice.objects.filter(is_active=True)


class CatalogView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "voices": VoiceSerializer(Voice.objects.filter(is_active=True), many=True).data,
            "languages": list(Language.objects.filter(is_active=True).values("code", "name", "native_name")),
            "models": list(TTSModel.objects.filter(is_active=True).values("slug", "name", "provider_model_id", "description", "languages")),
            "styles": list(DeliveryStyle.objects.filter(is_active=True).values("slug", "name", "description")),
        })


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"detail": "That username is already in use."}, status=status.HTTP_409_CONFLICT)
        login(request, user)
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"id": user.id, "username": user.username})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username, "email": request.user.email})


class GenerateView(APIView):
    """Proxy text-to-speech requests without exposing the provider key to browsers."""

    def post(self, request):
        serializer = GenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            return Response({"detail": "Set ELEVENLABS_API_KEY on the server to enable cloud generation."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        values = serializer.validated_data
        voice_key = values["voice"].upper().replace(" ", "_")
        selected_voice = Voice.objects.filter(name=values["voice"], is_active=True).first()
        voice_id = (selected_voice.provider_voice_id if selected_voice else "") or os.environ.get(f"SONORA_{voice_key}_VOICE_ID") or os.environ.get("ELEVENLABS_DEFAULT_VOICE_ID")
        if not voice_id:
            return Response({"detail": f"No provider voice ID configured for {values['voice']}."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        selected_model = TTSModel.objects.filter(name=values["model"], is_active=True).first()
        model_map = {"Sonora Express": "eleven_flash_v2_5", "Sonora Studio": "eleven_multilingual_v2", "Sonora Natural": "eleven_v3"}
        controls = values.get("controls") or {}
        payload = {
            "text": values["text"],
            "model_id": (selected_model.provider_model_id if selected_model and selected_model.provider_model_id else model_map.get(values["model"], "eleven_multilingual_v2")),
            "voice_settings": {
                "stability": max(0, min(1, float(controls.get("stability", 62)) / 100)),
                "similarity_boost": max(0, min(1, float(controls.get("clarity", 78)) / 100)),
                "style": max(0, min(1, float(controls.get("expressiveness", 44)) / 100)),
                "use_speaker_boost": True,
            },
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
        request_body = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "xi-api-key": api_key}, method="POST")
        try:
            with urllib.request.urlopen(request_body, timeout=60) as upstream:
                audio = upstream.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            return Response({"detail": "Voice provider rejected the request.", "provider_error": detail}, status=status.HTTP_502_BAD_GATEWAY)
        except urllib.error.URLError:
            return Response({"detail": "Voice provider could not be reached."}, status=status.HTTP_502_BAD_GATEWAY)

        response = HttpResponse(audio, content_type="audio/mpeg")
        response["Content-Disposition"] = "inline; filename=sonora-preview.mp3"
        return response
