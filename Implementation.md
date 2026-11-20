# Sonora Voice Studio — beginner implementation guide

This guide explains the project, local setup, administration, provider configuration, and deployment.

## 1. What was built

Sonora is a smaller original voice-studio application inspired by the public ElevenLabs workflow. It includes:

- Script editor with a 5,000-character limit.
- Voice library, languages, models, and delivery styles.
- Stability, clarity/similarity, expressiveness, and speed controls.
- Refinement directions for warm, thoughtful, confident, and custom delivery.
- Browser speech preview without an API key.
- Optional server-side AI audio generation.
- Local saving plus authenticated per-user project saving.
- Django admin management for users, voices, languages, models, styles, and projects.
- Provider catalog synchronization for importing real voice and model records.

The UI and code are an original implementation. It does not copy ElevenLabs private source code, private APIs, or protected assets.

## 2. REA investigation summary

REA browser capture was used against the public ElevenLabs website and its public Text to Speech route. The observed public workflow was:

1. The public page links to Text to Speech and Voice Library experiences.
2. Text to Speech is a separate route reached from the public page.
3. Public responses identify a Next.js-rendered site with React-style client bundles and utility-class CSS patterns.
4. The public product concepts include text-to-speech, voice selection, multilingual models, voice cloning, preview playback, and API access.

Sonora uses Django and Django REST Framework for the multi-user backend and plain HTML/CSS/JavaScript for the frontend. The browser Web Speech API is the no-key fallback; the server proxy keeps a provider API key out of browser code.

## 3. Project layout

```text
100labs/
├── index.html                 # Voice studio page
├── styles.css                 # Studio styling
├── app.js                     # Studio interactions and API calls
├── manage.py                  # Django command entry point
├── requirements.txt           # Python dependencies
├── db.sqlite3                 # Local development database
├── sonora/                    # Django project configuration
└── voice_api/                 # Catalog, projects, REST API, admin
```

Important backend files:

- `sonora/settings.py`: environment variables, database, static files, middleware.
- `sonora/urls.py`: home page, `/admin/`, and `/api/` routes.
- `voice_api/models.py`: Voice, Language, TTSModel, DeliveryStyle, and Project.
- `voice_api/admin.py`: Django admin registrations.
- `voice_api/management/commands/seed_voices.py`: offline starter catalog.
- `voice_api/management/commands/sync_catalog.py`: provider catalog import.

## 4. Windows setup

Open PowerShell and move into the project:

```powershell
cd C:\Users\coder\Documents\projects\100labs
python --version
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, run this once as your Windows user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Install the project packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create database tables and load the starter catalog:

```powershell
python manage.py migrate
python manage.py seed_voices
```

Start Django:

```powershell
python manage.py runserver
```

Open:

- Studio: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Catalog API: `http://127.0.0.1:8000/api/catalog/`
- Health check: `http://127.0.0.1:8000/api/health/`

## 5. Admin panel fix and usage

The admin problem was caused by two missing pieces: the URL route was absent, and application models were not registered. Both are now fixed.

Use the existing superuser account at:

```text
http://127.0.0.1:8000/admin/
```

Do not put the superuser password in documentation, source files, screenshots, or environment files.

The admin can manage:

- Users and permissions.
- Voices and provider voice IDs.
- Languages.
- Text-to-speech models.
- Delivery styles.
- Saved projects.

If `/admin/` fails, run:

```powershell
python manage.py check
python manage.py migrate
```

Then restart `runserver`.

## 6. Catalog and all provider voices

The database now contains a starter catalog of 16 voices, 24 languages, five model options, and eight delivery styles. The frontend calls `GET /api/catalog/` and fills its selectors from the database.

To import the current provider inventory, set the key only in the server terminal:

```powershell
$env:ELEVENLABS_API_KEY = "your-server-only-key"
python manage.py sync_catalog
```

The sync command imports provider voice IDs, names, labels, categories, preview URLs, model IDs, descriptions, and language metadata. It never sends the API key to the browser.

After syncing, refresh the studio page. You can also edit imported records in `/admin/`.

## 7. Enable real AI audio

Without provider configuration, Generate uses the browser's speech synthesis. To enable server-side MP3 generation:

```powershell
$env:ELEVENLABS_API_KEY = "your-server-only-key"
$env:ELEVENLABS_DEFAULT_VOICE_ID = "provider-voice-id"
python manage.py runserver
```

For a specific catalog voice:

```powershell
$env:SONORA_AVA_VOICE_ID = "provider-voice-id-for-ava"
```

The browser calls `POST /api/generate/`; Django calls the provider and returns audio. Never put provider credentials in `app.js` or `index.html`.

## 8. API overview

| Endpoint | Purpose |
|---|---|
| `GET /api/health/` | Backend health check |
| `GET /api/catalog/` | Voices, languages, models, and styles |
| `GET /api/voices/` | Active voices |
| `POST /api/generate/` | Server-side audio generation |
| `POST /api/auth/register/` | Create a user session |
| `POST /api/auth/login/` | Start a user session |
| `POST /api/auth/logout/` | End a session |
| `GET /api/auth/me/` | Current user |
| `GET|POST /api/projects/` | List or save the current user's projects |
| `GET|PATCH|DELETE /api/projects/<id>/` | Manage one owned project |

Project queries are filtered by `request.user`, so users do not receive each other's projects through these endpoints.

## 9. Production environment variables

Set these in the hosting provider's secret/environment-variable screen:

```text
DJANGO_SECRET_KEY=generate-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.example.com
CSRF_TRUSTED_ORIGINS=https://your-domain.example.com
ELEVENLABS_API_KEY=your-server-only-key
ELEVENLABS_DEFAULT_VOICE_ID=provider-voice-id
```

Do not use the development secret in production and do not commit a real `.env` file.

## 10. Deploy with Render

Render is a simple first hosting option.

1. Put the project in a GitHub repository.
2. Create a Render **Web Service** and connect the repository.
3. Use Python as the runtime.
4. Set the build command:

   ```text
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_voices && python manage.py collectstatic --noinput
   ```

5. Set the start command:

   ```text
   gunicorn sonora.wsgi:application
   ```

6. Add the production environment variables above.
7. Deploy and open the HTTPS URL.
8. Verify `https://your-domain.example.com/admin/`.

SQLite is fine for trying the app. For several users writing at the same time, use PostgreSQL. Configure the production database in `sonora/settings.py` using your host's database URL.

## 11. Deploy on another Linux server

```bash
git clone YOUR_REPOSITORY_URL
cd 100labs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_voices
python manage.py collectstatic --noinput
gunicorn sonora.wsgi:application --bind 127.0.0.1:8000
```

Put Nginx or another HTTPS reverse proxy in front of Gunicorn. Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to the real domain. Use PostgreSQL for multi-user production.

## 12. Common problems

**`/admin/` returns 404:** confirm `path("admin/", admin.site.urls)` is in `sonora/urls.py`, then restart Django.

**Admin login redirects repeatedly:** check cookies, `ALLOWED_HOSTS`, HTTPS, and `CSRF_TRUSTED_ORIGINS`.

**Generate uses a browser voice:** the provider key or voice ID is missing, invalid, or the provider rejected the request. Check the Django terminal output.

**New voices do not appear:** run `python manage.py seed_voices` or `python manage.py sync_catalog`, then refresh the page.

**CSS/JavaScript is missing in production:** run `python manage.py collectstatic --noinput`, verify WhiteNoise is installed, and restart Gunicorn.
