from flask import Flask, render_template, Response, redirect, url_for
import cv2
import face_recognition
import pickle

app = Flask(__name__)

# Load the face encodings
with open('face_encodings.pkl', 'rb') as f:
    known_face_encodings = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Recognize face
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            match_found = False
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True in matches:
                    match_found = True
                    break
            
            if match_found:
                cap.release()
                return redirect(url_for('access_granted'))

            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/access_granted')
def access_granted():
    return render_template('access_granted.html')

if __name__ == '__main__':
    app.run(debug=True)