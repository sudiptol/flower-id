from flask import Flask, jsonify, render_template, request

# Largest photo the server accepts (10 MB). The same limit is in static/app.js.
MAX_PHOTO_BYTES = 10 * 1024 * 1024

# HEIC files say "ftyp" at byte 4, followed by one of these "brand" names.
HEIC_BRANDS = [b"heic", b"heix", b"mif1"]

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

    # For now, just report what arrived. Pl@ntNet comes in step 4.
    return jsonify(
        filename=photo.filename,
        content_type=photo.content_type,
        size_bytes=len(photo_bytes),
    )


@app.errorhandler(413)
def photo_too_large(error):
    # Error E9 from SPEC.md section 5.
    return jsonify(error="That photo is too large (over 10 MB). Please choose a smaller one."), 413


if __name__ == "__main__":
    # host="0.0.0.0" lets other devices on my home Wi-Fi (my phone) reach the app.
    # Only run it like this on a network I trust.
    app.run(debug=True, host="0.0.0.0", port=5001)
