from PIL import Image
import streamlit as st
import google.generativeai as genai

from configs import SYSTEM_PROMPT, SAFETY_SETTINGS, GENERATION_CONFIG, MODEL_NAME


if __name__ == '__main__':
    # Configure Model
    genai.configure(api_key='your api')  # Check https://github.com/google-gemini/cookbook
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
        system_instruction=SYSTEM_PROMPT
    )

    # Setup Page
    # Head
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
        message = col4.chat_message("Model:")

    if submit_btn:
        # Analyze uploaded image
        history = st.session_state['history'] if 'history' in st.session_state else []

        content = [
            "Analyze this image.",
            image_data
        ]

        history.append({
            "role": "user",
            "parts": content,
        })

        chat_session = model.start_chat()
        response = chat_session.send_message(content)
        message.write(response.text)

        st.session_state['history'] = chat_session.history
