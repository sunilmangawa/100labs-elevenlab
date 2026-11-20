# Sonora Voice Studio

A focused voice studio inspired by the public ElevenLabs workflow: choose a voice, tune delivery, add refinement directions, preview, and save. It includes a Django REST API with per-user project ownership and a browser speech preview that works without an external API key.

For the complete beginner setup, admin, catalog, provider, and deployment instructions, read [Implementation.md](Implementation.md).

## Run it

From this folder:

```bash
python manage.py migrate
python manage.py seed_voices
python manage.py runserver
```

Open `http://127.0.0.1:8000`. The preview uses the browser Web Speech API, so available voices depend on the operating system and browser. Generated project settings can be exported as `sonora-project.json`.

The admin panel is available at `http://127.0.0.1:8000/admin/`.

## API

- `GET /api/health/`
- `GET /api/catalog/` (voices, languages, models, and delivery styles)
- `GET /api/voices/`
- `POST /api/generate/` (server-side ElevenLabs-compatible proxy; requires `ELEVENLABS_API_KEY` and a configured `ELEVENLABS_DEFAULT_VOICE_ID` or `SONORA_<VOICE>_VOICE_ID`)
- `POST /api/auth/register/` and `POST /api/auth/login/`
- `GET|POST /api/projects/`
- `GET|PATCH|DELETE /api/projects/<uuid>/`

The project API uses Django sessions and scopes projects to the authenticated user. The root page issues a CSRF cookie for same-origin API calls; the frontend keeps a local fallback until a user signs in.

For cloud audio, set the provider key only in the server environment. Never put it in frontend JavaScript:

```bash
set ELEVENLABS_API_KEY=your-key
set ELEVENLABS_DEFAULT_VOICE_ID=your-provider-voice-id
python manage.py runserver
```
"# 100labs-elevenlab" 
