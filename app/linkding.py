import logging
from datetime import date

import httpx

from app.config import LINKDING_TOKEN, LINKDING_URL, CONFIG
from app.classify import ScoredArticle

logger = logging.getLogger(__name__)

DIGEST_TAG = CONFIG.get("linkding", {}).get("digest_tag", "ai-digest")


def _tags_for_article(article: ScoredArticle, date_str: str) -> list[str]:
    categories = CONFIG.get("categories", {})
    cat_cfg = categories.get(article.category, {})
    tags = list(cat_cfg.get("tags", []))
    tags.append(DIGEST_TAG)
    tags.append(f"digest-{date_str}")
    return tags


async def bookmark_articles(articles: list[ScoredArticle]) -> int:
    date_str = date.today().isoformat()
    bookmarked = 0

    async with httpx.AsyncClient(timeout=30) as client:
        for article in articles:
            tags = _tags_for_article(article, date_str)
            payload = {
                "url": article.url,
                "title": article.title,
                "description": article.summary,
                "tag_names": tags,
            }
            try:
                resp = await client.post(
                    f"{LINKDING_URL}/api/bookmarks/",
                    headers={"Authorization": f"Token {LINKDING_TOKEN}"},
                    json=payload,
                )
                resp.raise_for_status()
                bookmarked += 1
            except Exception:
                logger.exception("Failed to bookmark: %s", article.url)

    logger.info("Bookmarked %d/%d articles", bookmarked, len(articles))
    return bookmarked


def linkding_search_url(tag: str, date_str: str) -> str:
    q = f"#{tag} #digest-{date_str}"
    return f"{LINKDING_URL}/bookmarks?q={q}"
