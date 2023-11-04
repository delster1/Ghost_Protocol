import redis
import numpy as np

def setup_redis(redis_host, redis_port, redis_password):
    r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password)

    return r

def build_whitelist(r):
    whitelist_encodings = []
    whitelist_names = r.keys()
    whitelist_encodings = get_user_encodings(r,whitelist_names)

    return whitelist_names, whitelist_encodings

def save_blacklisted_face(face_encoding):
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

     # Associate a random insult with the unique code
    blacklist_insults[unique_code] = random.choice(insults)
    return unique_code


def add_users(r, names, face_encodings):
    for index, object in enumerate(names):
        add_user(r, names[index], face_encodings[index])

def add_user(r, name, face_encoding):
    # Redis commands
    face_encoding = face_encoding.tobytes()
    r.setnx(name,face_encoding)

def get_user_encodings(r,names):
    face_encodings = []
    for name in names:
        encoded_data = r.get(name)
        encoding = np.frombuffer(encoded_data, dtype=np.float64)
        face_encodings.append(encoding)
    return face_encodings
