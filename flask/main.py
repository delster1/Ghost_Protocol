from flask import Flask, render_template, request
import face_recognition

app = Flask(__name__)

@app.route("/")
def index():
    title = "Deez"
    return render_template('index.html', title=title)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    title = "Upload unsuccessful"
    result = title
    if request.method == 'POST':
        f = request.files['file']
        print(f"Filename: {f.filename}")

        img = face_recognition.load_image_file(f)

        print(img)
        
        title = "Upload successful"

        result = f"Upload of {f.filename} successful"

    return render_template('index.html', title=title, result=result)

if __name__ == '__main__':  
   app.run(debug=True, port=3000)