from flask import Flask, render_template, request
import os
from PIL import Image
import google.generativeai as genai
import re

# Configuration
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Google AI Model Configuration (Replace with your API key)
genai.configure(api_key="AIzaSyD2FWWkJ-lMx76_kQDQHMagv7xGVq75vKA")
MODEL_NAME = "gemini-1.5-flash" 

# Function to highlight medical terms
def highlight_issues(text):
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

@app.route("/", methods=["GET", "POST"])
def upload_file():
    analysis = None
    image_url = None

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = "/" + filepath  # Flask serves static files directly

            # Load AI Model
            model = genai.GenerativeModel(model_name=MODEL_NAME)
            chat_session = model.start_chat()

            # Analyze the image
            image_data = Image.open(filepath)
            content = ["Analyze this image.", image_data]
            response = chat_session.send_message(content)
            ai_text = response.text

            # Highlight key medical terms
            analysis = highlight_issues(ai_text)

    return render_template("xindex.html", image_url=image_url, analysis=analysis)

if __name__ == "__main__":
    app.run(debug=True)
