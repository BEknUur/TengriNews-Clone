# Python modules
import logging
import re
from typing import Any

# Third-party modules
from celery import shared_task

# Project modules
from apps.main.models import Article

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def process_article_content_task(self: Any, article_id: int) -> dict[str, int]:
    """Calculate word count and estimated read time for an article."""
    article: Article | None = Article.objects.filter(
        id=article_id, deleted_at__isnull=True
    ).first()
    if not article:
        logger.error("process_article_content_task: article_id=%s not found", article_id)
        raise ValueError(f"Article with id {article_id} does not exist.")

    text = re.sub(r"<[^>]+>", "", article.content or "")
    words = [w for w in re.split(r"\s+", text) if w.strip()]
    word_count = len(words)
    read_time_minutes = max(1, word_count // 200) if word_count else 0

    result = {
        "article_id": article_id,
        "word_count": word_count,
        "read_time_minutes": read_time_minutes,
    }
    logger.info("process_article_content_task completed: %s", result)
    return result
