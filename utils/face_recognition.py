import os
import face_recognition
import numpy as np
import pickle
from typing import List, Dict, Tuple, Union
from tqdm import tqdm

class FaceRecognizer:
    def __init__(self, model_path: str = "face_encodings.pkl"):
        self.known_face_encodings = []
        self.known_face_names = []
        self.model_path = model_path
        
    def train_on_directory(self, directory: str) -> None:
        """Train face recognition model on all images in a directory."""
        print(f"Training on images in {directory}...")
        
        # Loop through all files in the directory
        for filename in tqdm(os.listdir(os.path.join(directory, "hers"))):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(os.path.join(directory, "hers"), filename)
                self._add_face(image_path, "Shiro")

        for filename in tqdm(os.listdir(os.path.join(directory, "his"))):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(os.path.join(directory, "his"), filename)
                self._add_face(image_path, "Ccino")
                
                
        # Save the trained model
        self.save_model()
        print(f"Training complete. {len(self.known_face_encodings)} faces encoded.")
        
    def _add_face(self, image_path: str, name: str) -> None:
        """Add a single face to the recognizer."""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations in the image
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print(f"No faces found in {image_path}")
                return
                
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # Add the first face found
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(name)
            # print(f"Added face: {name}")
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    def save_model(self) -> None:
        """Save trained model to disk."""
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }, f)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
            print(f"Model loaded with {len(self.known_face_encodings)} faces")
            return True
        except FileNotFoundError:
            print("No pre-trained model found")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def recognize_face(self, face_encoding) -> Tuple[bool, str]:
        """
        Recognize a face against known faces
        Returns (is_recognized, name)
        """
        if not self.known_face_encodings:
            return False, "No faces in database"
            
        # Compare faces with tolerance (lower is stricter)
        matches = face_recognition.compare_faces(
            self.known_face_encodings, 
            face_encoding, 
            tolerance=0.6
        )
        
        # Get distances (lower distance = better match)
        face_distances = face_recognition.face_distance(
            self.known_face_encodings, 
            face_encoding
        )
        
        if True in matches:
            # Use the closest match
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                return True, name
                
        return False, "Unknown"