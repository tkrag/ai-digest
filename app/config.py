import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_config_path = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(_config_path) as f:
        return yaml.safe_load(f)


def get_env(key: str, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


CONFIG = load_config()

ANTHROPIC_API_KEY = get_env("ANTHROPIC_API_KEY")
BRAVE_API_KEY = get_env("BRAVE_API_KEY")
LINKDING_TOKEN = get_env("LINKDING_TOKEN")
LINKDING_URL = get_env("LINKDING_URL", "https://pinboard.multiplicity.dk").rstrip("/")
SMTP_HOST = get_env("SMTP_HOST", "blizzard.mxrouting.net")
SMTP_PORT = int(get_env("SMTP_PORT", "587"))
SMTP_USER = get_env("SMTP_USER")
SMTP_PASS = get_env("SMTP_PASS")
EMAIL_TO = get_env("EMAIL_TO")
EMAIL_FROM = get_env("EMAIL_FROM", SMTP_USER)
DIGEST_HOUR = int(get_env("DIGEST_HOUR", "7"))
DIGEST_MINUTE = int(get_env("DIGEST_MINUTE", "53"))

STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "/storage"))
DIGESTS_DIR = STORAGE_DIR / "digests"
