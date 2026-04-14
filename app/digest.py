import asyncio
import json
import logging
from datetime import date

from app.classify import classify_articles
from app.config import DIGESTS_DIR
from app.linkding import bookmark_articles
from app.mailer import send_digest_email
from app.search import search_all_categories

logger = logging.getLogger(__name__)

_lock = asyncio.Lock()


async def run_digest() -> dict:
    if _lock.locked():
        logger.warning("Digest already running, skipping")
        return {"error": "already_running"}

    async with _lock:
        logger.info("Starting daily digest run")
        date_str = date.today().isoformat()

        # 1. Search
        articles = await search_all_categories()
        if not articles:
            logger.warning("No articles found from search")
            await send_digest_email([])
            return {"date": date_str, "searched": 0, "selected": 0, "bookmarked": 0}

        logger.info("Search returned %d articles", len(articles))

        # 2. Classify and rank
        selected, overview = await classify_articles(articles)
        logger.info("Classification selected %d articles", len(selected))

        # 3. Bookmark to LinkDing
        bookmarked = await bookmark_articles(selected)

        # 4. Send email
        await send_digest_email(selected, overview)

        # 5. Save digest to storage
        result = {
            "date": date_str,
            "searched": len(articles),
            "selected": len(selected),
            "bookmarked": bookmarked,
            "overview": overview,
            "articles": [
                {
                    "url": a.url,
                    "title": a.title,
                    "summary": a.summary,
                    "category": a.category,
                    "score": a.score,
                }
                for a in selected
            ],
        }

        try:
            DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
            out_path = DIGESTS_DIR / f"{date_str}.json"
            out_path.write_text(json.dumps(result, indent=2))
            logger.info("Digest saved to %s", out_path)
        except Exception:
            logger.exception("Failed to save digest to storage")

        return result
