import gradio as gr
import pytesseract
from PIL import Image
import os
import google.generativeai as genai

# Set up pytesseract path (adjust to your local installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# Configure Google Generative AI API
genai.configure(api_key='AIzaSyAEcGv1nDRPSw678oITOLTGwJRYxh3Aj3w')

# Function to handle image upload, OCR, and text generation
def process_image(image):
    # Open the image and extract text using pytesseract
    img = Image.open(image)
    extracted_text = pytesseract.image_to_string(img)
    
    # Call Google Generative AI to generate content based on the extracted text
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([extracted_text + " By this report give a summary of the disease with positive or negative impacts"])
    
    # Get the generated output from the model
    generated_output = response.text
    
    return extracted_text, generated_output

# Create the Gradio interface
iface = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="filepath"),
    outputs=[gr.Textbox(label="Extracted Text"), gr.Textbox(label="Generated AI Output")],
    title="Image OCR Text Extractor with Generative AI",
    description="Upload an image to extract text using OCR and generate AI-based content from the extracted text."
)

# Launch the Gradio app
if __name__ == '__main__':
    iface.launch()