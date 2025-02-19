from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import os
import cv2
import numpy as np
import tensorflow as tf
import re
import time
import google.generativeai as genai
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file upload limit

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure API Keys
genai.configure(api_key='put your api')

# Load MRI model
MRI_MODEL_PATH = "combined/model/final_tumor_model.keras"
mri_model = tf.keras.models.load_model(MRI_MODEL_PATH)

# MRI Class Labels
mri_labels = {0: 'glioma', 1: 'meningioma', 2: 'notumor', 3: 'pituitary'}
image_size = 150  # For MRI model input

# Set up Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'

### ====== [ ROUTES ] ====== ###
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/details')
def details():
    return render_template('details.html')


### ====== [ SCAN & OCR ] ====== ###
@app.route('/scan', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400  # Handle missing file error

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400  # Handle empty filename

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # OCR processing
            extracted_text = pytesseract.image_to_string(Image.open(file_path))

            # Generate AI content using extracted text
            model = genai.GenerativeModel("gemini-1.5-flash")
            chat_session = model.start_chat()
            response = chat_session.send_message(["Extract insights from this medical scan report:", extracted_text])
            generated_output = response.text

            return render_template('scan.html', extracted_text=extracted_text, generated_output=generated_output, image_path=file_path)

    return render_template('scan.html')


### ====== [ X-RAY PROCESSING ] ====== ###
def highlight_issues(text):
    """Highlight medical terms in AI response."""
    patterns = [
        r"\b(fracture.*?radius.*?ulna.*?bones)\b",
        r"\b(displacement.*?fractured fragments)\b",
        r"\b(complete fracture)\b",
        r"\b(bone.*?broken)\b",
        r"\b(fracture.*?midshaft)\b",
        r"\b(clear fracture)\b"
    ]
    for pattern in patterns:
        text = re.sub(pattern, r"<b><u>\1</u></b>", text, flags=re.IGNORECASE)
    return text

@app.route('/xray', methods=['GET', 'POST'])
def process_xray():
    analysis = None
    image_url = None

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = "/" + file_path

            # AI Analysis
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            chat_session = model.start_chat()
            response = chat_session.send_message(["Analyze this X-ray.", Image.open(file_path)])
            analysis = highlight_issues(response.text)

    return render_template("xindex.html", image_url=image_url, analysis=analysis)


### ====== [ MRI PROCESSING ] ====== ###
def get_medical_info(tumor_type):
    """Generate medical info for MRI results."""
    prompt = f"""
    Provide medical details about {tumor_type} brain tumor:
    - Affected area
    - Symptoms
    - Treatments & risks
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

def predict_mri(image_path):
    """Classify MRI scan using ML model."""
    img = cv2.imread(image_path)
    img = cv2.resize(img, (image_size, image_size))
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=0)

    prediction = mri_model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]
    predicted_label = mri_labels[predicted_class]

    medical_info = get_medical_info(predicted_label) if predicted_label != "notumor" else "No tumor detected."

    return predicted_label, medical_info

@app.route("/mri", methods=["GET", "POST"])
def upload_mri():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files["file"]
        if file.filename == '':
            return "No selected file", 400

        if file:
            timestamp = int(time.time())
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            return redirect(url_for('show_mri_result', filename=filename))

    return render_template("upload.html")

@app.route("/result/<filename>")
def show_mri_result(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    predicted_label, medical_info = predict_mri(file_path)
    return render_template("result.html", image_url=file_path, tumor_type=predicted_label, medical_info=medical_info)


### ====== [ RUN FLASK APP ] ====== ###
if __name__ == '__main__':
    app.run(debug=True)

#working