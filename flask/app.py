from flask import Flask, render_template, request
import face_recognition

import sys
sys.path.append("../")

from face_capture import RESIZE_FACTOR
from creds import redis_host, redis_port, redis_password
from auth_lab import setup_redis, add_user, add_blacklisted_user
import cv2

app = Flask(__name__)

r = setup_redis(redis_host, redis_port, redis_password)

@app.route("/")
def index():
    title = "Deez"
    return render_template("index.html", title=title)

@app.route("/uploader", methods = ["GET", "POST"])
def upload_file():
    title = "Upload unsuccessful"
    result = title
    if request.method == "POST":
        # the filename entered in the text field to save
        user_name = request.form.get("user_name")
        whitelist = request.form.get("whitelist") is not None

        f = request.files["file"]

        fnamecontents = f.filename.split(".")

        # obtaining the file extension
        fext = fnamecontents[-1]

        if fext.lower() in ["jpg", "png", "jpeg", "heic"]:
            # loads image as ndarray
            img = face_recognition.load_image_file(f)

            # Resize frame for faster face recognition processing
            small_frame = cv2.resize(img, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all the faces in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if len(face_encodings) > 0:
                if whitelist:
                    print(f"Whitelisting {user_name}")
                    add_user(r, user_name, face_encodings[0])
                else:
                    print(f"Blacklisting {user_name}")
                    add_blacklisted_user(r, user_name, face_encodings[0])

                print("User addition successful.")

            title = "Upload successful"

            result = f"Upload of {f.filename} as {user_name} successful"

    return render_template("index.html", title=title, result=result)

if __name__ == "__main__":  
   app.run(debug=True, port=3000)