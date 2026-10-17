"""Talking to Wikipedia. All Wikipedia details live in this file, so app.py doesn't need to know them."""

import re

import requests

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Wikipedia refuses requests that don't say who is asking (403 Forbidden).
# Its rules also ask for a way to contact the owner, so the project's address is included.
USER_AGENT = "flower-id/1.0 (https://github.com/sudiptol/flower-id; personal learning project)"

# Give up after 5 seconds: the Pl@ntNet result is shown anyway (W2 in SPEC.md).
TIMEOUT_SECONDS = 5

# Where "Did you know?" facts come from, best first (SPEC.md story 5).
# Name origins are consistently the most interesting, so they come first.
FUN_SECTIONS = [
    "etymology",
    "in culture", "culture", "cultural significance", "folklore", "symbolism", "in popular culture",
    "uses", "culinary use", "culinary uses", "medicinal use", "medicinal uses",
    "cultivation", "history",
]

# Shorter than this, a section is usually just a heading for subsections.
MIN_FACT_CHARACTERS = 80


def fetch_summary(name):
    """Get a short Wikipedia summary, and a "Did you know?" fact when there is one.

    Returns one of:
      {"status": "found", "summary": "...", "url": "https://...", "fun_fact": "..." or None}
      {"status": "no_article"}    W1: Wikipedia has nothing useful for this name
      {"status": "unavailable"}   W2: Wikipedia was slow, down or sent something odd
    """
    # One request gets the whole article as plain text, plus its link and whether
    # it's a "disambiguation" page. Redirects are followed (Helianthus annuus -> Common sunflower).
    try:
        response = requests.get(
            WIKIPEDIA_API_URL,
            params={
                "action": "query",
                "titles": name,
                "redirects": 1,
                "prop": "extracts|info|pageprops",
                "explaintext": 1,
                "inprop": "url",
                "ppprop": "disambiguation",
                "format": "json",
                "formatversion": 2,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        return {"status": "unavailable"}

    if response.status_code != 200:
        return {"status": "unavailable"}

    try:
        page = response.json()["query"]["pages"][0]
    except (ValueError, KeyError, IndexError):
        return {"status": "unavailable"}

    # A missing article still answers 200, but says "missing".
    # A "disambiguation" page ("Rosa may refer to:") is no use as a summary.
    if page.get("missing") or "disambiguation" in page.get("pageprops", {}):
        return {"status": "no_article"}

    article = page.get("extract", "")
    summary = first_paragraph(article)
    if not summary:
        return {"status": "no_article"}

    article_url = page.get("fullurl")
    if not article_url:
        return {"status": "unavailable"}

    return {"status": "found", "summary": summary, "url": article_url, "fun_fact": find_fun_fact(article)}


def first_paragraph(article):
    """The article's opening paragraph: Wikipedia's own summary of the plant."""
    paragraph = article.strip().split("\n")[0].strip()
    # Plain text leaves a stray space in pronunciation guides: "( BEL-iss)" -> "(BEL-iss)"
    return re.sub(r"\(\s+", "(", paragraph)


def split_into_sections(article):
    """Plain-text articles mark headings like "== Etymology ==". Returns {heading: text}."""
    sections = {}
    parts = re.split(r"\n={2,3} (.+?) ={2,3}\n", article)
    # parts is [intro, heading, text, heading, text, ...]
    for heading, text in zip(parts[1::2], parts[2::2]):
        sections.setdefault(heading.strip().lower(), text.strip())
    return sections


def find_fun_fact(article):
    """The first two sentences of the best fun section, or None if there isn't one."""
    sections = split_into_sections(article)
    for heading in FUN_SECTIONS:
        text = sections.get(heading, "")
        if len(text) >= MIN_FACT_CHARACTERS:
            return " ".join(split_into_sentences(text)[:2])
    return None


def split_into_sentences(text):
    """Split after ". ", "! " or "? ", but not after a one-letter abbreviation like "T. erecta"."""
    text = " ".join(text.split())  # one line, single spaces
    sentences = []
    start = 0
    for match in re.finditer(r"[.!?] ", text):
        end = match.start() + 1
        is_initial = end >= 2 and text[end - 2].isupper() and (end == 2 or text[end - 3] == " ")
        if not is_initial:
            sentences.append(text[start:end])
            start = match.end()
    sentences.append(text[start:])
    return [s for s in sentences if s]
