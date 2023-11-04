import redis
from creds.py import redis_host, redis_port, redis_password
import numpy as np

def setup_redis(redis_host, redis_port, redis_password):
    r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password)

    return r

def add_user(r, name, face_encoding_bits):
    # Redis commands
    r.set(name,face_encoding_bits)

def get_user_encoding(r,name):
    encoded_data = r.get(name)

    encoding = np.frombuffer(encoded_data, dtype=np.float32)

    return encoding
