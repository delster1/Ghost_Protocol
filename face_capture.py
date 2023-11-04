import os
import time
import numpy as np
import face_recognition
import cv2
import random
import string
from face_boxes import draw_boxes
from face_id import identify_faces
from face_labels import draw_labels

# Global constants
WHITELISTED_FACES_DIRECTORY = "Whitelisted_Faces"
BLACKLISTED_FACES_DIRECTORY = "Blacklisted_Faces"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_PROCESSING_INTERVAL = 1  # Process every frame
RECOGNITION_TOLERANCE = 0.6  # Tolerance for face recognition

blacklist_names = []
blacklist_encodings = []

def build_whitelist():
    whitelist_names = []
    whitelist_encodings = []
    
    for filename in os.listdir(WHITELISTED_FACES_DIRECTORY):
        f = os.path.join(WHITELISTED_FACES_DIRECTORY, filename)
        loaded_array = np.load(f)
        
        # Assuming the name is the part of the filename before the '.npy' extension
        name = filename.split('.')[0]  
        whitelist_names.append(name)
        whitelist_encodings.append(loaded_array)

    return whitelist_names, whitelist_encodings

def generate_unique_code(length=7):
    # Generate a random mix of letters and numbers
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def save_blacklisted_face(face_encoding, directory=BLACKLISTED_FACES_DIRECTORY):
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the face is already in the blacklist
    matches = face_recognition.compare_faces(blacklist_encodings, face_encoding, tolerance=RECOGNITION_TOLERANCE)
    if True in matches:
        match_index = matches.index(True)
        return blacklist_names[match_index]  # Return the existing name if face is already blacklisted
    
    unique_code = generate_unique_code()  # Generate a unique code
    filepath = os.path.join(directory, f"{unique_code}.npy")
    np.save(filepath, face_encoding)
    return unique_code

def run_video(whitelist_names, whitelist_encodings):
    # Get a reference to the webcam
    video_capture = cv2.VideoCapture(0)
    time.sleep(2)  # Camera warm-up

    # Set the resolution
    video_capture.set(3, CAMERA_WIDTH)
    video_capture.set(4, CAMERA_HEIGHT)

    frame_count = 0
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        frame_count += 1

        # Only process every nth frame to improve performance
        if frame_count % FRAME_PROCESSING_INTERVAL == 0:
            # Resize frame for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all the faces in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            # Identify faces
            identified_names = identify_faces(whitelist_names, whitelist_encodings, face_encodings)

            # Compute match results
            match_results = [name != "Unknown" for name in identified_names]

            # Draw boxes around faces
            draw_boxes(frame, face_locations, match_results)

            # Identify blacklisted faces
            for i, (face_encoding, name) in enumerate(zip(face_encodings, identified_names)):
                if name == "Unknown":
                    unique_code = save_blacklisted_face(face_encoding)
                    blacklist_names.append(unique_code)
                    blacklist_encodings.append(face_encoding)
                    identified_names[i] = unique_code  # Update the name in the list

            # Draw labels above the boxes
            draw_labels(frame, face_locations, identified_names)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
