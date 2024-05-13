from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as soup

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
        for a in soup(html_content, "html.parser").find_all("a")
        if "href" in a.attrs
    ]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
