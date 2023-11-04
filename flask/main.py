from flask import Flask, render_template, request
import face_recognition

app = Flask(__name__)

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
        filename = request.form.get("filename")

        f = request.files["file"]

        fnamecontents = f.filename.split(".")

        # obtaining the file extension
        fext = fnamecontents[-1]

        if fext.lower() in ["jpg", "png", "jpeg", "heic"]:
            # loads image as ndarray
            img = face_recognition.load_image_file(f)

            # save to redis below...
        
            title = "Upload successful"

            result = f"Upload of {f.filename} as {filename} successful"

    return render_template("index.html", title=title, result=result)

if __name__ == "__main__":  
   app.run(debug=True, port=3000)