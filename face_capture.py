import os
import numpy as np
import face_recognition
from auth_lab import  build_lists
from send_emails import send_location_emails
from location_details import get_location_details
import cv2
import random
import string

# Global constants
ALERT_FRAME_MAX = 7 # amount of "frames" a blacklister must remain on screen before logging is sent
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
REDIS_PROCESSING_INTERVAL = 600 # update redis every 600 frames, ideally 10s
FRAME_PROCESSING_INTERVAL = 1  # Process every frame
RECOGNITION_TOLERANCE = 0.6  # Tolerance for face recognition
RESIZE_FACTOR = 0.5
RESCALE_FACTOR = 2 # doing this to avoid live division

insults = ["DANGER", "meathead", "bro has no money XD", "smelly 4real"]
blacklist_insults = {}

def identify_faces(whitelist_names, whitelist_encodings, blacklist_names, blacklist_encodings, face_encodings):
    """
    Identifies faces from a list of face encodings.

    Args:
    - whitelist_names: A list of names corresponding to the whitelist.
    - whitelist_encodings: A list of face encodings corresponding to the whitelist.
    - face_encodings: A list of face encodings to identify.

    Returns:
    A list of names identified from the face_encodings.
    """
    total_encodings = whitelist_encodings + blacklist_encodings
    total_names = whitelist_names + blacklist_names

    identified_names = []
    for face_encoding in face_encodings:
        
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(total_encodings, face_encoding)
        face_distances = face_recognition.face_distance(total_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            string_data = str(total_names[best_match_index])
            identified_names.append(string_data)
        else:
            identified_names.append("Unknown")
    
    return identified_names

def generate_unique_code(length=7):
    # Generate a random mix of letters and numbers
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# print if someone is too close to the camera
def check_closeness(frame, face_features, whitelist_names, identified_names):
    ysize, xsize, dims = frame.shape
    # if camera is 1080p then this gets scaled to 120px which is about too close for the eyes lol
    maxdist = min(ysize, xsize) / 9

    for face, name in zip(face_features, identified_names):
        if name not in whitelist_names:
            for item in ["left_eye", "right_eye"]:
                # this is assuming small model size, and thus only checks 2 points for the left and right eye
                x0, y0 = face[item][0]
                x1, y1 = face[item][1]

                x0 *= RESCALE_FACTOR
                y0 *= RESCALE_FACTOR
                x1 *= RESCALE_FACTOR
                y1 *= RESCALE_FACTOR

                # euclidean distance between facial points such as eyes
                distance = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)

                if distance > maxdist:
                    print("Camera under attack!")

# draw circles on the corners of where the face is recognized
def blur_faces(frame, face_locations, whitelist_names, identified_names, blur_amount=75):
    for (top, right, bottom, left), name in zip(face_locations, identified_names):
        if name in whitelist_names:
            # face blurring function
            top *= RESCALE_FACTOR
            right *= RESCALE_FACTOR
            bottom *= RESCALE_FACTOR
            left *= RESCALE_FACTOR

            blur_kernel = np.ones((blur_amount, blur_amount), np.float32) / blur_amount**2

            # roi should be an ndarray object
            roi = frame[top:bottom, left:right]

            roi = cv2.filter2D(src=roi, ddepth=-1, kernel=blur_kernel)

            frame[top:bottom, left:right] = roi

def draw_boxes(frame, face_locations,whitelist_names, blacklist_names, identified_names):
    """
    Draws boxes around detected faces.
    Green boxes for whitelisted faces, red for others.

    Args:
    - frame: The frame of the video.
    - face_locations: The locations of detected faces.
    - matches: A list of boolean values indicating if a face matches the whitelist.
    """
    for (top, right, bottom, left), name in zip(face_locations, identified_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= RESCALE_FACTOR
        right *= RESCALE_FACTOR
        bottom *= RESCALE_FACTOR
        left *= RESCALE_FACTOR
        color = (0, 0, 0)
        # Choose box color: Green for matches, red for non-matches
        if name in whitelist_names:
            color = (0, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
        elif name in blacklist_names:
            color = (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        else:
            color = (100, 100, 100)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

def draw_labels(frame, face_locations, whitelist_names, blacklist_names, identified_names):
    font_scale = 0.75  # Increased from 0.5 to 0.75 (30% larger)
    font_thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX

    for (top, right, bottom, left), name in zip(face_locations, identified_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= RESCALE_FACTOR
        right *= RESCALE_FACTOR
        bottom *= RESCALE_FACTOR
        left *= RESCALE_FACTOR
        
        # Draw labels for blacklisted faces
        if name in blacklist_names:
            # Retrieve the associated insult
            insult = "BLOCKED_USER"
            # Draw the unique code (label) above the face box
            label_position = (left, top - 15)
            (text_width, text_height), _ = cv2.getTextSize(name, font, font_scale, font_thickness)
            rectangle_bgr = (0, 0, 0)  # Set the rectangle background to black
            cv2.rectangle(frame, (left, top - 35), (left + text_width, top), rectangle_bgr, cv2.FILLED)
            cv2.putText(frame, name, label_position, font, font_scale, (255, 255, 255), font_thickness)
            
            # Draw the insult below the face box
            insult_position = (left, bottom + 15)
            (text_width, text_height), _ = cv2.getTextSize(insult, font, font_scale, font_thickness)
            cv2.rectangle(frame, (left, bottom), (left + text_width, bottom + 35), rectangle_bgr, cv2.FILLED)
            cv2.putText(frame, insult, insult_position, font, font_scale, (255, 255, 255), font_thickness)
        
        # Draw labels for whitelisted faces
        elif name != "Unknown":
            
            name = str(name)
            # Draw the label above the face box
            label_position = (left, top - 15)
            (text_width, text_height), _ = cv2.getTextSize(name, font, font_scale, font_thickness)
            rectangle_bgr = (0, 0, 0)  # Set the rectangle background to black
            cv2.rectangle(frame, (left, top - 35), (left + text_width, top), rectangle_bgr, cv2.FILLED)
            cv2.putText(frame, name, label_position, font, font_scale, (255, 255, 255), font_thickness)



def save_graylist_encoding(face_encoding, graylist):
    face_encoding_bytes = face_encoding.tobytes()
    file_path = os.path.join("graylist_data.bin")

    # Check if the face is not in the graylist
    if not any(face_recognition.compare_faces(graylist, face_encoding)):
        graylist.append(face_encoding)

        with open(file_path, 'ab') as file:
            file.write(face_encoding_bytes)


def save_blacklisted_face(face_encoding, blacklist_names, blacklist_encodings):
    # Check if the face is already in the blacklist
    matches = face_recognition.compare_faces(blacklist_encodings, face_encoding, tolerance=RECOGNITION_TOLERANCE)
    if True in matches:
        return matches.index(True)  # Return the existing name if face is already blacklisted
    
    unique_code = generate_unique_code()  # Generate a unique code
    
     # Associate a random insult with the unique code
    blacklist_insults[unique_code] = random.choice(insults)
    return unique_code

def run_video(r):
    # Get a reference to the webcam
    video_capture = cv2.VideoCapture(0)

    # Set the resolution
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    graylist = []
    frame_count = 0
    alert_frame_count = 0
    whitelist_names, whitelist_encodings, blacklist_names, blacklist_encodings = build_lists(r)

    while True:
        # Grab a single frame of video
        frame_count += 1

        if frame_count % REDIS_PROCESSING_INTERVAL == 0:
            frame_count = 0
            print("Updating Redis lists...")
            whitelist_names, whitelist_encodings, blacklist_names, blacklist_encodings = build_lists(r)

        # Only process every nth frame to improve performance
        if frame_count % FRAME_PROCESSING_INTERVAL == 0:
            ret, frame = video_capture.read()
            # Resize frame for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all the faces in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_features = face_recognition.face_landmarks(rgb_small_frame, face_locations, model="small")
            
            # Identify faces
            identified_names = identify_faces(whitelist_names, whitelist_encodings, blacklist_names, blacklist_encodings, face_encodings)
            # print if the user is too close to the camera
            check_closeness(frame, face_features, whitelist_names, identified_names)

            # Stores graylist data in `graylist_data.bin` per-run of the code
            for _, (face_encoding, name) in enumerate(zip(face_encodings, identified_names)):
                if name == "Unknown":
                    save_graylist_encoding(face_encoding, graylist)
                
                if name in blacklist_names:
                    alert_frame_count += 1

                    if alert_frame_count == ALERT_FRAME_MAX:
                        # make it take triple the amount of time than before to avoid
                        # unnecessary warnings
                        alert_frame_count = -2 * ALERT_FRAME_MAX

                        try:
                            print("ALERT: BLACKLISTED USER IN FRAME FOR >7 FRAMES")
                            send_location_emails()
                        except:
                            print("ALERT: BLACKLISTED USER IN FRAME FOR >7 FRAMES")
                else:
                    alert_frame_count = 0
       
            # Draw labels above the boxes
            blur_faces(frame, face_locations,whitelist_names, identified_names)

            draw_boxes(frame, face_locations, whitelist_names, blacklist_names,  identified_names)
            draw_labels(frame, face_locations, whitelist_names, blacklist_names,  identified_names)

            # Display the resulting image
            cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    