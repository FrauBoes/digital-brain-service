from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import atexit
import os
import shutil

ARTIFACTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'artifacts'))
ZIP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'zips'))
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp'))

os.makedirs(ZIP_DIR, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artifacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.mp3', '.mp4'}

db = SQLAlchemy(app)

class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)

class DownloadLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False)
    zip_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def initialize_database():
    with app.app_context():
        if not os.path.exists('artifacts.db'):
            db.create_all()

@app.route("/")
def home():
    """Landing page"""
    return render_template("index.html")

@app.route('/about', methods=['GET', ])
def about():
    return render_template('about.html')

@app.route('/user/<uuid:user_uuid>', methods=['GET'])
def user_page(user_uuid):
    """Render the user page for the given UUID."""
    return render_template("user.html", user_uuid=user_uuid)

@app.route('/artifacts/<uuid:user_uuid>', methods=['POST'])
def store_artifact(user_uuid):
    """Store the artifact passed for the given UUID."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'File must have a name'}), 400

    filename = secure_filename(file.filename)
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return jsonify({'error': 'Unsupported file type'}), 400

    user_dir = os.path.join('artifacts', str(user_uuid))
    os.makedirs(user_dir, exist_ok=True)

    filepath = os.path.join(user_dir, filename)
    if os.path.exists(filepath):
        return jsonify({'error': 'File already exists'}), 409

    file.save(filepath)

    artifact = Artifact(uuid=str(user_uuid), filename=filename, filepath=filepath)
    db.session.add(artifact)
    db.session.commit()

    return jsonify({'message': 'Artifact stored successfully', 'uuid': user_uuid, 'filename': filename}), 201

@app.route('/artifacts/<uuid:user_uuid>', methods=['GET'])
def get_artifacts_by_uuid(user_uuid):
    """Get all artifacts of the given uuid."""
    artifacts = Artifact.query.filter_by(uuid=str(user_uuid)).all()
    if not artifacts:
        return jsonify({'error': 'No artifacts found for this UUID'}), 404

    response = [
        {
            'uuid': artifact.uuid,
            'filename': artifact.filename,
            'file_url': url_for('uploaded_file_by_uuid', user_uuid=artifact.uuid, filename=artifact.filename)
        }
        for artifact in artifacts
    ]
    return jsonify(response)

@app.route('/artifacts/download/<uuid:user_uuid>', methods=['GET'])
def download_artifacts_by_uuid(user_uuid):
    """Download all artifacts of the given uuid as zip."""
    artifacts = Artifact.query.filter_by(uuid=str(user_uuid)).all()
    if not artifacts:
        return jsonify({'error': 'No artifacts found for this UUID'}), 404

    os.makedirs(TEMP_DIR, exist_ok=True)

    for artifact in artifacts:
        shutil.copy(artifact.filepath, TEMP_DIR)

    zip_path = os.path.join(ZIP_DIR, f"{user_uuid}_artifacts.zip")
    shutil.make_archive(zip_path[:-4], 'zip', TEMP_DIR)

    absolute_zip_path = os.path.abspath(zip_path)

    if not os.path.exists(absolute_zip_path):
        return jsonify({'error': 'Generated file not found'}), 404

    log = DownloadLog(uuid=str(user_uuid), zip_path=absolute_zip_path)
    db.session.add(log)
    db.session.commit()

    shutil.rmtree(TEMP_DIR)
    return send_file(absolute_zip_path, as_attachment=True, mimetype='application/zip')

@app.route('/artifacts/<uuid:user_uuid>/<path:filename>', methods=['GET'])
def uploaded_file_by_uuid(user_uuid, filename):
    """Serve uploaded file from per-user folder."""
    user_folder = os.path.join(ARTIFACTS_DIR
, str(user_uuid))
    file_path = os.path.join(user_folder, filename)
    print(f"Looking for: {file_path}")

    if os.path.exists(file_path):
        return send_from_directory(user_folder, filename)
    print("File not found!")
    return jsonify({'error': 'File not found'}), 404

def cleanup_folders():
    for folder in [ZIP_DIR]:
        try:
            shutil.rmtree(folder)
            print(f"Cleaned up '{folder}/' folder.")
        except FileNotFoundError:
            print(f"Folder '{folder}/' not found. Skipped.")
        except Exception as e:
            print(f"Error removing '{folder}/': {e}")

if __name__ == '__main__':
    initialize_database()
    print(app.url_map)
    atexit.register(cleanup_folders)
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # limit to 20 MB
    app.run(host='0.0.0.0', port=5000)
