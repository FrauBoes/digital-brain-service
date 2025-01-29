from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import shutil

app = Flask(__name__)

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

@app.route('/test', methods=['GET'])
def test():
    return {"message": f"Received test"}, 200

@app.route('/artifacts/<uuid:user_uuid>', methods=['POST'])
def store_artifact(user_uuid):
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
    artifacts = Artifact.query.filter_by(uuid=str(user_uuid)).all()
    if not artifacts:
        return jsonify({'error': 'No artifacts found for this UUID'}), 404

    response = [{'uuid': artifact.uuid, 'filename': artifact.filename} for artifact in artifacts]
    return jsonify(response)

@app.route('/artifacts/download/<uuid:user_uuid>', methods=['GET'])
def download_artifacts_by_uuid(user_uuid):
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

if __name__ == '__main__':
    initialize_database()
    print(app.url_map)  # Print out the available routes
    app.run(host='0.0.0.0', port=5000)
