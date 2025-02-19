from PIL import Image
import streamlit as st
import google.generativeai as genai
import re

from configs import SYSTEM_PROMPT, SAFETY_SETTINGS, GENERATION_CONFIG, MODEL_NAME

# Function to dynamically highlight issues in AI-generated text
def highlight_issues(text):
    # Define patterns for key issues (fracture, break, displacement, etc.)
    patterns = [
        r"\b(fracture.*?radius.*?ulna.*?bones)\b",  # Fractures in the forearm (radius and ulna)
        r"\b(displacement.*?fractured fragments)\b",  # Displacement of fractured fragments
        r"\b(complete fracture)\b",  # General fracture
        r"\b(bone.*?broken)\b",  # General bone break
        r"\b(fracture.*?midshaft)\b",  # Fracture in the midshaft
        r"\b(clear fracture)\b"  # Clear fracture description
    ]
    
    # For each pattern, replace it with bold and underline HTML tags
    for pattern in patterns:
        text = re.sub(pattern, r"<b><u>\1</u></b>", text, flags=re.IGNORECASE)
    
    return text

if __name__ == '__main__':
    # Configure Model
    genai.configure(api_key='your api')
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
        system_instruction=SYSTEM_PROMPT
    )

    # Setup Page
    st.set_page_config(page_title='Axe Analytics')
    st.title('X-Ray Analytics')
    st.subheader('Analyzing medical X-Ray images using AI.')

    # Body
    col1, col2 = st.columns([1, 5])
    submit_btn = col1.button('ANALYZE', use_container_width=True)
    uploaded_file = col2.file_uploader('Upload X-Ray Image:', type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    col3, col4 = st.columns(2)
    
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        col3.image(image_data, use_column_width=True)  # Display Image
        message = col4.empty()  # Placeholder for the output

    if submit_btn and uploaded_file:
        # Reset the session state for fresh analysis
        if 'history' in st.session_state:
            del st.session_state['history']

        # Analyze uploaded image
        content = [
            "Analyze this image.",
            image_data
        ]

        # Start chat session and send message to AI model
        chat_session = model.start_chat()
        response = chat_session.send_message(content)
        ai_text = response.text  # Get AI's generated text

        # Log AI output for debugging
        st.write("**AI Output for Debugging:**", ai_text)

        # Highlight the identified issue in the response
        highlighted_text = highlight_issues(ai_text)
        
        # Display the highlighted text with formatting
        message.write(f"<p>{highlighted_text}</p>", unsafe_allow_html=True)

        # Save the chat history for debugging if needed
        st.session_state['history'] = chat_session.history
