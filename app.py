import os
import uuid
import re
import zipfile
import tempfile

from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, \
        send_file

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config')


@app.route("/g/<gallery_id>", methods=['GET', 'POST'])
def gallery(gallery_id):
    # Only UUIDs are allowed for sanity
    try:
        uuid.UUID(gallery_id, version=4)
    except ValueError:
        return abort(404)

    if request.method == "POST":
        return upload_to_gallery(gallery_id)
    return show_gallery(gallery_id)


def show_gallery(gallery_id):

    gallery_dir = get_gallery_dir(gallery_id)

    if os.path.exists(gallery_dir):
        images = [
                os.path.join("/g", gallery_id, f)
                for f in os.listdir(gallery_dir)
                ]
    else:
        images = []

    return render_template("gallery.html",
            images=images,
            upload_path=request.url,
            gallery_id=gallery_id)


def upload_to_gallery(gallery_id):
    gallery_dir = get_gallery_dir(gallery_id)

    def allowed_extension(filename):
        return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    for f in request.files.values():
        if not allowed_extension(f.filename):
            return abort(403)

        if not os.path.exists(gallery_dir):
            os.mkdir(gallery_dir)

        target_filename = f.filename
        while os.path.exists(os.path.join(gallery_dir, secure_filename(target_filename))):
            name, extension = target_filename.rsplit('.', 1)
            counter_match = re.search(r"(.*)-(\d+)$", name)
            if counter_match:
                target_filename = "{}-{}.{}".format(
                        counter_match.group(1),
                        int(counter_match.group(2)) + 1,
                        extension)
            else:
                target_filename = "{}-1.{}".format(name, extension)

        f.save(os.path.join(gallery_dir, secure_filename(target_filename)))

    return redirect(url_for("gallery", gallery_id=gallery_id))


@app.route("/g/<gallery_id>/zip")
def gallery_as_zip(gallery_id):
    gallery_dir = get_gallery_dir(gallery_id)
    if not os.path.exists(gallery_dir):
        return abort(404)

    temp = tempfile.NamedTemporaryFile()
    zf = zipfile.ZipFile(temp, 'w')

    for image_filename in os.listdir(gallery_dir):
        zf.write(os.path.join(gallery_dir, image_filename), image_filename)
    zf.close()

    temp.seek(0)
    return send_file(temp, attachment_filename=gallery_id + ".zip", as_attachment=True)


@app.route("/g/<path:filename>")
def serve_image(filename):
    return send_from_directory(app.config["DATA_DIR"], filename)


def get_gallery_dir(gallery_id):
    return os.path.join(app.config["DATA_DIR"], gallery_id)

