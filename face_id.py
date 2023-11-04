import numpy as np
import face_recognition

def identify_faces(whitelist_names, whitelist_encodings, face_encodings):
    """
    Identifies faces from a list of face encodings.

    Args:
    - whitelist_names: A list of names corresponding to the whitelist.
    - whitelist_encodings: A list of face encodings corresponding to the whitelist.
    - face_encodings: A list of face encodings to identify.

    Returns:
    A list of names identified from the face_encodings.
    """
    identified_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(whitelist_encodings, face_encoding)
        face_distances = face_recognition.face_distance(whitelist_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            string_data = whitelist_names[best_match_index].decode('utf-8')
            identified_names.append(string_data)
        else:
            identified_names.append("Unknown")
    
    return identified_names
