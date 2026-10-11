
import logging

from collections import Counter, defaultdict
from dataclasses import asdict

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from app.config import PROJECT_ROOT
from app.models import Book


logger = logging.getLogger(__name__)

REPORTS_DIR = PROJECT_ROOT / "reports"


def analyze_books(books: list[Book]) -> dict:
    if not books:
        logger.warning("Нет книг для анализа")
        return {}

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.DataFrame(
        [asdict(book) for book in books]
    )

    average_price = float(df["price"].mean())
    median_price = float(df["price"].median())

    rating_counts = Counter(
        book.rating for book in books
    )

    prices_by_rating = defaultdict(list)

    for book in books:
        prices_by_rating[book.rating].append(
            book.price
        )

    average_by_rating = {
        rating: sum(prices) / len(prices)
        for rating, prices in sorted(
            prices_by_rating.items()
        )
    }

    plt.figure(figsize=(9, 5))
    plt.hist(
        df["price"],
        bins=20,
        edgecolor="black",
    )
    plt.title("Book price distribution")
    plt.xlabel("Price (£)")
    plt.ylabel("Number of books")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "prices.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(
        list(sorted(rating_counts)),
        [
            rating_counts[rating]
            for rating in sorted(rating_counts)
        ],
    )
    plt.title("Book ratings")
    plt.xlabel("Rating")
    plt.ylabel("Number of books")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "ratings.png")
    plt.close()

    metrics = {
        "total_books": len(books),
        "average_price": round(average_price, 2),
        "median_price": round(median_price, 2),
        "rating_counts": dict(
            sorted(rating_counts.items())
        ),
        "average_price_by_rating": {
            rating: round(price, 2)
            for rating, price in average_by_rating.items()
        },
    }

    logger.info(
        "Аналитика завершена: %s книг",
        len(books),
    )

    return metrics
