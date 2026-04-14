# AI Digest

Daily AI research agent that searches for notable articles, classifies them by category, bookmarks them to LinkDing, and emails a brief summary.

## How it works

Runs as a Docker container on Once (Hetzner). A scheduler triggers the digest pipeline once daily:

1. **Search** — Queries Brave News API across configured categories
2. **Classify** — Sends articles to Claude for scoring and categorization
3. **Bookmark** — Posts selected articles to LinkDing with category + date tags
4. **Email** — Sends a summary with an overview paragraph and LinkDing filter links

## Categories

| Key | Label | What it covers |
|---|---|---|
| `ai-gone-bad` | AI Gone Bad | Security breaches, compliance failures, bias incidents |
| `new-tools` | New Tools | New AI tools, libraries, platforms, model releases |
| `success-stories` | Success Stories | Case studies with concrete KPIs and metrics |
| `ai-ecommerce` | E-Commerce | AI in D2C e-commerce, personalization, logistics |
| `all-star` | All-Star | Doesn't fit above but is highly relevant |

## Deployment

**Package:** `ghcr.io/tkrag/ai-digest:latest`

GitHub Actions builds and pushes the image on every push to `main`. Make sure the ghcr.io package is set to public (Package Settings > Danger Zone > Change visibility).

### Environment variables (set in Once TUI)

| Variable | Example |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `BRAVE_API_KEY` | `BSA...` |
| `LINKDING_TOKEN` | LinkDing API token |
| `LINKDING_URL` | `https://pinboard.multiplicity.dk` |
| `SMTP_HOST` | `blizzard.mxrouting.net` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | `once@krag.be` |
| `SMTP_PASS` | SMTP password |
| `EMAIL_TO` | `tomas.krag@hobbii.dk` |
| `EMAIL_FROM` | `once@krag.be` |
| `DIGEST_HOUR` | `7` (0-23, default 7) |
| `DIGEST_MINUTE` | `53` (0-59, default 53) |

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/up` | Healthcheck (required by Once) |
| `GET` | `/` | Service status + next scheduled run time |
| `POST` | `/run` | Manually trigger a digest run |

## Editing the config

All categories, search queries, scoring thresholds, and the Claude prompt live in `config.yaml`. On first boot, this file is copied from the image into `/storage/config.yaml`. Subsequent boots read from `/storage`, so you can edit it on the server without rebuilding.

### To edit config on the server

```bash
# SSH into the Hetzner server

# Find the container name
docker ps | grep ai-digest

# Option A: edit inside the container
docker exec -it <container> nano /storage/config.yaml

# Option B: copy out, edit, copy back
docker cp <container>:/storage/config.yaml ./config.yaml
nano ./config.yaml
docker cp ./config.yaml <container>:/storage/config.yaml

# Restart the container in Once TUI to pick up changes
```

### Adding a new category

Add a block under `categories:` in `config.yaml`:

```yaml
  ai-regulation:
    label: "AI Regulation"
    description: "New laws, policy proposals, and government actions around AI"
    queries:
      - "AI regulation law passed OR AI policy government"
      - "AI act enforcement OR AI governance legislation"
    max_articles: 3
    min_relevance: 7
    tags: ["ai-regulation"]
```

Then restart the container.

### Tuning the scoring prompt

The `scoring_prompt:` field in `config.yaml` is the full instruction set Claude receives for evaluating articles. Edit it to change how aggressively articles are filtered, what counts as relevant, or any category-specific rules.

## Updating the code

1. Make changes and push to `main`
2. Wait for the [GitHub Actions build](https://github.com/tkrag/ai-digest/actions) to go green (~2 min)
3. Pull the latest image in the Once TUI

## Data

Daily digest results are saved as JSON in `/storage/digests/YYYY-MM-DD.json` inside the container.
