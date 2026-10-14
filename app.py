from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


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

    # For now, just report what arrived. Pl@ntNet comes in step 4.
    return jsonify(
        filename=photo.filename,
        content_type=photo.content_type,
        size_bytes=len(photo_bytes),
    )


if __name__ == "__main__":
    # host="0.0.0.0" lets other devices on my home Wi-Fi (my phone) reach the app.
    # Only run it like this on a network I trust.
    app.run(debug=True, host="0.0.0.0", port=5001)
