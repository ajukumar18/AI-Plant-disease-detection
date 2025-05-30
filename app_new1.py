import datetime
import google.generativeai as genai
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
import os
from typing import List
# Add this at the top of your file
import json
from pathlib import Path

# Simple file-based user database
USER_DB_FILE = "users.json"

def load_users():
    try:
        if Path(USER_DB_FILE).exists():
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def add_user(username, password, email):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": password,  # In production, hash passwords!
        "email": email,
        "created_at": str(datetime.datetime.now())
    }
    save_users(users)
    return True

def verify_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True
    return False
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

# Authentication functions
def login(username, password):
    # In a real app, verify against database
    if username and password:  # Simple validation for demo
        return True, f"Welcome back, {username}!", gr.update(visible=True), gr.update(visible=False)
    return False, "Login failed. Please check your credentials.", gr.update(visible=False), gr.update(visible=True)

def signup(username, password, email):
    # In a real app, store in database
    if username and password and email:  # Simple validation for demo
        return True, f"Account created for {username}! Please login.", gr.update(visible=True), gr.update(visible=False)
    return False, "Please fill all fields.", gr.update(visible=False), gr.update(visible=True)

def logout():
    return gr.update(visible=False), gr.update(visible=True), "Logged out successfully."

# Custom CSS for enhanced UI
custom_css = """
:root {
    --primary: #4CAF50;
    --secondary: #8BC34A;
    --accent: #FFC107;
    --dark: #2E7D32;
    --light: #F1F8E9;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--light);
}

.gradio-container {
    background: linear-gradient(135deg, var(--light) 0%, #E8F5E9 100%);
    border-radius: 15px !important;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    max-width: 900px !important;
    margin: 20px auto !important;
}

.gr-button {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    transition: all 0.3s !important;
}

.gr-button:hover {
    background: var(--dark) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
}

.gr-button-secondary {
    background: var(--accent) !important;
    color: #333 !important;
}

.gr-input, .gr-textarea, .gr-dropdown {
    border: 1px solid #BDBDBD !important;
    border-radius: 8px !important;
    padding: 12px !important;
    background: white !important;
}

.gr-box {
    border-radius: 12px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05) !important;
}

.header {
    text-align: center;
    margin-bottom: 20px;
}

.header img {
    max-width: 150px;
    margin-bottom: 10px;
}

.header h1 {
    color: var(--dark);
    margin: 0;
}

.auth-card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    margin: 20px auto;
    max-width: 500px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.auth-card h2 {
    color: var(--primary);
    margin-top: 0;
    text-align: center;
}

.feature-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}

.feature-card h3 {
    color: var(--primary);
    margin-top: 0;
}

.tabs {
    margin-top: 20px;
}

.footer {
    text-align: center;
    margin-top: 20px;
    color: #666;
    font-size: 0.9em;
}

.welcome-message {
    text-align: center;
    font-size: 1.2em;
    margin: 20px 0;
    color: rgb(14, 2, 2);  /* This makes the welcome message appear in black */
}
"""

# Gradio interface setup
with gr.Blocks(css=custom_css, theme=gr.themes.Default(primary_hue="green")) as demo:
    # State to track authentication
    logged_in = gr.State(False)
    current_user = gr.State("")
    
    # Header section
    with gr.Row():
        with gr.Column():
            gr.Markdown("""<div class="header">
                <h1>🌿 Plant Disease Analyzer</h1>
                <p>plant pathology analysis in multiple Indian languages</p>
            </div>""")
    
    # Authentication section (visible by default)
    with gr.Column(visible=True) as auth_section:
        with gr.Tabs() as auth_tabs:
            with gr.TabItem("Login", id="login"):
                with gr.Column(elem_classes="auth-card"):
                    gr.Markdown("""<h2>Login to Your Account</h2>""")
                    login_username = gr.Textbox(label="Username", placeholder="Enter your username")
                    login_password = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
                    login_button = gr.Button("Login", variant="primary")
                    login_status = gr.Markdown()
                    
            with gr.TabItem("Sign Up", id="signup"):
                with gr.Column(elem_classes="auth-card"):
                    gr.Markdown("""<h2>Create New Account</h2>""")
                    signup_username = gr.Textbox(label="Choose Username", placeholder="Enter a username")
                    signup_email = gr.Textbox(label="Email Address", placeholder="Enter your email")
                    signup_password = gr.Textbox(label="Create Password", type="password", placeholder="Create a password")
                    signup_button = gr.Button("Create Account", variant="primary")
                    signup_status = gr.Markdown()
    
    # Main app section (hidden by default)
    with gr.Column(visible=False) as app_section:
        # Welcome message and logout button
        with gr.Row():
            welcome_message = gr.Markdown(elem_classes="welcome-message")
            logout_button = gr.Button("Logout", variant="secondary", size="sm")
        
        # Analysis tools
        with gr.Row():
            with gr.Column(scale=1):
                # Language selection dropdown
                language_dropdown = gr.Dropdown(
                    choices=list(INDIAN_LANGUAGES.keys()),
                    value="English",
                    label="🌐 Select Language",
                    interactive=True
                )
                
                # Multilingual text input
                text_input = gr.Textbox(
                    label="✍️ Additional Information (Type in your selected language)",
                    placeholder="Enter additional details about the plant...",
                    lines=3
                )

                # Upload button
                upload_button = gr.UploadButton(
                    label="📁 Upload Plant Image",
                    file_types=["image"],
                    file_count="multiple",
                    variant="primary"
                )

            with gr.Column(scale=1):
                # Output display
                image_output = gr.Image(label="🌱 Uploaded Image", height=300)
                response_output = gr.Textbox(
                    label="🔍 Analysis Result",
                    lines=10,
                    interactive=False
                )
        
        # Features section
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ## 🌟 Key Features
                
                <div class="feature-card">
                    <h3>🌍 Multilingual Support</h3>
                    <p>Get analysis in 11 Indian languages including Hindi, Bengali, Tamil, and more.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🔬 Plant Disease Analysis</h3>
                    <p>Our advanced AI model provides accurate plant disease identification and treatment suggestions.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🌱 Organic Solutions</h3>
                    <p>We prioritize natural and organic treatment options for your plants.</p>
                </div>
                """)
        
        # Footer
        gr.Markdown("""
        <div class="footer">
            <p>© 2025 Plant Disease Analyzer | Terms of Service | Privacy Policy</p>
            <p>For agricultural professionals: Contact us for enterprise solutions</p>
        </div>
        """)
    
    # Handle file upload and processing
    upload_button.upload(
        fn=process_uploaded_files,
        inputs=[upload_button, text_input, language_dropdown],
        outputs=[image_output, response_output]
    )
    
    # Authentication event handlers
    login_button.click(
        fn=login,
        inputs=[login_username, login_password],
        outputs=[logged_in, login_status, app_section, auth_section]
    )
    
    signup_button.click(
        fn=signup,
        inputs=[signup_username, signup_password, signup_email],
        outputs=[logged_in, signup_status, app_section, auth_section]
    )
    
    logout_button.click(
        fn=logout,
        outputs=[app_section, auth_section, login_status]
    )
    
    # Update welcome message when logged in
    def update_welcome_message(is_logged_in, user):
        if is_logged_in:
            return f"Welcome, {user}! Ready to analyze your plants?"
        return ""
    
    logged_in.change(
        fn=update_welcome_message,
        inputs=[logged_in, login_username],
        outputs=[welcome_message]
    )

# Launch the Gradio interface
demo.launch(debug=True)
