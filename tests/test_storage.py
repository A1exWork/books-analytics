
from app.models import Book
from app.storage import book_hash, load_books, save_books


def make_book(price=25.50):
    return Book(
        title="Python для начинающих",
        price=price,
        rating=5,
        availability="In stock",
        url="https://example.com/python",
    )


def test_book_hash():
    book = make_book()

    assert book_hash(book) == book_hash(book)
    assert len(book_hash(book)) == 64


def test_save_books_without_duplicates(tmp_path):
    file_path = tmp_path / "books.json"
    book = make_book()

    first_result = save_books([book], path=file_path)

    assert first_result == {
        "total": 1,
        "added": 1,
        "updated": 0,
    }

    second_result = save_books([book], path=file_path)

    assert second_result == {
        "total": 1,
        "added": 0,
        "updated": 0,
    }

    assert len(load_books(file_path)) == 1


def test_update_existing_book(tmp_path):
    file_path = tmp_path / "books.json"

    save_books([make_book(price=25.50)], path=file_path)

    updated_book = make_book(price=30.00)
    result = save_books([updated_book], path=file_path)

    assert result == {
        "total": 1,
        "added": 0,
        "updated": 1,
    }

    saved_books = load_books(file_path)
    assert saved_books[book_hash(updated_book)]["price"] == 30.00
