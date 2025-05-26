import google.generativeai as genai
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
import os
from typing import List

# Load environment variables from a .env file
load_dotenv()

# Configure the GenerativeAI API key using the loaded environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

# Initialize the GenerativeModel with the specified model name, configuration, and safety settings
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Dictionary of Indian languages with their codes
INDIAN_LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "বাংলা (Bengali)": "bn",
    "తెలుగు (Telugu)": "te",
    "मराठी (Marathi)": "mr",
    "தமிழ் (Tamil)": "ta",
    "ગુજરાતી (Gujarati)": "gu",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "اردو (Urdu)": "ur"
}

# Function to read image data from a file path
def read_image_data(file_path: str):
    image_path = Path(file_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Could not find image: {image_path}")
    return {"mime_type": "image/jpeg", "data": image_path.read_bytes()}

# Function to generate a response based on a prompt, image path, additional text, and selected language
def generate_gemini_response(prompt: str, image_path: str, additional_text: str, selected_language: str) -> str:
    # Combine the original prompt with additional text and language preference
    combined_prompt = f"""
    {prompt}
    Additional Information from User (in {selected_language}): {additional_text}
    Please provide the response in {selected_language} if possible.
    """
    
    image_data = read_image_data(image_path)
    response = model.generate_content([combined_prompt, image_data])
    return response.text

# Initial input prompt for the plant pathologist
input_prompt = """
As a highly skilled plant pathologist, your expertise is indispensable in our pursuit of maintaining optimal plant health. You will be provided with information or samples related to plant diseases, and your role involves conducting a detailed analysis to identify the specific issues, propose solutions, and offer recommendations.

**Analysis Guidelines:**

1. **Disease Identification:** Examine the provided information or samples to identify and characterize plant diseases accurately.

2. **Detailed Findings:** Provide in-depth findings on the nature and extent of the identified plant diseases, including affected plant parts, symptoms, and potential causes.

3. **Next Steps:** Outline the recommended course of action for managing and controlling the identified plant diseases. This may involve treatment options, preventive measures, or further investigations.

4. **Recommendations:** Offer informed recommendations for maintaining plant health, preventing disease spread, and optimizing overall plant well-being.

5. **Important Note:** As a plant pathologist, your insights are vital for informed decision-making in agriculture and plant management. Your response should be thorough, concise, and focused on plant health.

**Disclaimer:**
*"Please note that the information provided is based on plant pathology analysis and should not replace professional agricultural advice. Consult with qualified agricultural experts before implementing any strategies or treatments."*

Your role is pivotal in ensuring the health and productivity of plants. Proceed to analyze the provided information or samples, adhering to the structured guidelines above.
"""

# Function to process uploaded files and generate a response
def process_uploaded_files(files: List[gr.File], additional_text: str, selected_language: str) -> tuple:
    file_path = files[0].name if files else None
    if file_path:
        response = generate_gemini_response(input_prompt, file_path, additional_text, selected_language)
    else:
        response = "Please upload an image first."
    return file_path, response

# Gradio interface setup
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            # Language selection dropdown
            language_dropdown = gr.Dropdown(
                choices=list(INDIAN_LANGUAGES.keys()),
                value="English",
                label="Select Language"
            )
            # Multilingual text input
            text_input = gr.Textbox(
                label="Additional Information (Type in your selected language)",
                placeholder="Enter additional details about the plant...",
                lines=3
            )

            # Upload button
            upload_button = gr.File(
                label="Click to Upload an Image",
                file_types=["image"],
                file_count="multiple"
            )

        with gr.Column():
            # Output display
            image_output = gr.Image(label="Uploaded Image")
            response_output = gr.Textbox(
                label="Analysis Result",
                lines=10
            )

    # Handle file upload and processing
    upload_button.change(
        fn=process_uploaded_files,
        inputs=[upload_button, text_input, language_dropdown],
        outputs=[image_output, response_output]
    )

    # Add description
    gr.Markdown("""
    ## Multilingual Plant Disease Analysis Tool
    
    This tool allows you to:
    1. Select your preferred Indian language
    2. Upload an image of the affected plant
    3. Add additional details in your chosen language
    4. Get analysis results in the selected language
    
    Supported languages include Hindi, Bengali, Telugu, Tamil, and more.
    """)

# Launch the Gradio interface
demo.launch(debug=True)
