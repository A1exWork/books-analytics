
BASE_URL = "https://books.toscrape.com/"
REQUEST_TIMEOUT = 15
CONCURRENT_REQUESTS = 5
MAX_RETRIES = 3

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BOOKS_FILE = DATA_DIR / "books.json"


PARSE_INTERVAL_MINUTES = 30

MIN_PRICE = None
MAX_PRICE = None
MIN_RATING = None