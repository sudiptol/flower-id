import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from plantnet import identify_with_plantnet, summarise
from wikipedia import fetch_summary

# Read secrets such as PLANTNET_API_KEY from the .env file (never saved in git).
load_dotenv()

# Largest photo the server accepts (10 MB). The same limit is in static/app.js.
MAX_PHOTO_BYTES = 10 * 1024 * 1024

# HEIC files say "ftyp" at byte 4, followed by one of these "brand" names.
HEIC_BRANDS = [b"heic", b"heix", b"mif1"]

# Messages from SPEC.md section 5, by error number.
E3_TOO_SLOW = "Identification is taking too long. Please try again."
E4_NO_FLOWER = "No flower recognised. Try a closer, sharper photo with the flower filling the frame."
E5_DAILY_LIMIT = "Daily limit reached. Identification will work again tomorrow."
E6_BAD_KEY = "Setup problem: the Pl@ntNet key isn't working. Check the .env file."
E7_PLANTNET_DOWN = "Pl@ntNet isn't responding right now. Try again in a few minutes."
E8_UNEXPECTED = "Something went wrong. Please try again."

app = Flask(__name__)
# Flask refuses anything bigger before our code even runs (error 413, handled below).
app.config["MAX_CONTENT_LENGTH"] = MAX_PHOTO_BYTES


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
    return render_template("index.html")


@app.route("/identify", methods=["POST"])
def identify():
    # The browser sends the photo as a form field named "photo".
    photo = request.files.get("photo")
    if photo is None:
        return jsonify(error="No photo was sent."), 400

    photo_bytes = photo.read()

    if is_heic(photo_bytes):
        # Error E10: Pl@ntNet only accepts JPEG and PNG. Step 6 converts photos in the browser.
        return jsonify(error="HEIC photos can't be identified yet. Please use a JPG or PNG."), 400

    if not is_jpeg_or_png(photo_bytes):
        # Error E1 from SPEC.md section 5.
        return jsonify(error="That file isn't a photo. Please choose a JPG or PNG image."), 400

    if not os.environ.get("PLANTNET_API_KEY"):
        app.logger.error("PLANTNET_API_KEY is missing. Is it in the .env file?")
        return jsonify(error=E6_BAD_KEY), 500

    try:
        response = identify_with_plantnet(photo_bytes)
    except requests.Timeout:
        app.logger.warning("Pl@ntNet didn't answer in time")
        return jsonify(error=E3_TOO_SLOW), 504
    except requests.RequestException as error:
        # Log only the kind of error: its full text can contain the web address, which includes the key.
        app.logger.warning("Couldn't reach Pl@ntNet (%s)", type(error).__name__)
        return jsonify(error=E7_PLANTNET_DOWN), 502

    if response.status_code != 200:
        return plantnet_error(response)

    reply = response.json()
    app.logger.info("Pl@ntNet: %s identifications left today", reply.get("remainingIdentificationRequests"))

    if not reply.get("results"):
        return jsonify(error=E4_NO_FLOWER), 404

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
        return jsonify(error=E4_NO_FLOWER), 404
    if response.status_code == 429:
        return jsonify(error=E5_DAILY_LIMIT), 429
    if response.status_code in (401, 403):
        return jsonify(error=E6_BAD_KEY), 500
    if response.status_code >= 500:
        return jsonify(error=E7_PLANTNET_DOWN), 502
    return jsonify(error=E8_UNEXPECTED), 502


@app.errorhandler(413)
def photo_too_large(error):
    # Error E9 from SPEC.md section 5.
    return jsonify(error="That photo is too large (over 10 MB). Please choose a smaller one."), 413


if __name__ == "__main__":
    # host="0.0.0.0" lets other devices on my home Wi-Fi (my phone) reach the app.
    # Only run it like this on a network I trust.
    app.run(debug=True, host="0.0.0.0", port=5001)
