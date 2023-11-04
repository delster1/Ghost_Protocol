import os
import time
import numpy as np
import face_recognition
import cv2
import random
import string
from face_id import identify_faces
# from face_labels import draw_labels

# Global constants
WHITELISTED_FACES_DIRECTORY = "Whitelisted_Faces"
BLACKLISTED_FACES_DIRECTORY = "Blacklisted_Faces"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_PROCESSING_INTERVAL = 1  # Process every frame
RECOGNITION_TOLERANCE = 0.6  # Tolerance for face recognition
RESIZE_FACTOR = 0.5
RESCALE_FACTOR = 2 # doing this to avoid live division

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

def draw_boxes(frame, face_locations, matches):
    """
    Draws boxes around detected faces.
    Green boxes for whitelisted faces, red for others.

    Args:
    - frame: The frame of the video.
    - face_locations: The locations of detected faces.
    - matches: A list of boolean values indicating if a face matches the whitelist.
    """
    for (top, right, bottom, left), match in zip(face_locations, matches):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= RESCALE_FACTOR
        right *= RESCALE_FACTOR
        bottom *= RESCALE_FACTOR
        left *= RESCALE_FACTOR

        # Choose box color: Green for matches, red for non-matches
        color = (0, 255, 0) if match else (0, 0, 255)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

def draw_labels(frame, face_locations, identified_names):
    """
    Draws the usernames of whitelisted users above their heads.

    Args:
    - frame: The frame of the video.
    - face_locations: The locations of detected faces.
    - identified_names: A list of identified names for each face.
    """
    font_scale = 0.75  # Increased from 0.5 to 0.75 (30% larger)
    font_thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX

    for (top, right, bottom, left), name in zip(face_locations, identified_names):
        if name != "Unknown":
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= RESCALE_FACTOR
            right *= RESCALE_FACTOR
            bottom *= RESCALE_FACTOR
            left *= RESCALE_FACTOR
            
            # Calculate the position just above the face box
            label_position = (left, top - 15)
            
            # Get the width and height of the text box
            (text_width, text_height), _ = cv2.getTextSize(name, font, font_scale, font_thickness)

            # Set the rectangle background to black
            rectangle_bgr = (0, 0, 0)
            
            # Draw the rectangle to fill the text
            cv2.rectangle(frame, (left, top - 35), (left + text_width, top), rectangle_bgr, cv2.FILLED)
            
            # Put the text (name) at that position on the frame
            cv2.putText(frame, name, label_position, font, font_scale, (255, 255, 255), font_thickness)


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
            small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)

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
    