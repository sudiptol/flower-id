"""Talking to Wikipedia. All Wikipedia details live in this file, so app.py doesn't need to know them."""

from urllib.parse import quote

import requests

WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# Wikipedia refuses requests that don't say who is asking (403 Forbidden).
USER_AGENT = "flower-id-learning-project/0.1 (personal learning app)"

# Give up after 5 seconds: the Pl@ntNet result is shown anyway (W2 in SPEC.md).
TIMEOUT_SECONDS = 5


def fetch_summary(name):
    """Get a short Wikipedia summary for a plant name.

    Returns one of:
      {"status": "found", "summary": "...", "url": "https://..."}
      {"status": "no_article"}    W1: Wikipedia has nothing useful for this name
      {"status": "unavailable"}   W2: Wikipedia was slow, down or sent something odd
    """
    # "Iris × hollandica" -> "Iris_%C3%97_hollandica"
    address = WIKIPEDIA_SUMMARY_URL + quote(name.replace(" ", "_"), safe="")

    try:
        response = requests.get(address, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
    except requests.RequestException:
        return {"status": "unavailable"}

    if response.status_code == 404:
        return {"status": "no_article"}
    if response.status_code != 200:
        return {"status": "unavailable"}

    try:
        page = response.json()
    except ValueError:
        return {"status": "unavailable"}

    # A "disambiguation" page ("Rosa may refer to:") succeeds, but is no use as a summary.
    if page.get("type") == "disambiguation" or not page.get("extract"):
        return {"status": "no_article"}

    # Use Wikipedia's own link: names can redirect to a differently titled article
    # (Helianthus annuus -> Common sunflower).
    article_url = page.get("content_urls", {}).get("mobile", {}).get("page")
    if not article_url:
        return {"status": "unavailable"}

    return {"status": "found", "summary": page["extract"], "url": article_url}
