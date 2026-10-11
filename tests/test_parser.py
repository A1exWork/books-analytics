
import asyncio
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

import app.parser as parser


BOOK_HTML = """
<article class="product_pod">
    <h3>
        <a href="book_1.html" title="Python Book">Book</a>
    </h3>
    <p class="star-rating Five"></p>
    <p class="price_color">£25.50</p>
    <p class="availability">In stock</p>
</article>
"""


def test_extract_books():
    books = parser.extract_books(
        BOOK_HTML,
        "https://example.com/catalogue/",
    )

    assert len(books) == 1

    book = books[0]

    assert book.title == "Python Book"
    assert book.price == 25.50
    assert book.rating == 5
    assert book.availability == "In stock"
    assert book.url == "https://example.com/catalogue/book_1.html"


def test_extract_books_empty_page():
    books = parser.extract_books(
        "<html><body></body></html>",
        "https://example.com/",
    )

    assert books == []


def test_extract_books_unknown_rating():
    html = BOOK_HTML.replace(
        "star-rating Five",
        "star-rating Unknown",
    )

    books = parser.extract_books(
        html,
        "https://example.com/",
    )

    assert books[0].rating == 0


def test_fetch_page_success():
    async def run():
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.text = AsyncMock(return_value="<html>OK</html>")

        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=None)

        session = MagicMock()
        session.get.return_value = context

        result = await parser.fetch_page(
            session,
            "https://example.com/",
            asyncio.Semaphore(1),
        )

        assert result == "<html>OK</html>"
        session.get.assert_called_once()

    asyncio.run(run())


def test_fetch_page_retries(monkeypatch):
    async def run():
        attempts = 0

        async def fake_sleep(seconds):
            pass

        monkeypatch.setattr(parser.asyncio, "sleep", fake_sleep)

        response = MagicMock()
        response.text = AsyncMock(return_value="OK")

        def raise_once():
            nonlocal attempts
            attempts += 1

            if attempts == 1:
                raise aiohttp.ClientError("Temporary error")

        response.raise_for_status.side_effect = raise_once

        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=None)

        session = MagicMock()
        session.get.return_value = context

        result = await parser.fetch_page(
            session,
            "https://example.com/",
            asyncio.Semaphore(1),
        )

        assert result == "OK"
        assert attempts == 2

    asyncio.run(run())


def test_fetch_page_all_retries_fail(monkeypatch):
    async def run():
        async def fake_sleep(seconds):
            pass

        monkeypatch.setattr(parser.asyncio, "sleep", fake_sleep)

        response = MagicMock()
        response.raise_for_status.side_effect = aiohttp.ClientError(
            "Connection failed"
        )

        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=None)

        session = MagicMock()
        session.get.return_value = context

        with pytest.raises(aiohttp.ClientError):
            await parser.fetch_page(
                session,
                "https://example.com/",
                asyncio.Semaphore(1),
            )

        assert session.get.call_count == parser.MAX_RETRIES

    asyncio.run(run())


def test_parse_books(monkeypatch):
    async def run():
        first_page = """
        <html>
            <li class="current">Page 1 of 2</li>
        </html>
        """ + BOOK_HTML

        second_page = BOOK_HTML.replace(
            "Python Book",
            "Second Book",
        ).replace(
            "book_1.html",
            "book_2.html",
        )

        async def fake_fetch(session, url, semaphore):
            if url == parser.BASE_URL:
                return first_page
            return second_page

        monkeypatch.setattr(parser, "fetch_page", fake_fetch)

        books = await parser.parse_books()

        assert len(books) == 2
        assert books[0].title == "Python Book"
        assert books[1].title == "Second Book"

    asyncio.run(run())


def test_parse_books_invalid_pagination(monkeypatch):
    async def run():
        async def fake_fetch(session, url, semaphore):
            return "<html><li class='current'>Unknown</li></html>"

        monkeypatch.setattr(parser, "fetch_page", fake_fetch)

        with pytest.raises(ValueError):
            await parser.parse_books()

    asyncio.run(run())
