import logging
import os
import queue
import sys
from typing import Iterator
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def fetch_page(url: str, session: requests.Session) -> requests.Response:
    logging.info("fetching %s", url)
    return session.get(url)


def get_links(page: str) -> Iterator[str]:
    soup = BeautifulSoup(page, "html.parser")
    for link in soup.find_all("a"):
        yield link.get("href")


def write_page(page: bytes, path: str):
    parent_dir = os.path.dirname(path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(path, "wb") as f:
        logging.info("writing %s to disk", path)
        f.write(page)


def file_name(link: str, start: str, out_dir: str) -> str:
    start = start.lstrip("/") + "/"
    return os.path.join(out_dir, link[len(start) :] or "index.html")


def crawl(start: str, out_dir: str):
    session = requests.Session()
    seen_links = {
        start,
    }
    parsed_start = urlparse(start)
    scheme = parsed_start.scheme
    netloc = parsed_start.netloc
    scheme_netloc = f"{scheme}://{netloc}"
    to_crawl = queue.Queue()
    to_crawl.put(start)
    while True:
        try:
            current_url = to_crawl.get()
        except queue.Empty:
            break
        local_path = file_name(joined_url, start, out_dir)
        page = fetch_page(current_url, session)
        for link_url in get_links(page.text):
            defragged_url, _ = urldefrag(link_url)
            joined_url = urljoin(start, defragged_url)
            if not joined_url.startswith(start):
                continue
            seen_links.add(joined_url)
            to_crawl.put(joined_url)
            write_page(
                page.content,
                local_path,
            )


def main():
    start = sys.argv[1]
    out_dir = sys.argv[2]
    crawl(start, out_dir)
