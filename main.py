from face_capture import run_video
from creds import redis_host, redis_port, redis_password
from auth_lab import setup_redis, build_lists
import numpy as np
import json
import os
from pathlib import Path

def main():

    
    r = setup_redis(redis_host, redis_port, redis_password)

    run_video(r)

if __name__ == "__main__":
    main()
