import os
import base64
import re
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import numpy as np
import face_recognition
from utils.face_recognition import FaceRecognizer
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize face recognizer
face_recognizer = FaceRecognizer("face_encodings.pkl")

# Content data structure
content = []

def load_content():
    """Load photos and poems for the gallery"""
    global content
    
    # In a production app, this would load from a database
    content = [
        {
            "id": 1,
            "image": "static/img/content/photo1.jpg",
            "poem": "Whispers of dawn,\nDelicate light unfolds,\nA new day begins."
        },
        {
            "id": 2,
            "image": "static/img/content/photo2.jpg",
            "poem": "Mountain silhouette,\nStrength enduring through all time,\nWisdom in stillness."
        },
        {
            "id": 3,
            "image": "static/img/content/photo3.jpg",
            "poem": "Ocean waves dancing,\nEndless rhythm of the tides,\nEternity speaks."
        }
    ]

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'development-secret-key')
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Initialize app
    with app.app_context():
        initialize()
    
    @app.route('/')
    def index():
        """Main authentication page"""
        return render_template('auth.html')

    @app.route('/verify', methods=['POST'])
    def verify():
        """API endpoint to verify a face from webcam data"""
        # Get image data from the request
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data'})
        
        try:
            # Process the base64 image
            image_data = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            
            # Create a temporary file for face_recognition to process
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(image_bytes)
            
            # Detect and recognize faces
            image = face_recognition.load_image_file(temp_filename)
            os.unlink(temp_filename)  # Delete the temporary file
            
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return jsonify({'success': False, 'error': 'No face detected'})
            
            # Get face encodings for the faces in the image
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # Check if any of the faces match our known faces
            is_recognized, name = face_recognizer.recognize_face(face_encodings[0])
            
            if is_recognized:
                # Set a session cookie to maintain authentication
                session['authenticated'] = True
                session['user_name'] = name
                
                return jsonify({
                    'success': True, 
                    'authenticated': True,
                    'name': name
                })
            else:
                return jsonify({
                    'success': True,
                    'authenticated': False,
                    'error': 'Face not recognized'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/content')
    def content_page():
        """Content page with gallery (protected by authentication)"""
        if not session.get('authenticated', False):
            return redirect(url_for('index'))
        
        # return render_template('content.html', 
        #                     name=session.get('user_name', 'User'),
        #                     items=content)
        return render_template('content.html', 
                            name=session.get('user_name', 'User'))


    @app.route('/api/content')
    def get_content():
        """API endpoint to get content data"""
        if not session.get('authenticated', False):
            return jsonify({'error': 'Not authenticated'}), 401
        
        # return jsonify({'success': True, 'content': content})
        return jsonify({'success': True})

    @app.route('/logout')
    def logout():
        """Log out the user by clearing the session"""
        session.clear()
        return redirect(url_for('index'))
        
    return app

def initialize():
    """Initialize application - load models and content"""
    # Try to load the model, train if not available
    if not face_recognizer.load_model():
        static_folder = os.path.join(os.path.dirname(__file__), 'static')
        reference_dir = os.path.join(static_folder, 'img', 'reference')
        if os.path.exists(reference_dir) and os.listdir(reference_dir):
            face_recognizer.train_on_directory(reference_dir)
        else:
            print("Warning: No reference images found for training")
    
    # Load content data
    load_content()

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(debug=True)