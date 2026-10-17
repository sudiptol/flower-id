"""Automated checks for app.py. Run them all with:  python -m pytest"""

import io
import logging

import pytest
import requests

from app import (
    E3_TOO_SLOW,
    E4_NO_FLOWER,
    E5_DAILY_LIMIT,
    E6_BAD_KEY,
    E7_PLANTNET_DOWN,
    E8_UNEXPECTED,
    E11_WRONG_PASSCODE,
    MAX_PHOTO_BYTES,
    app,
)

TEST_PASSCODE = "correct horse battery staple"

# The first bytes of each format are all the server looks at, so these short fakes are enough.
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
HEIC_BYTES = b"\x00\x00\x00\x20ftypheic" + b"\x00" * 100

# A shortened copy of a real Pl@ntNet reply (the mixed bouquet from step 4c).
BOUQUET_REPLY = {
    "results": [
        {"score": 0.02573, "species": {"scientificNameWithoutAuthor": "Eustoma russellianum",
                                       "commonNames": ["Lisianthus", "Bluebell"]}},
        {"score": 0.01621, "species": {"scientificNameWithoutAuthor": "Iris × hollandica",
                                       "commonNames": ["Dutch Iris"]}},
        {"score": 0.00846, "species": {"scientificNameWithoutAuthor": "Veronica spuria",
                                       "commonNames": ["Bastard speedwell"]}},
    ],
    "remainingIdentificationRequests": 498,
}


MARIGOLD_WIKIPEDIA = {
    "status": "found",
    "summary": "Tagetes erecta, the Aztec marigold, is a species of flowering plant.",
    "url": "https://en.wikipedia.org/wiki/Tagetes_erecta",
}


class FakePlantNetResponse:
    """Stands in for a real reply from Pl@ntNet, so tests use no quota and work offline."""

    def __init__(self, status_code, reply):
        self.status_code = status_code
        self.reply = reply

    def json(self):
        return self.reply


@pytest.fixture
def locked_client(monkeypatch):
    """A pretend browser that talks to the app without starting a real server, not yet unlocked.

    Pl@ntNet is replaced by a fake that always answers with the bouquet reply,
    and Wikipedia by a fake that always finds the marigold article.
    Wrong passcodes don't really wait, so the tests stay fast; the waits are recorded instead.
    """
    monkeypatch.setenv("PLANTNET_API_KEY", "fake-key-for-tests")
    monkeypatch.setenv("APP_PASSCODE", TEST_PASSCODE)
    monkeypatch.setattr(app, "secret_key", "test-secret-key")
    monkeypatch.setattr("app.identify_with_plantnet", lambda photo_bytes: FakePlantNetResponse(200, BOUQUET_REPLY))
    monkeypatch.setattr("app.fetch_summary", lambda name: MARIGOLD_WIKIPEDIA)
    waits = []
    monkeypatch.setattr("app.time.sleep", waits.append)
    test_client = app.test_client()
    test_client.waits = waits
    return test_client


@pytest.fixture
def client(locked_client):
    """The same pretend browser, after entering the right passcode."""
    locked_client.post("/unlock", data={"passcode": TEST_PASSCODE})
    return locked_client


def upload(client, data, filename="photo.jpg"):
    """Send a file to /identify the same way the page does."""
    return client.post("/identify", data={"photo": (io.BytesIO(data), filename)})


# --- Safe to put online ---

def test_debug_mode_is_off_when_loaded_like_a_web_server_does():
    # The web server online imports the app, just as this test file does. Debug mode online
    # would show code details to anyone, so it must only ever be on with "python app.py".
    assert app.debug is False


def test_passcode_cookie_is_https_only_when_loaded_like_a_web_server_does(locked_client):
    # Online, the "unlocked" cookie must never travel over plain http, where others could copy it.
    response = locked_client.post("/unlock", data={"passcode": TEST_PASSCODE})
    assert "Secure" in response.headers["Set-Cookie"]


def test_info_log_lines_are_shown_even_without_debug_mode():
    # Online, the log is the only way to see what happened ("Received photo", the candidates...).
    assert app.logger.isEnabledFor(logging.INFO)


# --- The passcode lock (SPEC.md story 9 and error E11) ---

def test_locked_page_shows_only_the_passcode_box(locked_client):
    page = locked_client.get("/").get_data(as_text=True)
    assert '<section id="locked">' in page
    assert '<section id="start" hidden>' in page


def test_unlocked_page_starts_on_the_photo_buttons(client):
    page = client.get("/").get_data(as_text=True)
    assert '<section id="locked" hidden>' in page
    assert '<section id="start">' in page


def test_server_refuses_photos_without_the_passcode(locked_client, monkeypatch):
    monkeypatch.setattr("app.identify_with_plantnet", lambda photo_bytes: pytest.fail("Pl@ntNet must not be called"))
    response = upload(locked_client, JPEG_BYTES)
    assert response.status_code == 401
    assert response.get_json()["locked"] is True


def test_wrong_passcode_is_refused_and_slowed_down(locked_client):
    response = locked_client.post("/unlock", data={"passcode": "wrong guess"})
    assert response.status_code == 401
    assert response.get_json()["error"] == E11_WRONG_PASSCODE
    assert locked_client.waits == [1]  # made to wait a second
    assert upload(locked_client, JPEG_BYTES).status_code == 401  # still locked


def test_right_passcode_unlocks_and_is_remembered_for_a_year(locked_client):
    response = locked_client.post("/unlock", data={"passcode": TEST_PASSCODE})
    assert response.get_json() == {"unlocked": True}
    assert locked_client.waits == []  # no waiting for the right passcode
    cookie = response.headers["Set-Cookie"]
    assert "Expires=" in cookie  # kept after closing the browser, not just for this visit
    assert "HttpOnly" in cookie  # the page's own JavaScript can't read or steal it
    assert upload(locked_client, JPEG_BYTES).status_code == 200


def test_no_passcode_set_up_means_nobody_gets_in(locked_client, monkeypatch):
    # Fail closed: a missing APP_PASSCODE must never mean "no lock".
    monkeypatch.delenv("APP_PASSCODE")
    for attempt in ["", "anything"]:
        assert locked_client.post("/unlock", data={"passcode": attempt}).status_code == 401


def test_no_secret_key_set_up_fails_clearly(locked_client, monkeypatch, caplog):
    # Without SECRET_KEY the cookie can't be signed. Nobody gets in, and the log says why.
    monkeypatch.setattr(app, "secret_key", None)
    response = locked_client.post("/unlock", data={"passcode": TEST_PASSCODE})
    assert response.status_code == 500
    assert response.get_json()["error"] == E8_UNEXPECTED  # a friendly message, not a crash page
    assert "SECRET_KEY is missing" in caplog.text


def test_a_forged_cookie_is_not_accepted(locked_client):
    # A cookie signed with a different secret key, as an attacker would have to make
    forger = app.test_client()
    real_key = app.secret_key
    app.secret_key = "attackers-guess-at-the-key"
    with forger.session_transaction() as fake_session:
        fake_session["unlocked"] = True
    app.secret_key = real_key
    assert upload(forger, JPEG_BYTES).status_code == 401


# --- The page ---

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Take a photo" in response.get_data(as_text=True)


def test_result_shows_the_plantnet_line_above_the_name_and_no_red_warning(client):
    # Changed on 2026-10-17 (SPEC.md stories 4 and 6): the confidence line sits where the red box was.
    page = client.get("/").get_data(as_text=True)
    assert page.index("Identified by Pl@ntNet") < page.index('id="best-guess-label"') < page.index('id="main-name"')
    assert "Not sure about this one" not in page

def test_home_screen_icon_is_a_png_even_when_locked(locked_client):
    # Safari asks for the icons before anyone has typed the passcode.
    response = locked_client.get("/apple-touch-icon.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(b"\x89PNG\r\n\x1a\n")


def test_browser_tab_icon_is_an_ico_even_when_locked(locked_client):
    response = locked_client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.data.startswith(b"\x00\x00\x01\x00")  # every .ico file starts like this


def test_page_links_to_both_icons(locked_client):
    page = locked_client.get("/").get_data(as_text=True)
    assert '<link rel="icon" href="/favicon.ico">' in page
    assert '<link rel="apple-touch-icon" href="/apple-touch-icon.png">' in page


# --- Real images are accepted and identified ---

def test_accepts_jpeg(client):
    response = upload(client, JPEG_BYTES, "flower.jpg")
    assert response.status_code == 200


def test_accepts_png(client):
    response = upload(client, PNG_BYTES, "flower.png")
    assert response.status_code == 200


def test_accepts_photo_just_under_the_limit(client):
    almost_too_big = JPEG_BYTES + b"\x00" * (MAX_PHOTO_BYTES - 100_000)
    response = upload(client, almost_too_big)
    assert response.status_code == 200


def test_returns_top_3_candidates_from_plantnet(client):
    reply = upload(client, JPEG_BYTES).get_json()
    assert reply["candidates"] == [
        {"scientific_name": "Eustoma russellianum", "common_name": "Lisianthus", "confidence": 2},
        {"scientific_name": "Iris × hollandica", "common_name": "Dutch Iris", "confidence": 1},
        {"scientific_name": "Veronica spuria", "common_name": "Bastard speedwell", "confidence": 0},
    ]
    assert reply["confident"] is False


# --- The Wikipedia part (SPEC.md story 5, errors W1 and W2) ---

def test_wikipedia_is_looked_up_for_the_best_guess_only(client, monkeypatch):
    names_looked_up = []
    monkeypatch.setattr("app.fetch_summary", lambda name: names_looked_up.append(name) or MARIGOLD_WIKIPEDIA)

    reply = upload(client, JPEG_BYTES).get_json()

    assert names_looked_up == ["Eustoma russellianum"]  # the bouquet's best guess
    assert reply["wikipedia"] == MARIGOLD_WIKIPEDIA


@pytest.mark.parametrize("wikipedia_problem", ["no_article", "unavailable"])
def test_plantnet_result_still_shown_when_wikipedia_has_a_problem(client, monkeypatch, wikipedia_problem):
    monkeypatch.setattr("app.fetch_summary", lambda name: {"status": wikipedia_problem})

    response = upload(client, JPEG_BYTES)

    assert response.status_code == 200
    reply = response.get_json()
    assert reply["candidates"][0]["scientific_name"] == "Eustoma russellianum"
    assert reply["wikipedia"] == {"status": wikipedia_problem}


def test_wikipedia_not_asked_when_plantnet_fails(client, monkeypatch):
    make_plantnet_reply_with(monkeypatch, 404, {"message": "Species not found"})
    monkeypatch.setattr("app.fetch_summary", lambda name: pytest.fail("Wikipedia should not be asked"))
    upload(client, JPEG_BYTES)


# --- Everything else is refused (SPEC.md errors E1, E9 and E10) ---

def test_refuses_heic_with_its_own_message(client):
    # Pl@ntNet only accepts JPEG and PNG.
    response = upload(client, HEIC_BYTES, "flower.heic")
    assert response.status_code == 400
    assert response.get_json()["error"] == "HEIC photos can't be identified yet. Please use a JPG or PNG."


def test_refuses_text_disguised_as_jpeg(client):
    response = upload(client, b"just some text", "sneaky.jpg")
    assert response.status_code == 400
    assert response.get_json()["error"] == "That file isn't a photo. Please choose a JPG or PNG image."


def test_refuses_pdf(client):
    response = upload(client, b"%PDF-1.4 some document", "notes.pdf")
    assert response.status_code == 400


def test_refuses_empty_file(client):
    response = upload(client, b"", "empty.jpg")
    assert response.status_code == 400


def test_refuses_photo_over_the_limit(client):
    too_big = JPEG_BYTES + b"\x00" * MAX_PHOTO_BYTES
    response = upload(client, too_big)
    assert response.status_code == 413
    assert response.get_json()["error"] == "That photo is too large (over 10 MB). Please choose a smaller one."


def test_refuses_request_without_photo(client):
    response = client.post("/identify")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No photo was sent."


def test_identify_only_accepts_uploads(client):
    response = client.get("/identify")
    assert response.status_code == 405


# --- Every Pl@ntNet problem becomes the right message (SPEC.md errors E3-E8) ---

def make_plantnet_reply_with(monkeypatch, status_code, reply=None):
    """Make the fake Pl@ntNet answer with this status code."""
    monkeypatch.setattr("app.identify_with_plantnet", lambda photo_bytes: FakePlantNetResponse(status_code, reply))


def make_plantnet_fail_with(monkeypatch, error):
    """Make the fake Pl@ntNet fail before answering, like a timeout or a dropped connection."""
    def fail(photo_bytes):
        raise error
    monkeypatch.setattr("app.identify_with_plantnet", fail)


# Each line: what Pl@ntNet answers -> the message we must show, and whether Try again makes sense.
@pytest.mark.parametrize("plantnet_status, expected_message, expected_can_retry", [
    (404, E4_NO_FLOWER,     False),  # no plant in the photo: same photo, same answer
    (429, E5_DAILY_LIMIT,   False),  # 500 used today: won't change until tomorrow
    (401, E6_BAD_KEY,       False),  # wrong key: needs fixing in .env
    (403, E6_BAD_KEY,       False),  # key not allowed
    (500, E7_PLANTNET_DOWN, True),   # Pl@ntNet crashed: may recover
    (503, E7_PLANTNET_DOWN, True),   # Pl@ntNet down for maintenance
    (400, E8_UNEXPECTED,    True),   # something we didn't plan for: worth one more go
])
def test_plantnet_errors_become_friendly_messages(
        client, monkeypatch, plantnet_status, expected_message, expected_can_retry):
    make_plantnet_reply_with(monkeypatch, plantnet_status, {"message": "whatever Pl@ntNet says"})
    response = upload(client, JPEG_BYTES)
    assert response.status_code >= 400
    assert response.get_json() == {"error": expected_message, "can_retry": expected_can_retry}


def test_plantnet_ok_but_no_results_means_no_flower(client, monkeypatch):
    make_plantnet_reply_with(monkeypatch, 200, {"results": []})
    response = upload(client, JPEG_BYTES)
    assert response.get_json() == {"error": E4_NO_FLOWER, "can_retry": False}


def test_plantnet_too_slow(client, monkeypatch):
    make_plantnet_fail_with(monkeypatch, requests.Timeout())
    response = upload(client, JPEG_BYTES)
    assert response.get_json() == {"error": E3_TOO_SLOW, "can_retry": True}


def test_plantnet_unreachable(client, monkeypatch):
    make_plantnet_fail_with(monkeypatch, requests.ConnectionError())
    response = upload(client, JPEG_BYTES)
    assert response.get_json() == {"error": E7_PLANTNET_DOWN, "can_retry": True}


def test_missing_key_is_reported_without_calling_plantnet(client, monkeypatch):
    monkeypatch.delenv("PLANTNET_API_KEY")
    make_plantnet_fail_with(monkeypatch, AssertionError("Pl@ntNet must not be called without a key"))
    response = upload(client, JPEG_BYTES)
    assert response.get_json() == {"error": E6_BAD_KEY, "can_retry": False}


# --- File problems never offer Try again: the same file would fail the same way ---

@pytest.mark.parametrize("photo_bytes", [
    HEIC_BYTES,                           # E10
    b"just some text",                    # E1
    JPEG_BYTES + b"\x00" * MAX_PHOTO_BYTES,  # E9, too big
])
def test_file_problems_cannot_be_retried(client, photo_bytes):
    assert upload(client, photo_bytes).get_json()["can_retry"] is False


# --- The key never leaks (SPEC.md acceptance criterion 7) ---

def test_key_never_appears_in_logs_or_reply(client, monkeypatch, caplog):
    secret = "super-secret-test-key-123"
    monkeypatch.setenv("PLANTNET_API_KEY", secret)
    # A real requests error contains the full web address, which includes the key.
    leaky_error = requests.ConnectionError(
        f"Max retries exceeded with url: /v2/identify/all?api-key={secret}&lang=en"
    )
    make_plantnet_fail_with(monkeypatch, leaky_error)

    caplog.set_level(logging.DEBUG)
    response = upload(client, JPEG_BYTES)

    assert "Couldn't reach Pl@ntNet" in caplog.text  # something useful was logged...
    assert secret not in caplog.text                  # ...but never the key
    assert secret not in response.get_data(as_text=True)
