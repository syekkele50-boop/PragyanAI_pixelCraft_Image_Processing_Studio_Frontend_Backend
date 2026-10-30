import json
import os
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from PIL import Image, ImageOps, UnidentifiedImageError

from utils import apply_operation, make_collage


BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "config.json", "r", encoding="utf-8") as file:
    CONFIG = json.load(file)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = (
    CONFIG.get("max_upload_mb", 15) * 1024 * 1024
)

# For initial deployment. Restrict this to your Netlify domain later.
CORS(app)


def load_image(uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        raise ValueError("Please upload an image.")

    allowed = CONFIG.get(
        "allowed_extensions", ["png", "jpg", "jpeg", "webp"]
    )
    extension = uploaded_file.filename.rsplit(".", 1)[-1].lower()

    if "." not in uploaded_file.filename or extension not in allowed:
        raise ValueError("Unsupported file extension.")

    with Image.open(uploaded_file.stream) as source:
        source.load()
        image = ImageOps.exif_transpose(source).convert("RGB")

    if image.width * image.height > 25_000_000:
        raise ValueError("Image dimensions are too large.")

    return image


@app.get("/")
def home():
    return jsonify({
        "message": "Image Processing Studio API is running.",
        "health": "/api/health"
    })


@app.get("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.post("/api/process")
def process_image():
    try:
        operation = request.form.get("operation", "").lower()

        if not operation:
            return jsonify({"error": "Choose an operation."}), 400

        options_text = request.form.get("options", "{}")

        try:
            options = json.loads(options_text)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid options JSON."}), 400

        if not isinstance(options, dict):
            return jsonify({"error": "Options must be an object."}), 400

        if operation == "collage":
            uploads = request.files.getlist("images")

            if not uploads or not any(f.filename for f in uploads):
                uploads = [request.files.get("image")]

            images = [load_image(f) for f in uploads if f and f.filename]
            result = make_collage(images)

        else:
            original = load_image(request.files.get("image"))
            second_file = request.files.get("image2")
            second_image = (
                load_image(second_file)
                if second_file and second_file.filename
                else None
            )

            if operation in ("blend", "add", "subtract") and second_image is None:
                return jsonify({
                    "error": "This operation requires a second image."
                }), 400

            result = apply_operation(
                original,
                operation,
                image2=second_image,
                options=options
            )

        output = BytesIO()
        result.convert("RGB").save(output, format="PNG")
        output.seek(0)

        return send_file(
            output,
            mimetype="image/png",
            as_attachment=False,
            download_name="processed-image.png"
        )

    except (ValueError, UnidentifiedImageError, OSError) as error:
        return jsonify({"error": str(error) or "Could not process this image."}), 400
    except Exception:
        app.logger.exception("Image processing failed")
        return jsonify({
            "error": "An unexpected server error occurred."
        }), 500


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "error": "Upload too large. Maximum request size is 15 MB."
    }), 413


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
