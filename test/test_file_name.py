import pytest

from crawler.crawler import file_name


@pytest.mark.parametrize(
    "link,start,out_dir,expected",
    [
        ("https://example.com/foo", "https://example.com", "out", "out/foo"),
        ("https://example.com", "https://example.com", "out", "out/index.html"),
        (
            "https://news.ycombinator.com/news",
            "https://news.ycombinator.com/",
            "out",
            "out/news",
        ),
        (
            "https://example.com/from?site=some/website&something",
            "https://example.com",
            "out",
            r"out/from?site=some%2Fwebsite&something",
        ),
    ],
)
def test_file_name(link, start, out_dir, expected):
    assert str(file_name(link, start, out_dir)) == expected
