import os
import cv2
import numpy as np
import tensorflow as tf
import google.generativeai as genai
import time  # Import for unique filenames
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# Configure API key
genai.configure(api_key="your api")  # Replace with your Gemini API key

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load the trained model
model = tf.keras.models.load_model("model/final_tumor_model.keras")

# Class labels from training
labels = {0: 'glioma', 1: 'meningioma', 2: 'notumor', 3: 'pituitary'}

# Image size for model input
image_size = 150

# Function to get medical info using Gemini API
def get_medical_info(tumor_type):
    prompt = f"""
    Provide medical information for {tumor_type} brain tumor including:
    - Affected location in the brain.
    - Common symptoms.
    - Medical recommendations and treatments.
    - Severity level and potential risks.
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Function to predict the tumor type from an image
def predict_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (image_size, image_size))
    img = img / 255.0  # Normalize
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]
    predicted_label = labels[predicted_class]

    medical_info = ""
    if predicted_label in ["glioma", "meningioma", "pituitary"]:
        medical_info = get_medical_info(predicted_label)

    return predicted_label, medical_info

# Route for uploading files
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        if file:
            # Save file with a unique timestamped name
            timestamp = int(time.time())
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # Predict tumor type
            predicted_label, medical_info = predict_image(file_path)

            # Redirect to the results page with a unique URL
            return redirect(url_for('show_result', filename=filename))

    return render_template("upload.html")

# New route for displaying results dynamically
@app.route("/result/<filename>")
def show_result(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    predicted_label, medical_info = predict_image(file_path)
    return render_template("result.html", image_url=file_path, tumor_type=predicted_label, medical_info=medical_info, timestamp=int(time.time()))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
