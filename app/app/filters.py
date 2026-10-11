from app.config import MIN_PRICE, MAX_PRICE, MIN_RATING
from app.models import Book


def filter_books(books: list[Book]) -> list[Book]:
    result = []

    for book in books:
        if MIN_PRICE is not None and book.price < MIN_PRICE:
            continue

        if MAX_PRICE is not None and book.price > MAX_PRICE:
            continue

        if MIN_RATING is not None and book.rating < MIN_RATING:
            continue

        result.append(book)

    return result