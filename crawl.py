import requests

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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
