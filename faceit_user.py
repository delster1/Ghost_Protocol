class Faceit_User:
    def __init__(self, name, face_encoding):
        serialized_face = face_encoding.tobytes()

        r.set(name, face_encoding)