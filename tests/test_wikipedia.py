"""Automated checks for wikipedia.py, using a fake Wikipedia (works offline, same result every time)."""

import pytest
import requests

from wikipedia import TIMEOUT_SECONDS, fetch_summary

SUNFLOWER_PAGE = {
    "type": "standard",
    "title": "Common sunflower",
    "extract": "The common sunflower is a species of large annual forb of the daisy family.",
    "content_urls": {"mobile": {"page": "https://en.m.wikipedia.org/wiki/Common_sunflower"}},
}


class FakeWikipediaResponse:
    def __init__(self, status_code, page=None, is_json=True):
        self.status_code = status_code
        self.page = page
        self.is_json = is_json

    def json(self):
        if not self.is_json:
            raise ValueError("not JSON")
        return self.page


@pytest.fixture
def requests_made(monkeypatch):
    """Records every request wikipedia.py makes. Set .answer to choose the fake reply."""
    class Recorder:
        answer = FakeWikipediaResponse(200, SUNFLOWER_PAGE)
        calls = []

    def fake_get(address, **options):
        Recorder.calls.append({"address": address, **options})
        if isinstance(Recorder.answer, Exception):
            raise Recorder.answer
        return Recorder.answer

    Recorder.calls = []
    monkeypatch.setattr("wikipedia.requests.get", fake_get)
    return Recorder


# --- Found ---

def test_returns_summary_and_link(requests_made):
    result = fetch_summary("Helianthus annuus")
    assert result == {
        "status": "found",
        "summary": "The common sunflower is a species of large annual forb of the daisy family.",
        # Wikipedia's own link, not one built from the name we asked for (it redirected).
        "url": "https://en.m.wikipedia.org/wiki/Common_sunflower",
    }


def test_asks_politely_and_with_a_time_limit(requests_made):
    fetch_summary("Bellis perennis")
    request = requests_made.calls[0]
    assert "flower-id" in request["headers"]["User-Agent"]  # otherwise Wikipedia answers 403
    assert request["timeout"] == TIMEOUT_SECONDS == 5


def test_name_with_spaces_and_hybrid_sign_is_encoded(requests_made):
    fetch_summary("Iris × hollandica")
    assert requests_made.calls[0]["address"].endswith("/page/summary/Iris_%C3%97_hollandica")


# --- No article (W1) ---

def test_missing_article(requests_made):
    requests_made.answer = FakeWikipediaResponse(404, {"type": "Internal error"})
    assert fetch_summary("Notarealplant fakeus") == {"status": "no_article"}


def test_disambiguation_page_counts_as_no_article(requests_made):
    requests_made.answer = FakeWikipediaResponse(200, {
        "type": "disambiguation",
        "extract": "Rosa or De Rosa may refer to:",
        "content_urls": {"mobile": {"page": "https://en.m.wikipedia.org/wiki/Rosa"}},
    })
    assert fetch_summary("Rosa") == {"status": "no_article"}


def test_empty_summary_counts_as_no_article(requests_made):
    requests_made.answer = FakeWikipediaResponse(200, {**SUNFLOWER_PAGE, "extract": ""})
    assert fetch_summary("Helianthus annuus") == {"status": "no_article"}


# --- Couldn't load (W2) ---

@pytest.mark.parametrize("problem", [
    requests.Timeout(),                        # slower than 5 seconds
    requests.ConnectionError(),                # no connection
    FakeWikipediaResponse(503, {}),            # Wikipedia down
    FakeWikipediaResponse(200, is_json=False), # garbled reply
    FakeWikipediaResponse(200, {**SUNFLOWER_PAGE, "content_urls": {}}),  # no article link
])
def test_problems_mean_unavailable(requests_made, problem):
    requests_made.answer = problem
    assert fetch_summary("Helianthus annuus") == {"status": "unavailable"}
