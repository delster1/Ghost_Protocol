import os
import time
import numpy as np
import face_recognition
import cv2
import random
import string
from face_id import identify_faces
from face_labels import draw_labels
from concurrent.futures import ThreadPoolExecutor

# Global constants
WHITELISTED_FACES_DIRECTORY = "Whitelisted_Faces"
BLACKLISTED_FACES_DIRECTORY = "Blacklisted_Faces"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_PROCESSING_INTERVAL = 1  # Process every frame
RECOGNITION_TOLERANCE = 0.6  # Tolerance for face recognition
RESIZE_FACTOR = 0.5
RESCALE_FACTOR = 2  # Doing this to avoid live division
BATCH_SIZE = 4  # Number of faces in each batch for parallel processing

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

def process_faces(face_batch):
    # Convert each face in the batch from BGR to RGB
    rgb_faces = [cv2.cvtColor(face, cv2.COLOR_BGR2RGB) for face in face_batch]
    # Compute the face encodings
    face_encodings = []
    for face in rgb_faces:
        encodings = face_recognition.face_encodings(face)
        if len(encodings) > 0:
            face_encodings.append(encodings[0])
    return face_encodings


def run_video(whitelist_names, whitelist_encodings):
    # Get a reference to the webcam
    video_capture = cv2.VideoCapture(0)
    time.sleep(2)  # Camera warm-up

    # Set the resolution
    video_capture.set(3, CAMERA_WIDTH)
    video_capture.set(4, CAMERA_HEIGHT)

    frame_count = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            frame_count += 1

            # Only process every nth frame to improve performance
            if frame_count % FRAME_PROCESSING_INTERVAL == 0:
                # Resize frame for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)

                # Find all the faces in the current frame of video
                face_locations = face_recognition.face_locations(small_frame, model="hog")
                
                # Prepare batches of faces for parallel processing
                face_batches = [small_frame[top:bottom, left:right] for top, right, bottom, left in face_locations]
                face_batches = [face_batches[i:i + BATCH_SIZE] for i in range(0, len(face_batches), BATCH_SIZE)]
                
                # Process each batch in parallel
                future_results = [executor.submit(process_faces, batch) for batch in face_batches]
                face_encodings = [enc for future in future_results for enc in future.result()]
                
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
