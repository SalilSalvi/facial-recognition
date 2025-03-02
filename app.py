from flask import Flask, render_template, Response, redirect, url_for, jsonify
import cv2
import face_recognition
import pickle
import numpy as np
import os

app = Flask(__name__)

# Create static folder if it doesn't exist
os.makedirs('static', exist_ok=True)

# Load the face encodings
with open('ccino_face.pkl', 'rb') as f:
    known_face_encodings = pickle.load(f)

# Global variable to track match status
match_found = False

@app.route('/')
def index():
    global match_found
    match_found = False
    return render_template('index.html')

@app.route('/check_match')
def check_match():
    global match_found
    if match_found:
        match_found = False  # Reset for next use
        return jsonify({"match": True})
    return jsonify({"match": False})

@app.route('/video_feed')
def video_feed():
    def gen():
        global match_found
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

            # Recognize face
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True in matches:
                    match_found = True

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangle around faces with an elegant color
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (148, 131, 201), 2)  # Lavender color for elegance
                
                # Add text with recognized status
                if match_found:
                    cv2.putText(frame, "Recognized", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (148, 131, 201), 2)

            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            
            if match_found:
                # Don't try to redirect here, just break the loop after sending a few more frames
                # This makes the UI experience smoother
                if cv2.waitKey(3000):  # Wait for 3 seconds to show the "Recognized" status
                    break
                
        cap.release()
        
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/access_granted')
def access_granted():
    return render_template('access_granted.html')

if __name__ == '__main__':
    app.run(debug=True)