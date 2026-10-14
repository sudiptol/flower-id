"""Talking to Pl@ntNet. All Pl@ntNet details live in this file, so app.py doesn't need to know them."""

import math
import os

import requests

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# Give up after 20 seconds instead of waiting forever (error E3 in SPEC.md).
TIMEOUT_SECONDS = 20

# Below this confidence, the page shows a warning and the top 3 candidates (SPEC.md story 6).
CONFIDENT_PERCENT = 50


def identify_with_plantnet(photo_bytes):
    """Send one JPEG or PNG photo to Pl@ntNet and return its raw response.

    Careful: Pl@ntNet wants the key inside the web address, so never print or log
    the request's URL, or an error message from requests, which can contain it.
    """
    return requests.post(
        PLANTNET_URL,
        params={
            "api-key": os.environ["PLANTNET_API_KEY"],
            "lang": "en",  # English common names
            "nb-results": 3,  # we only ever show the top 3
        },
        files={"images": ("photo.jpg", photo_bytes)},
        data={"organs": "auto"},  # let Pl@ntNet work out which part of the plant it is
        timeout=TIMEOUT_SECONDS,
    )


def to_percent(score):
    """Turn Pl@ntNet's score (0 to 1) into a whole percentage: 0.92613 -> 92.

    Always rounds down, so 0.497 shows as 49% and gets the warning, never as a
    confident-looking 50%. (Rounding to 2 decimals first removes tiny computer
    maths errors, like 0.29 * 100 = 28.999999999999996.)
    """
    return math.floor(round(score * 100, 2))


def summarise(reply):
    """Turn Pl@ntNet's long reply into just what the page needs."""
    candidates = []
    for result in reply["results"][:3]:
        species = result["species"]
        common_names = species.get("commonNames") or []
        candidates.append({
            "scientific_name": species["scientificNameWithoutAuthor"],
            "common_name": common_names[0] if common_names else None,
            "confidence": to_percent(result["score"]),
        })

    return {
        "confident": candidates[0]["confidence"] >= CONFIDENT_PERCENT,
        "candidates": candidates,
    }
