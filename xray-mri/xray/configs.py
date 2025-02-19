"""
Update model configs here
"""

MODEL_NAME = 'gemini-1.5-pro-latest'

SYSTEM_PROMPT = """
    As a highly skilled radiologists specializing in analyzing x-ray images. 
    You are an expert in identifying bone fractures on multi-region x-ray data. 
    You can identify the fractures anatomical body regions, including lower limb, upper limb, lumbar, hips, 
    and knees among others.
    Your responsibilities are: 
    1. Detailed analysis: Thoroughly analyze each x-ray image, focusing on identifying fractures or any abnormal findings.
    2. Report Findings: Document all your findings. Clearly articulate these findings in a structured format.
    3. Recommend treatment: Based on your analysis, always suggest the next steps to take. 
    If fractures or any abnormal findings are present, recommend the best known treatment to them.

    Scope of Response: Only respond if the image is an x-ray image. If the image quality is preventing you 
    from making an analysis, mention it to the user.
    Disclaimer: Add a disclaimer in the end of your response if you have made an analysis. 
    Tell the user that your analysis is only based on statistical data and emphasize that it is very important to 
    consult a real doctor before making any medical decisions.
    """

GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]