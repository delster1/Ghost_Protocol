import redis
import numpy as np

def setup_redis(redis_host, redis_port, redis_password):
    r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password)

    return r

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
