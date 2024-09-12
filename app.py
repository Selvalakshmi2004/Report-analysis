from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import os
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Set up pytesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


# Configure Google Generative AI API
genai.configure(api_key='AIzaSyAEcGv1nDRPSw678oITOLTGwJRYxh3Aj3w')


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Open image and extract text using pytesseract
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)

            # Call Google Generative AI (Gemini model) to generate content from the extracted text
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content([extracted_text+"By this report give a summary of the disease with positive or negative impacts"])
            
            # Get the generated output text from the model
            generated_output = response.text
            
            # Render the page with the extracted text and the generated content
            return render_template('index.html', extracted_text=extracted_text, generated_output=generated_output, image_path=file_path)
    
    return render_template('index.html', extracted_text=None, generated_output=None)

if __name__ == '__main__':
    app.run(debug=True)
