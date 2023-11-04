
import cv2

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
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Choose box color: Green for matches, red for non-matches
        color = (0, 255, 0) if match else (0, 0, 255)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
