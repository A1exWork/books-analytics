

import asyncio
import re
import logging

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.config import (
    BASE_URL,
    REQUEST_TIMEOUT,
    CONCURRENT_REQUESTS,
    MAX_RETRIES,
)
from app.models import Book


logger = logging.getLogger(__name__)

RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def extract_books(html: str, page_url: str) -> list[Book]:
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for card in soup.select("article.product_pod"):
        title = card.select_one("h3 a")["title"]

        price_text = card.select_one(
            ".price_color"
        ).get_text(strip=True)

        price = float(
            price_text.replace("£", "").replace("Â", "")
        )

        rating_classes = card.select_one(
            ".star-rating"
        ).get("class", [])

        rating = next(
            (
                value
                for name, value in RATINGS.items()
                if name in rating_classes
            ),
            0,
        )

        availability = card.select_one(
            ".availability"
        ).get_text(strip=True)

        relative_url = card.select_one("h3 a")["href"]
        book_url = urljoin(page_url, relative_url)

        books.append(
            Book(
                title=title,
                price=price,
                rating=rating,
                availability=availability,
                url=book_url,
            )
        )

    return books


async def fetch_page(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> str:
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()

            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
            ) as error:
                logger.warning(
                    "Ошибка загрузки %s, попытка %s/%s: %s",
                    url,
                    attempt,
                    MAX_RETRIES,
                    error,
                )

                if attempt == MAX_RETRIES:
                    raise

                await asyncio.sleep(attempt)

            finally:
                logger.debug(
                    "Завершена попытка %s для %s",
                    attempt,
                    url,
                )

    raise RuntimeError(f"Не удалось загрузить {url}")


async def parse_books() -> list[Book]:
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    semaphore = asyncio.Semaphore(
        CONCURRENT_REQUESTS
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        first_html = await fetch_page(
            session,
            BASE_URL,
            semaphore,
        )

        first_soup = BeautifulSoup(
            first_html,
            "html.parser",
        )

        page_text = first_soup.select_one(
            "li.current"
        ).get_text(" ", strip=True)

        match = re.search(
            r"Page\s+\d+\s+of\s+(\d+)",
            page_text,
        )

        if not match:
            raise ValueError(
                "Не удалось определить количество страниц"
            )

        total_pages = int(match.group(1))

        books = extract_books(
            first_html,
            BASE_URL,
        )

        page_urls = [
            urljoin(
                BASE_URL,
                f"catalogue/page-{page}.html",
            )
            for page in range(2, total_pages + 1)
        ]

        tasks = [
            fetch_page(session, url, semaphore)
            for url in page_urls
        ]

        html_pages = await asyncio.gather(*tasks)

        for url, html in zip(page_urls, html_pages):
            books.extend(
                extract_books(html, url)
            )

        logger.info(
            "Собрано %s книг с %s страниц",
            len(books),
            total_pages,
        )

        return books
