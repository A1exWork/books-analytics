
import asyncio
import logging

from collections.abc import Awaitable, Callable

from app.config import PARSE_INTERVAL_MINUTES


logger = logging.getLogger(__name__)


async def run_scheduler(
    job: Callable[[], Awaitable[None]],
) -> None:
    interval_seconds = PARSE_INTERVAL_MINUTES * 60

    if interval_seconds <= 0:
        raise ValueError(
            "Интервал запуска должен быть больше нуля"
        )

    while True:
        try:
            await job()

        except Exception:
            logger.exception(
                "Ошибка выполнения запланированной задачи"
            )

        finally:
            logger.info(
                "Следующий запуск через %s минут",
                PARSE_INTERVAL_MINUTES,
            )

        await asyncio.sleep(interval_seconds)
