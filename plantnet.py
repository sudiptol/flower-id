"""Talking to Pl@ntNet. All Pl@ntNet details live in this file, so app.py doesn't need to know them."""

import os

import requests

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

# Give up after 20 seconds instead of waiting forever (error E3 in SPEC.md).
TIMEOUT_SECONDS = 20


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
