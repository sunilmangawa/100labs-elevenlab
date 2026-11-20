from django.urls import path

from .views import CatalogView, GenerateView, HealthView, LoginView, LogoutView, MeView, ProjectDetailView, ProjectListCreateView, RegisterView, VoiceListView

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("voices/", VoiceListView.as_view()),
    path("catalog/", CatalogView.as_view()),
    path("generate/", GenerateView.as_view()),
    path("projects/", ProjectListCreateView.as_view()),
    path("projects/<uuid:pk>/", ProjectDetailView.as_view()),
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
]
