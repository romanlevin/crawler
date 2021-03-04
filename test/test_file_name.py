import pytest

from crawler.crawler import file_name


@pytest.mark.parametrize(
    "link,start,out_dir,expected",
    [
        ("https://example.com/foo", "https://example.com", "out", "out/foo"),
        ("https://example.com", "https://example.com", "out", "out/index.html"),
    ],
)
def test_file_name(link, start, out_dir, expected):
    assert file_name(link, start, out_dir) == expected
