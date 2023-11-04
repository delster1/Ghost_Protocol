from PIL import Image
import os
import time
import numpy as np
import face_recognition
import cv2
from face_boxes import draw_boxes

whitelist_names = []
whitelist_encodings = []
whitelisted_faces_directory = "Whitelisted_Faces"

for filename in os.listdir(whitelisted_faces_directory):
    f = os.path.join(whitelisted_faces_directory, filename)
    loaded_array = np.load(f)

    whitelist_names.append(f)
    whitelist_encodings.append(loaded_array)
    

# Get a reference to the webcam
video_capture = cv2.VideoCapture(0)

# Reduce the resolution
video_capture.set(3, 320)  # Width
video_capture.set(4, 240)  # Height

# Initialize a list to store face encodings
face_encodings = []

t_end = time.time() + 5
while time.time() < t_end:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    match_results = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(whitelist_encodings, face_encoding)
        
        face_distances = face_recognition.face_distance(whitelist_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        match_results.append(matches[best_match_index])
        if matches[best_match_index]:
            name = whitelist_names[best_match_index]
            print(name)

    # Display the results
    draw_boxes(frame, face_locations, match_results)


    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
my_file = open("face_encodings.txt",'w')
for obj in face_encodings:
    my_file.write(f"OBJECT: {str(obj)}\n")
