from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import shutil

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))

app = Flask(__name__, template_folder="templates", static_folder="static")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artifacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Artifact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)

def initialize_database():
    with app.app_context():
        if not os.path.exists('artifacts.db'):
            db.create_all()

@app.route("/")
def home():
    """Landing page"""
    return render_template("index.html")

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

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
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
            'file_url': url_for('uploaded_file', filename=artifact.filename)
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

    temp_dir = os.path.join('uploads', f"temp_{user_uuid}")
    os.makedirs(temp_dir, exist_ok=True)

    for artifact in artifacts:
        shutil.copy(artifact.filepath, temp_dir)

    zip_path = os.path.join('uploads', f"{user_uuid}_artifacts.zip")
    shutil.make_archive(zip_path[:-4], 'zip', temp_dir)

    absolute_zip_path = os.path.abspath(zip_path)

    if not os.path.exists(absolute_zip_path):
        return jsonify({'error': 'Generated file not found'}), 404

    return send_file(absolute_zip_path, as_attachment=True, mimetype='application/zip')

@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    """Serve uploaded files."""
    uploads_dir = UPLOAD_FOLDER

    for root, _, files in os.walk(uploads_dir):
        if filename in files:
            return send_from_directory(root, filename)
    
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    initialize_database()
    print(app.url_map)  # Print out the available routes
    app.run(host='0.0.0.0', port=5000)
