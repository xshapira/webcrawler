# Web Crawler

Crawl a website and save pages up to a specified depth.

## Usage

```bash
poetry install
poetry run python crawl.py <start_url> <depth>

```

- `start_url` - The URL to start crawling from
- `depth` - The maximum depth of links to follow

For example:

```bash
poetry run python crawl.py "https://docs.djangoproject.com/en/5.0/" 1
```

This will start crawling from Django docs (<https://docs.djangoproject.com/en/5.0/>), following links up to a depth of 1 page, and saving the HTML content of the pages found along the way

Downloaded pages and a JSON file listing all pages will be saved to the `pages/` directory.

## Output

The script generates `pages_metadata.json` file with metadata about all saved pages in the following format:

```json
{
  "pages": [
    {
      "url": "https://www.djangoproject.com/",
      "page": "https://docs.djangoproject.com/en/5.0/",
      "depth": 1
    },
    {
      "url": "https://www.djangoproject.com/start/overview/",
      "page": "https://docs.djangoproject.com/en/5.0/",
      "depth": 1
    },
    {
      "url": "https://www.djangoproject.com/download/",
      "page": "https://docs.djangoproject.com/en/5.0/",
      "depth": 1
    },
    {
      "url": "https://docs.djangoproject.com/",
      "page": "https://docs.djangoproject.com/en/5.0/",
      "depth": 1
    },
    {
      "url": "https://www.djangoproject.com/weblog/",
      "page": "https://docs.djangoproject.com/en/5.0/",
      "depth": 1
    }
  ]
}


```

It also saves the HTML content of each page to individual files in the `pages/` directory, named by their URL filename with the `.html` extension.

## Testing

To run the included tests:

```bash
pytest -vv
```

## How `max_depth` and `current_depth` work in page crawling

We use two key parameters to control how deep we go into a website to save pages:

- `max_depth`: Determines how far we can go from the starting page to find pages. If `max_depth` is set to 1, we will only save pages from the starting page. If it is set to 2, we will also save pages from any page directly linked to it, and so on.
- `current_depth`: Keeps track of how deep we are within the website's structure. It begins at 1 on the starting page and increases as we extract links from the HTML content and add them to the queue.
