import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_bundled_config = Path(__file__).parent.parent / "config.yaml"
_storage_dir = Path(os.getenv("STORAGE_DIR", "/storage"))
_storage_config = _storage_dir / "config.yaml"


def load_config() -> dict:
    if _storage_config.exists():
        path = _storage_config
    else:
        path = _bundled_config
        # Seed storage with the bundled default so it can be edited in place
        try:
            _storage_dir.mkdir(parents=True, exist_ok=True)
            _storage_config.write_text(_bundled_config.read_text())
        except OSError:
            pass  # storage not writable yet (e.g. first boot before mount)

    with open(path) as f:
        return yaml.safe_load(f)


def _int_env(key: str, default: str, lo: int, hi: int) -> int:
    val = int(os.getenv(key, default))
    if not lo <= val <= hi:
        raise RuntimeError(f"{key}={val} out of range [{lo}, {hi}]")
    return val


CONFIG = load_config()

# All env vars use empty-string defaults so the app can boot for healthchecks
# before env vars are configured. validate_config() checks them before use.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
LINKDING_TOKEN = os.getenv("LINKDING_TOKEN", "")
LINKDING_URL = os.getenv("LINKDING_URL", "https://pinboard.multiplicity.dk").rstrip("/")
SMTP_HOST = os.getenv("SMTP_HOST", "blizzard.mxrouting.net")
SMTP_PORT = _int_env("SMTP_PORT", "587", 1, 65535)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "") or SMTP_USER
DIGEST_HOUR = _int_env("DIGEST_HOUR", "7", 0, 23)
DIGEST_MINUTE = _int_env("DIGEST_MINUTE", "53", 0, 59)

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "/storage"))
DIGESTS_DIR = STORAGE_DIR / "digests"

_REQUIRED = {
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "BRAVE_API_KEY": BRAVE_API_KEY,
    "LINKDING_TOKEN": LINKDING_TOKEN,
    "SMTP_USER": SMTP_USER,
    "SMTP_PASS": SMTP_PASS,
    "EMAIL_TO": EMAIL_TO,
}


def validate_config():
    missing = [k for k, v in _REQUIRED.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
