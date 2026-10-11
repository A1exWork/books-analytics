
import app.analytics as analytics
from app.models import Book


def test_analyze_books(tmp_path, monkeypatch):
    # Не перезаписываем настоящие графики
    monkeypatch.setattr(analytics, "REPORTS_DIR", tmp_path)

    books = [
        Book("First", 10.0, 1, "In stock", "https://example.com/1"),
        Book("Second", 20.0, 3, "In stock", "https://example.com/2"),
        Book("Third", 30.0, 5, "In stock", "https://example.com/3"),
    ]

    result = analytics.analyze_books(books)

    assert result["total_books"] == 3
    assert result["average_price"] == 20.0
    assert result["median_price"] == 20.0

    assert result["rating_counts"] == {
        1: 1,
        3: 1,
        5: 1,
    }

    assert result["average_price_by_rating"] == {
        1: 10.0,
        3: 20.0,
        5: 30.0,
    }

    assert (tmp_path / "prices.png").exists()
    assert (tmp_path / "ratings.png").exists()
