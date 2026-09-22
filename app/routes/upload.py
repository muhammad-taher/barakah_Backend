from flask import Blueprint, request, jsonify, current_app, url_for
import os
import uuid
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__, url_prefix='/api/v1/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Ensure upload folder exists
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Return full URL assuming standard Flask setup
        # The frontend can just use this URL to display the image
        file_url = f"http://127.0.0.1:5000/static/uploads/{filename}"
        return jsonify({'url': file_url}), 201
        
    return jsonify({'error': 'File type not allowed'}), 400
