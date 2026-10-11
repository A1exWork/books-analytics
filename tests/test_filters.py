
import app.filters as filters
from app.models import Book


def make_book(title, price, rating):
    return Book(
        title=title,
        price=price,
        rating=rating,
        availability="In stock",
        url=f"https://example.com/{title}",
    )


def test_min_price(monkeypatch):
    monkeypatch.setattr(filters, "MIN_PRICE", 20)
    monkeypatch.setattr(filters, "MAX_PRICE", None)
    monkeypatch.setattr(filters, "MIN_RATING", None)

    books = [
        make_book("cheap", 10, 5),
        make_book("expensive", 30, 5),
    ]

    result = filters.filter_books(books)

    assert len(result) == 1
    assert result[0].title == "expensive"


def test_max_price(monkeypatch):
    monkeypatch.setattr(filters, "MIN_PRICE", None)
    monkeypatch.setattr(filters, "MAX_PRICE", 20)
    monkeypatch.setattr(filters, "MIN_RATING", None)

    books = [
        make_book("cheap", 10, 5),
        make_book("expensive", 30, 5),
    ]

    result = filters.filter_books(books)

    assert len(result) == 1
    assert result[0].title == "cheap"


def test_min_rating(monkeypatch):
    monkeypatch.setattr(filters, "MIN_PRICE", None)
    monkeypatch.setattr(filters, "MAX_PRICE", None)
    monkeypatch.setattr(filters, "MIN_RATING", 4)

    books = [
        make_book("low", 20, 2),
        make_book("high", 20, 5),
    ]

    result = filters.filter_books(books)

    assert len(result) == 1
    assert result[0].title == "high"


def test_without_filters(monkeypatch):
    monkeypatch.setattr(filters, "MIN_PRICE", None)
    monkeypatch.setattr(filters, "MAX_PRICE", None)
    monkeypatch.setattr(filters, "MIN_RATING", None)

    books = [
        make_book("first", 10, 1),
        make_book("second", 50, 5),
    ]

    assert filters.filter_books(books) == books
