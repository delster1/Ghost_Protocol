from face_capture import build_whitelist, run_video
def main():
    
    whitelist_names, whitelist_encodings = build_whitelist()
    run_video(whitelist_names, whitelist_encodings)
if __name__ == "__main__":
    main()