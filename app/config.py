import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_config_path = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(_config_path) as f:
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
