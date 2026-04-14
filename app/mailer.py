import logging
import smtplib
import ssl
from datetime import date
from email.mime.text import MIMEText

from app.classify import ScoredArticle
from app.config import CONFIG, EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PASS, SMTP_PORT, SMTP_USER
from app.linkding import DIGEST_TAG, linkding_search_url

logger = logging.getLogger(__name__)

CATEGORY_ICONS = {
    "ai-gone-bad": "\U0001f512",
    "new-tools": "\U0001f6e0\ufe0f",
    "success-stories": "\U0001f4c8",
    "ai-ecommerce": "\U0001f6d2",
    "all-star": "\u2b50",
}


def _build_email(articles: list[ScoredArticle], date_str: str, overview: str = "") -> tuple[str, str]:
    categories = CONFIG.get("categories", {})

    by_cat: dict[str, list[ScoredArticle]] = {}
    for a in articles:
        by_cat.setdefault(a.category, []).append(a)

    total = len(articles)
    cat_count = len(by_cat)

    lines = [f"Found {total} article{'s' if total != 1 else ''} across {cat_count} categor{'ies' if cat_count != 1 else 'y'} today.\n"]

    if overview:
        lines.append(overview)
        lines.append("")

    for key, cfg in categories.items():
        cat_articles = by_cat.get(key, [])
        if not cat_articles:
            continue
        icon = CATEGORY_ICONS.get(key, "")
        label = cfg["label"]
        count = len(cat_articles)
        primary_tag = cfg.get("tags", [key])[0]
        url = linkding_search_url(primary_tag, date_str)
        lines.append(f"{icon} {label} ({count})")
        lines.append(f"   {url}\n")

    empty_cats = [cfg["label"] for key, cfg in categories.items() if key not in by_cat]
    if empty_cats:
        lines.append(f"Nothing today: {', '.join(empty_cats)}")

    all_url = linkding_search_url(DIGEST_TAG, date_str)
    lines.append(f"\nAll articles: {all_url}")

    text = "\n".join(lines)
    subject = f"AI Digest \u2014 {date_str}"
    return subject, text


async def send_digest_email(articles: list[ScoredArticle], overview: str = ""):
    date_str = date.today().isoformat()
    subject, body = _build_email(articles, date_str, overview)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=ctx)
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info("Digest email sent to %s", EMAIL_TO)
    except Exception:
        logger.exception("Failed to send digest email")
