from __future__ import annotations

import logging

from app.core.config import get_settings
from app.db.database import init_db
from app.services.jobs import ensure_storage
from app.services.worker import run_worker_loop


def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    ensure_storage()
    init_db()
    run_worker_loop(poll_seconds=settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
