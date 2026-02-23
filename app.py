import gradio as gr
import gspread
from google.oauth2.service_account import Credentials
from huggingface_hub import InferenceClient
from threading import Thread
from datetime import datetime
import uuid

# --- CONFIGURATION ---
RECORD_IP = True  # Set to False if you don't want to log IPs
SHEET_ID = "1bX9jkIUG4GrlPt6y6ESFiBzyfoceeqvguMTyXhy335A"

# Using Hugging Face Inference API
# We can use a powerful model since it runs on the cloud
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct" 
HF_TOKEN = "#######"

# --- CREDENTIALS ---
# Your Service Account JSON (Embedded)
SERVICE_ACCOUNT_INFO = {
  ###########
  ########@@##
}

# --- MODEL INITIALIZATION ---
print(f"Connecting to Hugging Face Inference API ({MODEL_ID})...")
try:
    client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)
    print("✅ Inference API client ready.")
except Exception as e:
    print(f"❌ API Client Error: {e}")

# --- GOOGLE SHEETS SETUP ---
def get_sheet():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(SHEET_ID).get_worksheet(0)
    except Exception as e:
        print(f"⚠️ Google Sheets Connection Error: {e}")
def setup_headers():
    sheet = get_sheet()
    if sheet:
        try:
            # Check if headers exist
            headers = ["Session ID", "Timestamp", "User Message", "AI Response", "IP Address"]
            existing_headers = sheet.row_values(1)
            
            if existing_headers != headers:
                print("Adding headers to Google Sheet...")
                sheet.insert_row(headers, index=1)
                # Optional: Format the header row to be bold
                sheet.format("A1:E1", {"textFormat": {"bold": True}})
                print("✅ Headers added successfully.")
        except Exception as e:
            print(f"⚠️ Could not setup headers: {e}")

# Run setup on startup
setup_headers()

def log_chat(session_id, user_msg, ai_response, ip="N/A"):
    def _log():
        sheet = get_sheet()
        if sheet:
            try:
                timestamp = datetime.now().isoformat()
                sheet.append_row([session_id, timestamp, user_msg, ai_response, str(ip)])
            except Exception as e:
                print(f"Logging failed: {e}")
    Thread(target=_log).start()

# --- CHAT GENERATION ---
def generate_response(message, history, session_id, request: gr.Request):
    # With type="messages", history is already a list of dicts: [{'role': 'user', 'content': '...'}, ...]
    messages = list(history)
    messages.append({"role": "user", "content": message})
    
    try:
        stream = client.chat_completion(
            messages=messages, 
            max_tokens=1024, 
            stream=True, 
            temperature=0.7, 
            top_p=0.9
        )
        
        response = ""
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta.content
                if delta:
                    response += delta
                    yield response
    except Exception as e:
        response = f"Error: {str(e)}"
        yield response

    
    # Handle IP extraction safely
    try:
        if request and RECORD_IP:
            client_ip = request.client.host
        else:
            client_ip = "N/A"
    except:
        client_ip = "Unknown"
    
    log_chat(session_id, message, response, client_ip)

# --- UI SETUP ---
# --- UI SETUP ---
# --- UI SETUP ---
# Custom CSS for a "Premium & Interactive" aesthetic
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap');

.gradio-container {
    font-family: 'Outfit', sans-serif !important;
}

/* Animated Title */
h1 {
    text-align: center;
    background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5em !important;
    font-weight: 800 !important;
    margin-bottom: 0.1em !important;
    animation: fadeIn 1.5s ease-in-out;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(-20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 1.2em;
    margin-bottom: 25px;
    font-weight: 300;
    letter-spacing: 0.5px;
}

/* Chatbot Container - Floating Glass Effect */
#chatbot-component {
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
    transition: all 0.3s ease;
}

#chatbot-component:hover {
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25) !important;
    transform: translateY(-2px);
}

/* User & Bot Bubbles */
.message-row.user-row .message-bubble {
    border-radius: 20px 20px 4px 20px !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
}

.message-row.bot-row .message-bubble {
    border-radius: 20px 20px 20px 4px !important;
    background: #f3f4f6 !important;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* Interactive Input Area */
input {
    border-radius: 50px !important;
    border: 2px solid transparent !important;
    background-color: #f9fafb !important;
    transition: all 0.3s ease !important;
}

input:focus {
    border-color: #8bb1f6 !important;
    box-shadow: 0 0 0 4px rgba(139, 177, 246, 0.2) !important;
    background-color: white !important;
}

/* Buttons with Pop Effect */
button.primary {
    border-radius: 50px !important;
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

button.primary:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 20px rgba(0, 242, 254, 0.3);
}

button.primary:active {
    transform: scale(0.95);
}

/* Footer hidden */
footer { display: none !important; }
"""

# Theme: Modern Soft with Cyan/Sky palette
theme = gr.themes.Soft(
    primary_hue="sky",
    neutral_hue="slate",
    spacing_size="md",
    radius_size="lg",
    font=[gr.themes.GoogleFont("Outfit"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="*neutral_50",
    block_background_fill="rgba(255,255,255,0.8)",
    block_border_width="0px",
    shadow_drop="none",
    button_primary_background_fill="*primary_500",
    button_primary_text_color="white",
)

with gr.Blocks(title="GrokChat", theme=theme, css=custom_css, fill_height=True) as app:
    session_id = gr.State(lambda: str(uuid.uuid4()))
    
    with gr.Column(elem_id="main-container"):
        gr.Markdown("# ✨ GrokChat")
        gr.Markdown(f"<div class='subtitle'>Experience AI • Powered by <b>{MODEL_ID}</b></div>")
        
        chatbot = gr.ChatInterface(
            fn=generate_response,
            additional_inputs=[session_id],
            type="messages",
            examples=[["Explain quantum computing like I'm 5"], ["Draft a python script to scrape a website"], ["Tell me a joke about AI"]],
        )

if __name__ == "__main__":
    app.launch()