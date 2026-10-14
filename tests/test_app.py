"""Automated checks for app.py. Run them all with:  python -m pytest"""

import io

import pytest

from app import MAX_PHOTO_BYTES, app

# The first bytes of each format are all the server looks at, so these short fakes are enough.
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
HEIC_BYTES = b"\x00\x00\x00\x20ftypheic" + b"\x00" * 100


@pytest.fixture
def client():
    """A pretend browser that talks to the app without starting a real server."""
    return app.test_client()


def upload(client, data, filename="photo.jpg"):
    """Send a file to /identify the same way the page does."""
    return client.post("/identify", data={"photo": (io.BytesIO(data), filename)})


# --- The page ---

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Take a photo" in response.get_data(as_text=True)


# --- Real images are accepted ---

def test_accepts_jpeg(client):
    response = upload(client, JPEG_BYTES, "flower.jpg")
    assert response.status_code == 200
    assert response.get_json()["size_bytes"] == len(JPEG_BYTES)


def test_accepts_png(client):
    response = upload(client, PNG_BYTES, "flower.png")
    assert response.status_code == 200


def test_accepts_photo_just_under_the_limit(client):
    almost_too_big = JPEG_BYTES + b"\x00" * (MAX_PHOTO_BYTES - 100_000)
    response = upload(client, almost_too_big)
    assert response.status_code == 200


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
