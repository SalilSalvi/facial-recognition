import face_recognition
import os
import pickle
import pdb
from tqdm import tqdm

reference_images_dir = 'data/imgs/his/'
encodings = []

for filename in tqdm(os.listdir(reference_images_dir)):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        img_path = os.path.join(reference_images_dir, filename)
        image = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(image)
        encodings.append(encoding[0])

pdb.set_trace()
with open('models/face_encodings.pkl', 'wb') as f:
    pickle.dump(encodings, f)