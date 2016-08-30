import os
import uuid

from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)
app.config.from_object('config')


@app.route("/g/<gallery_id>")
def show_gallery(gallery_id):
    # Only UUIDs are allowed for sanity
    try:
        uuid.UUID(gallery_id, version=4)
    except ValueError:
        return abort(404)

    gallery_dir = os.path.join(app.config["DATA_DIR"], gallery_id)

    if os.path.exists(gallery_dir):
        images = [
                os.path.join("/g", gallery_id, f)
                for f in os.listdir(os.path.join(app.config["DATA_DIR"], gallery_id))
                ]
    else:
        images = []

    return render_template("gallery.html", images=images)


@app.route("/g/<path:filename>")
def serve_image(filename):
    return send_from_directory(app.config["DATA_DIR"], filename)

