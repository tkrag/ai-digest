import logging
from dataclasses import dataclass

import httpx

from app.config import BRAVE_API_KEY, CONFIG

logger = logging.getLogger(__name__)

BRAVE_NEWS_URL = "https://api.search.brave.com/res/v1/news/search"

search_config = CONFIG.get("search", {})
DEFAULT_FRESHNESS = search_config.get("freshness", "pd")
RESULTS_PER_QUERY = search_config.get("results_per_query", 10)


@dataclass
class Article:
    url: str
    title: str
    snippet: str
    source: str
    published: str
    search_category: str


async def search_brave(query: str, freshness: str = DEFAULT_FRESHNESS) -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            BRAVE_NEWS_URL,
            headers={"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"},
            params={"q": query, "count": RESULTS_PER_QUERY, "freshness": freshness},
        )
        resp.raise_for_status()
        data = resp.json()
    return data.get("results", [])


async def search_category(category_key: str, category_cfg: dict) -> list[Article]:
    articles = []
    seen_urls = set()

    for query in category_cfg.get("queries", []):
        try:
            results = await search_brave(query)
        except Exception:
            logger.exception("Brave search failed for query: %s", query)
            continue

        for r in results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            articles.append(Article(
                url=url,
                title=r.get("title", ""),
                snippet=r.get("description", ""),
                source=r.get("meta_url", {}).get("hostname", "") if isinstance(r.get("meta_url"), dict) else "",
                published=r.get("age", ""),
                search_category=category_key,
            ))

    return articles


async def search_all_categories() -> list[Article]:
    categories = CONFIG.get("categories", {})
    all_articles = []
    seen_urls = set()

    for key, cfg in categories.items():
        if not cfg.get("queries"):
            continue
        cat_articles = await search_category(key, cfg)
        for a in cat_articles:
            if a.url not in seen_urls:
                seen_urls.add(a.url)
                all_articles.append(a)

    logger.info("Found %d unique articles across all categories", len(all_articles))
    return all_articles
