from pathlib import Path

import pytest
import requests_mock

from crawl import fetch_pages_from_url


@pytest.fixture
def mock_response():
    # fixture that provides a mocked HTML response containing links
    return """
    <html>
        <body>
            <a href="http://example.com/page1.html">Page 1</a>
            <a href="http://example.com/page2.html">Page 2</a>
            <a href="http://example.com/page3.html">Page 3</a>
            <a href="http://example.com/nextpage.html">Next Page</a>
        </body>
    </html>
    """


@pytest.fixture
def cleanup_pages_dir():
    # cleanup fixture to run after tests that might create files/directories
    yield
    pages_dir = Path("pages")
    if pages_dir.exists():
        for file in pages_dir.iterdir():
            file.unlink()
        pages_dir.rmdir()


def assert_pages_start_with(pages, prefix):
    """
    Check that each page URL in the list starts with the given prefix.
    """
    for page in pages:
        assert page["url"].startswith(
            prefix
        ), f"Page URL {page['url']} does not start with {prefix}"


def test_fetch_pages_single_page(mock_response):
    """
    Verify that `fetch_pages_from_url` can successfully fetch page URLs from
    a given page without following any links.
    """
    with requests_mock.Mocker() as m:
        m.get("http://example.com/testpage.html", text=mock_response)
        m.get("http://example.com/nextpage.html", text=mock_response)
        pages = fetch_pages_from_url("http://example.com/testpage.html", 1, 1)
        assert len(pages) == 3
        # helper function to assert the condition for each page URL
        assert_pages_start_with(pages, "http://example.com/page")


def test_handling_maximum_depth(mock_response):
    """
    Check that the crawler respects the `max_depth` parameter.
    """
    with requests_mock.Mocker() as m:
        m.get("http://example.com/testpage.html", text=mock_response)
        m.get("http://example.com/nextpage.html", text=mock_response)
        # assuming depth 1 means only the initial page is processed
        pages = fetch_pages_from_url("http://example.com/testpage.html", 1, 2)
        # make sure no additional pages from "next page" are included
        assert len(pages) == 6
