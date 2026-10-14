"""Automated checks for wikipedia.py, using a fake Wikipedia (works offline, same result every time)."""

import pytest
import requests

from wikipedia import TIMEOUT_SECONDS, fetch_summary, find_fun_fact, split_into_sentences

DAISY_ARTICLE = (
    "Bellis perennis ( BEL-iss), the daisy, is a European species of the family Asteraceae.\n"
    "A second intro paragraph that the summary should leave out.\n\n"
    "== Description ==\n"
    "Leaves, stems and flower heads, described in botanical detail for anyone who wants it.\n\n"
    "== Uses ==\n"
    "The young leaves can be eaten raw in salads or cooked, and the flower buds can be pickled like capers.\n\n"
    "== Etymology ==\n"
    'Bellis may come from bellus, Latin for "pretty". The name "daisy" is a corruption of "day\'s eye". '
    "A third sentence that should be left out.\n"
)


def make_page(**fields):
    """A Wikipedia reply for one page, in the shape the real API sends."""
    page = {
        "title": "Bellis perennis",
        "extract": DAISY_ARTICLE,
        "fullurl": "https://en.wikipedia.org/wiki/Bellis_perennis",
    }
    page.update(fields)
    return {"query": {"pages": [page]}}


class FakeWikipediaResponse:
    def __init__(self, status_code, reply=None, is_json=True):
        self.status_code = status_code
        self.reply = reply
        self.is_json = is_json

    def json(self):
        if not self.is_json:
            raise ValueError("not JSON")
        return self.reply


@pytest.fixture
def requests_made(monkeypatch):
    """Records every request wikipedia.py makes. Set .answer to choose the fake reply."""
    class Recorder:
        answer = FakeWikipediaResponse(200, make_page())
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

def test_returns_summary_link_and_fun_fact(requests_made):
    result = fetch_summary("Bellis perennis")
    assert result == {
        "status": "found",
        # Only the first paragraph, with the pronunciation's stray space tidied
        "summary": "Bellis perennis (BEL-iss), the daisy, is a European species of the family Asteraceae.",
        "url": "https://en.wikipedia.org/wiki/Bellis_perennis",
        # Etymology wins over Uses, even though Uses comes first in the article; two sentences only
        "fun_fact": 'Bellis may come from bellus, Latin for "pretty". The name "daisy" is a corruption of "day\'s eye".',
    }


def test_uses_wikipedias_own_link_after_a_redirect(requests_made):
    requests_made.answer = FakeWikipediaResponse(200, make_page(
        title="Common sunflower", fullurl="https://en.wikipedia.org/wiki/Common_sunflower"))
    assert fetch_summary("Helianthus annuus")["url"] == "https://en.wikipedia.org/wiki/Common_sunflower"


def test_one_polite_request_with_a_time_limit(requests_made):
    fetch_summary("Iris × hollandica")
    assert len(requests_made.calls) == 1  # summary and fun fact come from the same request
    request = requests_made.calls[0]
    assert "flower-id" in request["headers"]["User-Agent"]  # otherwise Wikipedia answers 403
    assert request["timeout"] == TIMEOUT_SECONDS == 5
    assert request["params"]["titles"] == "Iris × hollandica"  # requests encodes the "×" itself
    assert request["params"]["redirects"] == 1


# --- "Did you know?" facts ---

def test_no_fun_section_means_no_fun_fact(requests_made):
    plain = "Chrysanthemum × morifolium is a hybrid species.\n\n== Description ==\nBotanical detail only.\n"
    requests_made.answer = FakeWikipediaResponse(200, make_page(extract=plain))
    result = fetch_summary("Chrysanthemum × morifolium")
    assert result["status"] == "found"
    assert result["fun_fact"] is None


def test_too_short_section_is_skipped_for_the_next_one():
    article = (
        "Intro.\n\n== Etymology ==\nSee below.\n\n"
        "== Uses ==\nThe flowers are used to make a bright yellow dye for wool, and the leaves are made into tea.\n"
    )
    assert find_fun_fact(article).startswith("The flowers are used")


def test_one_letter_abbreviations_dont_end_a_sentence():
    text = "It was used by the Mexica of T. erecta fame. It is still grown today. A third one."
    assert split_into_sentences(text) == [
        "It was used by the Mexica of T. erecta fame.",
        "It is still grown today.",
        "A third one.",
    ]


# --- No article (W1) ---

def test_missing_article(requests_made):
    # The real API answers 200 for a missing page, with "missing": true.
    requests_made.answer = FakeWikipediaResponse(200, make_page(missing=True, extract=""))
    assert fetch_summary("Notarealplant fakeus") == {"status": "no_article"}


def test_disambiguation_page_counts_as_no_article(requests_made):
    requests_made.answer = FakeWikipediaResponse(200, make_page(
        extract="Rosa or De Rosa may refer to:", pageprops={"disambiguation": ""}))
    assert fetch_summary("Rosa") == {"status": "no_article"}


def test_empty_article_counts_as_no_article(requests_made):
    requests_made.answer = FakeWikipediaResponse(200, make_page(extract=""))
    assert fetch_summary("Bellis perennis") == {"status": "no_article"}


# --- Couldn't load (W2) ---

@pytest.mark.parametrize("problem", [
    requests.Timeout(),                               # slower than 5 seconds
    requests.ConnectionError(),                       # no connection
    FakeWikipediaResponse(503, {}),                   # Wikipedia down
    FakeWikipediaResponse(200, is_json=False),        # garbled reply
    FakeWikipediaResponse(200, {"unexpected": True}), # reply in an unexpected shape
    FakeWikipediaResponse(200, make_page(fullurl=None)),  # no article link
])
def test_problems_mean_unavailable(requests_made, problem):
    requests_made.answer = problem
    assert fetch_summary("Bellis perennis") == {"status": "unavailable"}
