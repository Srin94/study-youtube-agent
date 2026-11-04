"""Central configuration: env variables and pipeline constants.

Everything that tunes the pipeline lives here so the individual modules stay
declarative. Environment variables are loaded once via python-dotenv.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# agent-backend/src/config.py -> agent-backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent

DATA_DIR = BACKEND_DIR / "data"
OUTPUT_DIR = BACKEND_DIR / "output"
TEMPLATES_DIR = BACKEND_DIR / "templates"

VIDEO_ENGINE_DIR = REPO_ROOT / "video-engine"
VIDEO_ASSETS_DIR = VIDEO_ENGINE_DIR / "public" / "assets"

DB_PATH = DATA_DIR / "seen_topics.db"
CURRICULUM_PATH = DATA_DIR / "curriculum_syllabus.json"
RENDER_PAYLOAD_PATH = OUTPUT_DIR / "render_payload.json"
NARRATION_PATH = OUTPUT_DIR / "narration.wav"
THUMBNAIL_PATH = OUTPUT_DIR / "thumbnail.png"
FINAL_VIDEO_PATH = OUTPUT_DIR / "final_video.mp4"
THUMBNAIL_TEMPLATE_PATH = TEMPLATES_DIR / "thumbnail_template.html"

for _d in (DATA_DIR, OUTPUT_DIR, VIDEO_ASSETS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

load_dotenv(REPO_ROOT / ".env")
load_dotenv(BACKEND_DIR / ".env")

# ---------------------------------------------------------------------------
# Secrets / credentials
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

APPROVAL_WINDOW_MINUTES = int(
    os.getenv("APPROVAL_WINDOW_MINUTES", os.getenv("AUTO_APPROVE_MINUTES", "30")) or "30"
)
AUTO_APPROVE_MINUTES = APPROVAL_WINDOW_MINUTES

# Fail-closed by default: no explicit "Approve" within the window => do NOT publish.
APPROVE_ON_TIMEOUT = os.getenv("APPROVE_ON_TIMEOUT", "false").lower() in ("1", "true", "yes")

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "").strip()
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "").strip()
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "").strip()

DRY_RUN_SKIP_UPLOAD = os.getenv("DRY_RUN_SKIP_UPLOAD", "false").lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
# NOTE: gemini-2.5-flash (named in the spec) is retired for new API keys; the
# live API directs new users to gemini-3.8-flash. Override via GEMINI_MODEL.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# ---------------------------------------------------------------------------
# Curriculum tracks (strict round-robin rotation order; requirement 2.1)
# ---------------------------------------------------------------------------
TRACKS = [
    "EVERYDAY_ALGORITHMS",
    "GAME_THEORY_PARADOXES",
    "MONEY_AND_MARKETS",
    "HARDWARE_AND_PHYSICS",
    "CRYPTO_AND_SECURITY",
    "CS_AND_AI_INTERNALS",
]

# Track -> default theme id (requirement 5.3).
TRACK_THEME = {
    "EVERYDAY_ALGORITHMS": "ARCHIVAL_LAB_PAPER",
    "GAME_THEORY_PARADOXES": "ARCHIVAL_LAB_PAPER",
    "MONEY_AND_MARKETS": "ARCHIVAL_LAB_PAPER",
    "HARDWARE_AND_PHYSICS": "QUANTUM_SIM_HUD",
    "CRYPTO_AND_SECURITY": "QUANTUM_SIM_HUD",
    "CS_AND_AI_INTERNALS": "QUANTUM_SIM_HUD",
}

# A browser-like UA so Wikipedia / Jina / news endpoints don't 429 us.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36 study-youtube-agent/1.0"
)

# ---------------------------------------------------------------------------
# Reference gathering (Jina Reader over Wikipedia + optional secondary)
# ---------------------------------------------------------------------------
JINA_READER_PREFIX = "https://r.jina.ai/"
JINA_TIMEOUT_SECONDS = 25
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/{slug}"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}"
MIN_ARTICLE_CHARS = 400
MAX_ARTICLE_CHARS = 18_000
TITLE_SIMILARITY_THRESHOLD = 0.80

# ---------------------------------------------------------------------------
# Audio / TTS
# ---------------------------------------------------------------------------
KOKORO_VOICE = os.getenv("KOKORO_VOICE", "am_michael")
KOKORO_SPEED = float(os.getenv("KOKORO_SPEED", "1.0"))
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AndrewMultilingualNeural")
EDGE_TTS_FALLBACK_VOICES = ["en-US-GuyNeural", "en-US-ChristopherNeural"]
EDGE_TTS_RATE = os.getenv("EDGE_TTS_RATE", "-3%")
SCENE_GAP_MS = 340
AUDIO_SAMPLE_RATE = 24_000
WHISPER_MODEL = "base.en"
WHISPER_COMPUTE_TYPE = "int8"

# ---------------------------------------------------------------------------
# Background music (procedurally generated bed mixed under narration)
# ---------------------------------------------------------------------------
BACKGROUND_MUSIC_ENABLED = os.getenv("BACKGROUND_MUSIC_ENABLED", "true").lower() in ("1", "true", "yes")
MUSIC_DIR = BACKEND_DIR / "assets" / "music"
MUSIC_LEVEL_DBFS = float(os.getenv("MUSIC_LEVEL_DBFS", "-30"))
MUSIC_FADE_MS = int(os.getenv("MUSIC_FADE_MS", "2500"))

# ---------------------------------------------------------------------------
# Thumbnail (text-vs-text contrast card; no icon slugs)
# ---------------------------------------------------------------------------
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 60
REMOTION_COMPOSITION_ID = "StudyMasterVideo"

# On-screen channel brand (wordmark + outro CTA + thumbnail).
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "First Principles")

# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------
YOUTUBE_CATEGORY_ID = "27"  # Education
YOUTUBE_UPLOAD_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def require_gemini() -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to .env or the environment "
            "(see .env.example)."
        )
    return GEMINI_API_KEY


def has_telegram() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def has_youtube_credentials() -> bool:
    return bool(YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN)
