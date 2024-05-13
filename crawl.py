import json
import shutil
from collections import deque
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from logger import setup_logger

log = setup_logger(__name__)


def fetch_html_content(url: str) -> str | None:
    """
    Fetch HTML content for a given URL.

    Args:
        url (str): The URL from which to fetch the HTML content.

    Returns:
        str: The raw HTML content of the page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as exc:
        log.error(f"Failed to fetch HTML content from {url}: {exc}")
        return None


def extract_page_urls(html_content: str, url: str, current_depth: int) -> list[dict]:
    """
    Parse HTML content to extract page URLs.

    Args:
        html_content (str): The raw HTML content.
        url (str): The URL from which the HTML content was fetched.
        current_depth (int): The current depth of the URL being processed.

    Returns:
        A list of dictionaries, where each dictionary contains the
        following keys:
        - 'url': The URL of the page.
        - 'page': The URL of the page where the URL was found.
        - 'depth': The depth at which the URL was found relative to the starting URL.
    """
    return [
        {
            "url": urljoin(url, a["href"]),
            "page": url,
            "depth": current_depth,
        }
        for a in BeautifulSoup(html_content, "html.parser").find_all("a")
        if "href" in a.attrs
    ]


def extract_links(html_content: str, url: str) -> list[str]:
    """
    Parse HTML content to extract links.

    Args:
        html_content (str): The raw HTML content.
        url (str): The URL from which the HTML content was fetched.

    Returns:
        A list of URL strings from the href attributes of anchor tags.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    return [a["href"] for a in soup.find_all("a") if "href" in a.attrs]


def fetch_pages_from_url(url: str, current_depth: int, max_depth: int) -> list[dict]:
    """
    Fetch pages from a given URL and its linked pages up to a specified depth.

    Note:
        We are using BFS algorithm to crawl pages, avoiding processing the same URL multiple times.

    Args:
        url (str): The starting URL from which to fetch pages.
        current_depth (int): The current depth of the URL being processed.
        max_depth (int): The maximum depth to crawl from the starting URL.

    Returns:
        A list of dictionaries, each containing the following keys:
        - 'url': The URL of the page.
        - 'html': The raw HTML content of the page.
        - 'depth': The depth at which the page was found relative to the starting URL.

        Return an empty list if no pages are found or in case of a request failure.
    """
    pages = []
    visited_urls = set()
    queue = deque([(url, current_depth)])

    while queue:
        current_url, current_depth = queue.popleft()
        # Skip processing if the URL has already been visited
        if current_url in visited_urls:
            continue
        visited_urls.add(current_url)

        log.info(f"Fetching pages from {current_url} at depth {current_depth}")
        html_content = fetch_html_content(current_url)
        pages.extend(extract_page_urls(html_content, current_url, current_depth))

        # Stop crawling if current depth reaches maximum depth
        if current_depth == max_depth:
            continue
        links = extract_links(html_content, current_url)
        for link in links:
            page_url = urljoin(current_url, link)
            # `current_depth` incremented by 1
            # indicating it's now one level deeper.
            queue.append((page_url, current_depth + 1))

    return pages


def save_pages_metadata(pages: list[dict]) -> None:
    """
    Save page metadata to a JSON file.

    Args:
        pages (list of dict): A list of dictionaries where each dictionary contains the 'url', 'depth', and 'html' keys.
    """
    pages_dir = Path("pages")
    if not pages_dir.exists():
        shutil.rmtree(pages_dir)
    # don't raise an error if directory already exists
    pages_dir.mkdir(exist_ok=True)

    if not pages:
        log.info("No pages to save metadata for.")
        return

    metadata = {"pages": pages}
    with open(pages_dir / "pages_metadata.json") as fp:
        json.dump(metadata, fp, indent=4)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
