# Ghost Protocol
A facial recognition anti-surveillance software.

## Features
- OpenCV live facial recognition software
- Blurring of whitelisted users' faces
- Classification of non-whitelisted and blacklisted users using facial_recognition and dlib
- Flask Web Application to add new whitelisted/blacklisted users

### Live Facial Recognition Usage
- Make sure you're located in the root folder before running this script
```bash
python main.py
```

### Web Application Usage
- Make sure you're located in the flask folder before running this script
```bash
python app.py
```

### Dependencies
- OpenCV
- dlib
- facial_recognition
- Redis