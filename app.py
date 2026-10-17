import hmac
import logging
import os
import time
from datetime import timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory, session

from plantnet import identify_with_plantnet, summarise
from wikipedia import fetch_summary

# Read secrets such as PLANTNET_API_KEY from the .env file next to this one (never saved in git).
# The exact path matters online, where the web server starts in a different folder.
load_dotenv(Path(__file__).parent / ".env")

# Largest photo the server accepts (10 MB). The same limit is in static/app.js.
MAX_PHOTO_BYTES = 10 * 1024 * 1024

# HEIC files say "ftyp" at byte 4, followed by one of these "brand" names.
HEIC_BRANDS = [b"heic", b"heix", b"mif1"]

# Messages from SPEC.md section 5, by error number.
E1_NOT_A_PHOTO = "That file isn't a photo. Please choose a JPG or PNG image."
E3_TOO_SLOW = "Identification is taking too long. Please try again."
E4_NO_FLOWER = "No flower recognised. Try a closer, sharper photo with the flower filling the frame."
E5_DAILY_LIMIT = "Daily limit reached. Identification will work again tomorrow."
E6_BAD_KEY = "Setup problem: the Pl@ntNet key isn't working. Check the .env file."
E7_PLANTNET_DOWN = "Pl@ntNet isn't responding right now. Try again in a few minutes."
E8_UNEXPECTED = "Something went wrong. Please try again."
E9_TOO_LARGE = "That photo is too large (over 10 MB). Please choose a smaller one."
E10_HEIC = "HEIC photos can't be identified yet. Please use a JPG or PNG."
E11_WRONG_PASSCODE = "That passcode isn't right. Please try again."

# How long a wrong passcode makes you wait, so guessing thousands of passcodes is impractical.
WRONG_PASSCODE_DELAY_SECONDS = 1

app = Flask(__name__)
# Show our INFO lines ("Received photo", the Pl@ntNet candidates...) in the log online too.
# Without this, they only appear in debug mode on the Mac, and online the log would be silent.
app.logger.setLevel(logging.INFO)
# Flask refuses anything bigger before our code even runs (error 413, handled below).
app.config["MAX_CONTENT_LENGTH"] = MAX_PHOTO_BYTES

# The passcode lock (SPEC.md story 9). After the right passcode, the browser keeps a cookie
# that the server signs with SECRET_KEY, so it can't be forged. It lasts about a year.
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
# Only send the cookie over https, never plain http. Safe by default on any host;
# "python app.py" on the Mac turns this off at the bottom, because home Wi-Fi uses plain http.
app.config["SESSION_COOKIE_SECURE"] = True


def passcode_is_right(attempt):
    """Compare in constant time, so the time taken doesn't reveal how much of a guess was right."""
    real_passcode = os.environ.get("APP_PASSCODE", "")
    if not real_passcode:
        # Fail closed: with no passcode set up, nobody gets in.
        app.logger.error("APP_PASSCODE is missing. Is it in the .env file?")
        return False
    return hmac.compare_digest(attempt.encode(), real_passcode.encode())


def is_unlocked():
    return session.get("unlocked") is True


def is_jpeg_or_png(data):
    """Check the file's first bytes, because the label the sender gives can be wrong."""
    if data.startswith(b"\xff\xd8\xff"):
        return True  # JPEG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True  # PNG
    return False


def is_heic(data):
    return data[4:8] == b"ftyp" and data[8:12] in HEIC_BRANDS


@app.route("/")
def home():
    # The page starts on the passcode box or on the photo buttons.
    return render_template("index.html", unlocked=is_unlocked())


# The app icons (made by scripts/make_icons.py). Browsers ask for them at these exact addresses,
# not under /static/. No passcode needed: they're the same for everyone and show nothing private.
@app.route("/apple-touch-icon.png")
def home_screen_icon():
    return send_from_directory(app.static_folder, "apple-touch-icon.png")


@app.route("/favicon.ico")
def browser_tab_icon():
    return send_from_directory(app.static_folder, "favicon.ico")


@app.route("/unlock", methods=["POST"])
def unlock():
    if not app.secret_key:
        # Fail closed, but clearly: without it the "remembered" cookie can't be signed.
        app.logger.error("SECRET_KEY is missing. Is it in the .env file?")
        return error_reply(E8_UNEXPECTED, 500)

    if passcode_is_right(request.form.get("passcode", "")):
        session["unlocked"] = True
        session.permanent = True  # keep the cookie for PERMANENT_SESSION_LIFETIME, not just this visit
        return jsonify(unlocked=True)

    app.logger.warning("Wrong passcode entered")
    time.sleep(WRONG_PASSCODE_DELAY_SECONDS)
    return error_reply(E11_WRONG_PASSCODE, 401)


def error_reply(message, status_code, can_retry=False):
    """An error for the page: the message to show, and whether a Try again button makes sense.

    can_retry is only True when sending the same photo again might work
    (SPEC.md section 5): not for file problems, "no flower", the daily limit or a bad key.
    """
    return jsonify(error=message, can_retry=can_retry), status_code


@app.route("/identify", methods=["POST"])
def identify():
    # Checked here on the server, not just in the page: anyone could skip the page
    # and send photos straight here, using up my 500 identifications a day.
    if not is_unlocked():
        return jsonify(error="Please enter the passcode.", can_retry=False, locked=True), 401

    # The browser sends the photo as a form field named "photo".
    photo = request.files.get("photo")
    if photo is None:
        return error_reply("No photo was sent.", 400)

    photo_bytes = photo.read()
    app.logger.info("Received photo: %d KB", len(photo_bytes) // 1024)

    if is_heic(photo_bytes):
        # Pl@ntNet only accepts JPEG and PNG. The page converts photos when it can.
        return error_reply(E10_HEIC, 400)

    if not is_jpeg_or_png(photo_bytes):
        return error_reply(E1_NOT_A_PHOTO, 400)

    if not os.environ.get("PLANTNET_API_KEY"):
        app.logger.error("PLANTNET_API_KEY is missing. Is it in the .env file?")
        return error_reply(E6_BAD_KEY, 500)

    try:
        response = identify_with_plantnet(photo_bytes)
    except requests.Timeout:
        app.logger.warning("Pl@ntNet didn't answer in time")
        return error_reply(E3_TOO_SLOW, 504, can_retry=True)
    except requests.RequestException as error:
        # Log only the kind of error: its full text can contain the web address, which includes the key.
        app.logger.warning("Couldn't reach Pl@ntNet (%s)", type(error).__name__)
        return error_reply(E7_PLANTNET_DOWN, 502, can_retry=True)

    if response.status_code != 200:
        return plantnet_error(response)

    reply = response.json()
    app.logger.info("Pl@ntNet: %s identifications left today", reply.get("remainingIdentificationRequests"))

    if not reply.get("results"):
        return error_reply(E4_NO_FLOWER, 404)

    summary = summarise(reply)
    # Show in Terminal what Pl@ntNet said, to help understand surprising results.
    for candidate in summary["candidates"]:
        app.logger.info(
            "  %s%%  %s  (common name: %s)",
            candidate["confidence"],
            candidate["scientific_name"],
            candidate["common_name"] or "none from Pl@ntNet",
        )

    # The Wikipedia part, for the best guess only. fetch_summary never fails:
    # if Wikipedia has a problem, the Pl@ntNet result is still sent (W1, W2).
    best_name = summary["candidates"][0]["scientific_name"]
    summary["wikipedia"] = fetch_summary(best_name)
    app.logger.info("Wikipedia for %s: %s", best_name, summary["wikipedia"]["status"])

    return jsonify(summary)


def plantnet_error(response):
    """Turn an error from Pl@ntNet into one of our friendly messages (SPEC.md section 5)."""
    app.logger.warning("Pl@ntNet replied with status %s", response.status_code)

    if response.status_code == 404:
        return error_reply(E4_NO_FLOWER, 404)  # same photo, same answer: no point retrying
    if response.status_code == 429:
        return error_reply(E5_DAILY_LIMIT, 429)
    if response.status_code in (401, 403):
        return error_reply(E6_BAD_KEY, 500)
    if response.status_code >= 500:
        return error_reply(E7_PLANTNET_DOWN, 502, can_retry=True)
    return error_reply(E8_UNEXPECTED, 502, can_retry=True)


@app.errorhandler(413)
def photo_too_large(error):
    return error_reply(E9_TOO_LARGE, 413)


# This only runs when I start the app on my Mac with "python app.py".
# Online, the web server loads the app without running this, so debug mode is never on there.
if __name__ == "__main__":
    # The phone reaches the Mac over plain http, so the cookie can't be https-only here.
    app.config["SESSION_COOKIE_SECURE"] = False
    # host="0.0.0.0" lets other devices on my home Wi-Fi (my phone) reach the app.
    # Only run it like this on a network I trust.
    app.run(debug=True, host="0.0.0.0", port=5001)
