import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Score
from app.scoring.engine import run_scoring_job

logger = logging.getLogger("saans.scoring_cycle")

PostScoringHook = Callable[[Session, list[Score], Settings], None]

_post_scoring_hooks: list[PostScoringHook] = []


def register_post_scoring_hook(hook: PostScoringHook) -> None:
    _post_scoring_hooks.append(hook)


def run_full_scoring_cycle(db: Session, settings: Settings) -> list[Score]:
    scores = run_scoring_job(db, settings)
    for hook in _post_scoring_hooks:
        try:
            hook(db, scores, settings)
        except Exception:
            logger.exception("post-scoring hook %s failed, continuing with the rest", hook.__module__)
    return scores
