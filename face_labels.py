import cv2

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
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            
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
