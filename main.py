from face_capture import run_video
from creds import redis_host, redis_port, redis_password
from auth_lab import setup_redis, build_whitelist
import json

def main():
    r = setup_redis(redis_host, redis_port, redis_password)

    whitelist_names, whitelist_encodings = build_whitelist(r)
    print(whitelist_names)
    print(whitelist_encodings)
    # run_video(whitelist_names, whitelist_encodings)

if __name__ == "__main__":
    main()
