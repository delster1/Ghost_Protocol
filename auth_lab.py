import redis
import numpy as np

def setup_redis(redis_host, redis_port, redis_password):
    r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password)

    return r

def build_lists(r):
    whitelist_names = []
    whitelist_encodings = []
    blacklist_names = []
    blacklist_encodings = []
    database_names = r.keys()
    
    for name in database_names:
        list = r.hget(name, "whitelist")
        face_encoding = r.hget(name, "face_encoding")
        if list.decode("utf-8") == "0":
            blacklist_names.append(name.decode("utf-8"))
            blacklist_encodings.append(face_encoding)
        if list.decode("utf-8") == "1":
            whitelist_names.append(name.decode("utf-8"))
            whitelist_encodings.append(face_encoding)

    whitelist_encodings = get_user_encodings(r,whitelist_encodings)
    blacklist_encodings = get_user_encodings(r,blacklist_encodings)

    return whitelist_names, whitelist_encodings, blacklist_names, blacklist_encodings

def build_blacklist(r):
    blacklist_encoding = []
    

def add_users(r, names, face_encodings):
    for index, object in enumerate(names):
        add_user(r, names[index], face_encodings[index])

def add_user(r, name, face_encoding):
    # Redis commands
    face_encoding_bytes = face_encoding.tobytes()
    r.hset(name,"face_encoding", face_encoding_bytes)
    r.hset(name, "whitelist", "1")
def get_user_encodings(r,encodings):
    face_encodings = []
    for encoding in encodings:

        encoding = np.frombuffer(encoding, dtype=np.float64)
        face_encodings.append(encoding)
    return face_encodings
