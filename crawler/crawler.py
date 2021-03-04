import queue
import sys
from pathlib import Path
from typing import Iterator
from urllib.parse import urldefrag, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def fetch_page(url: str, session: requests.Session, local_path: Path) -> bytes:
    """
    Gets an HTML page, first checking if it's already present on disk, and if not,
    fetching it via its url
    """
    # TODO: Implement using Last-Modified header if present for verifying identity
    if local_path.is_file():
        print(f"reading {url} from local path {local_path}")
        return local_path.read_bytes()
    else:
        print(f"fetching {url}")
        return session.get(url).content


def get_links(page: bytes) -> Iterator[str]:
    """
    Get all link urls from an HTML page
    """
    soup = BeautifulSoup(page, "html.parser")
    for link in soup.find_all("a"):
        yield link.get("href")


def write_page(page: bytes, path: Path):
    """
    Write a page to disk, making sure its parent folders exist
    """
    if path.is_file():
        # Don't write back files that were fetched from disk
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(page)


def file_name(link: str, start: str, out_dir: str) -> Path:
    """
    Get the local path where a page should be written
    """
    start = start.rstrip("/") + "/"
    path_and_query = link[len(start) :] or "index.html"
    parsed = urlsplit(path_and_query)
    # Escape `/` characters in the query part of the url
    quoted_path = (
        parsed.path + "?" + parsed.query.replace("/", r"%2F")
        if parsed.query
        else path_and_query
    )
    return Path(out_dir, quoted_path)


def crawl(start: str, out_dir: str):
    session = requests.Session()
    seen_links = {
        start,
    }
    to_crawl = queue.Queue()
    to_crawl.put(start)
    while True:
        try:
            current_url = to_crawl.get()
        except queue.Empty:
            break
        local_path = file_name(current_url, start, out_dir)
        page = fetch_page(current_url, session, local_path)
        for link_url in get_links(page):
            defragged_url, _ = urldefrag(link_url)
            joined_url = urljoin(start, defragged_url)
            if not joined_url.startswith(start) or joined_url in seen_links:
                continue
            seen_links.add(joined_url)
            to_crawl.put(joined_url)
        write_page(
            page,
            local_path,
        )


def main():
    start = sys.argv[1]
    # TODO: Make out_dir parameter optional
    out_dir = sys.argv[2]
    try:
        crawl(start, out_dir)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
