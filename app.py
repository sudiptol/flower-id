from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    # host="0.0.0.0" lets other devices on my home Wi-Fi (my phone) reach the app.
    # Only run it like this on a network I trust.
    app.run(debug=True, host="0.0.0.0", port=5001)
