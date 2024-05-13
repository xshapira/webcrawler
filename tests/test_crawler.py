import json
from pathlib import Path

import pytest
import requests_mock

from crawl import fetch_pages_from_url, save_pages_locally, save_pages_metadata


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


def test_save_pages_locally(requests_mock, mocker):
    """
    Verify that `save_pages_locally` correctly saves page content to local files and handles duplicate page URLs.
    """
    # mock HTTP responses for page URLs
    requests_mock.get(
        "http://example.com/page1.html", text="<html>Page 1 content</html>"
    )
    requests_mock.get(
        "http://example.com/page2.html", text="<html>Page 2 content</html>"
    )

    # mock filesystem interactions
    # assume directory doesn't exist
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch("pathlib.Path.mkdir")  # mock mkdir to do nothing

    # mock open
    mock_open_function = mocker.patch("builtins.open", mocker.mock_open())

    pages = [
        {
            "url": "http://example.com/page1.html",
            "depth": 1,
        },
        {
            "url": "http://example.com/page1.html",  # duplicate
            "depth": 1,
        },
        {
            "url": "http://example.com/page2.html",
            "depth": 1,
        },
    ]
    # this should now use the mocked open and not actually write files
    save_pages_locally(pages)

    # With open mocked, we can't check the filesystem to verify behavior as
    # before. Instead, we can check if open was called the expected number of
    # times with the right arguments.
    assert mock_open_function.call_count == 2  # 2 unique pages


def test_save_pages_metadata(mocker, cleanup_pages_dir):
    """
    Verify that `save_pages_metadata` correctly saves page metadata to a JSON file.
    """
    # mock filesystem interactions
    # assume directory doesn't exist
    mocker.patch("pathlib.Path.exists", return_value=False)
    mocker.patch("pathlib.Path.mkdir")  # mock mkdir to do nothing

    # mock open
    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)

    # mock json.dump
    mock_json_dump = mocker.patch.object(json, "dump")
    pages = [
        {
            "url": "http://example.com/page1.html",
            "depth": 1,
        },
        {
            "url": "http://example.com/page2.html",
            "depth": 1,
        },
    ]
    save_pages_metadata(pages)

    # Check if open was called with the correct arguments
    expected_path = Path("pages/pages_metadata.json")
    mock_open.assert_called_once_with(expected_path, "w")

    # Check if json.dump was called with the correct arguments
    expected_data = {"pages": pages}
    mock_json_dump.assert_called_once_with(
        expected_data, mock_open.return_value, indent=4
    )
