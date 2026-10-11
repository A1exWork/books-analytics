
import hashlib
import json
import logging

from dataclasses import asdict
from pathlib import Path

from app.config import BOOKS_FILE
from app.models import Book


logger = logging.getLogger(__name__)


def book_hash(book: Book) -> str:
    return hashlib.sha256(
        book.url.encode("utf-8")
    ).hexdigest()


def load_books(path: Path = BOOKS_FILE) -> dict[str, dict]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        saved_books = json.load(file)

    if not isinstance(saved_books, list):
        raise ValueError("JSON должен содержать список книг")

    return {
        book["id"]: book
        for book in saved_books
    }


def save_books(
    books: list[Book],
    path: Path = BOOKS_FILE,
) -> dict[str, int]:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved = load_books(path)

    added = 0
    updated = 0

    for book in books:
        book_id = book_hash(book)

        book_data = asdict(book)
        book_data["id"] = book_id

        if book_id not in saved:
            saved[book_id] = book_data
            added += 1

        elif saved[book_id] != book_data:
            saved[book_id] = book_data
            updated += 1

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            list(saved.values()),
            file,
            ensure_ascii=False,
            indent=4,
        )

    logger.info(
        "Сохранено книг: %s. Новых: %s. Обновлено: %s",
        len(saved),
        added,
        updated,
    )

    return {
        "total": len(saved),
        "added": added,
        "updated": updated,
    }
