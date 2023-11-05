import logging
from face_capture import run_video
from creds import redis_host, redis_port, redis_password
from auth_lab import setup_redis


def main():
    # simple configs to add day/time to the logs
    logging.basicConfig(filename='logs/out.log', encoding='utf-8', level=logging.INFO, format="%(asctime)s %(message)s")
    
    r = setup_redis(redis_host, redis_port, redis_password)

    run_video(r)

if __name__ == "__main__":
    main()
