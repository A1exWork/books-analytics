
import argparse
import asyncio
import logging

from app.analytics import analyze_books
from app.filters import filter_books
from app.logging_config import setup_logging
from app.parser import parse_books
from app.scheduler import run_scheduler
from app.storage import save_books


logger = logging.getLogger(__name__)


async def run_once() -> None:
    logger.info("Начинаем сбор книг")

    books = await parse_books()

    logger.info(
        "Парсер получил %s книг",
        len(books),
    )

    if not books:
        raise RuntimeError(
            "Парсер не вернул ни одной книги"
        )

    storage_result = save_books(books)

    filtered_books = filter_books(books)

    metrics = analyze_books(filtered_books)

    logger.info(
        "Результат сохранения: %s",
        storage_result,
    )

    logger.info(
        "Результат аналитики: %s",
        metrics,
    )


def main() -> None:
    setup_logging()

    argument_parser = argparse.ArgumentParser(
        description="Books Analytics Parser"
    )

    argument_parser.add_argument(
        "--schedule",
        action="store_true",
        help="Запускать парсер по расписанию",
    )

    args = argument_parser.parse_args()

    if args.schedule:
        asyncio.run(run_scheduler(run_once))
    else:
        asyncio.run(run_once())


if __name__ == "__main__":
    main()
