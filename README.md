# ChatHugginf - AI Chat Application

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Inference%20API-yellow)](https://huggingface.co/inference-api)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange)](https://gradio.app/)
[![Google Sheets](https://img.shields.io/badge/Logging-Google%20Sheets-green)](https://developers.google.com/sheets/api)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A modern AI-powered chat interface built with **Gradio** and **Hugging Face Inference API**, featuring Google Sheets logging and IP tracking.

## 🛠️ Tech Stack

- **UI Framework**: Gradio 
- **AI Model**: Qwen/Qwen2.5-72B-Instruct (Hugging Face)
- **Inference**: Hugging Face Inference API
- **Logging**: Google Sheets API (gspread)
- **Authentication**: Google Service Account
- **Language**: Python

## 📁 Project Structure

```
chathugginf/
├── app.py              # Main Gradio application
└── service_name.json   # Google Service Account credentials
```

## 🔑 Key Features

- ✅ AI-powered chat using Hugging Face models
- ✅ Real-time streaming responses
- ✅ Session management with UUID
- ✅ IP address logging (configurable)
- ✅ Google Sheets integration for chat history
- ✅ Premium glassmorphism UI design
- ✅ Custom CSS with animations

## 🗄️ Data Structures

### Session Management
- **Session ID**: UUID v4 generated per user
- **Storage**: Gradio State (in-memory)

### Chat History (Google Sheets)
```python
headers = ["Session ID", "Timestamp", "User Message", "AI Response", "IP Address"]
```

### Message Flow
```python
messages = [
    {"role": "user", "content": "message"},
    {"role": "assistant", "content": "response"}
]
```

## 🔌 API Integration

### Hugging Face Inference API
```python
client = InferenceClient(
    model="Qwen/Qwen2.5-72B-Instruct",
    token=HF_TOKEN
)

stream = client.chat_completion(
    messages=messages,
    max_tokens=1024,
    stream=True,
    temperature=0.7,
    top_p=0.9
)
```

### Google Sheets API
- **Scopes**: `spreadsheets`, `drive`
- **Authentication**: Service Account (OAuth2)
- **Operations**: Append rows, format headers

## 💻 Implementation Details

### IP Address Extraction

The app extracts client IP addresses using Gradio's `Request` object:

```python
def generate_response(message, history, session_id, request: gr.Request):
    try:
        if request and RECORD_IP:
            client_ip = request.client.host
        else:
            client_ip = "N/A"
    except:
        client_ip = "Unknown"
```

**How it works**:
1. Gradio passes HTTP request object to function
2. IP extracted via `request.client.host`
3. Falls back to "N/A" if `RECORD_IP=False`
4. Falls back to "Unknown" on error

### Asynchronous Logging

```python
def log_chat(session_id, user_msg, ai_response, ip="N/A"):
    def _log():
        sheet = get_sheet()
        timestamp = datetime.now().isoformat()
        sheet.append_row([session_id, timestamp, user_msg, ai_response, str(ip)])
    Thread(target=_log).start()  # Non-blocking
```

Logging runs in separate thread to avoid blocking UI.

### Streaming Responses

```python
response = ""
for chunk in stream:
    if chunk.choices and len(chunk.choices) > 0:
        delta = chunk.choices[0].delta.content
        if delta:
            response += delta
            yield response  # Real-time update
```

Gradio's generator pattern enables real-time streaming.

## 🎨 UI Design

### Custom Theme
- **Base**: Gradio Soft theme
- **Primary**: Sky blue palette
- **Font**: Google Font "Outfit"

### CSS Features
- Glassmorphism chat bubbles
- Gradient animated title
- Smooth hover effects
- Rounded input fields
- Button pop animations

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Hugging Face account + API token
- Google Cloud project with Sheets API enabled
- Service Account credentials

### Installation

1. **Install dependencies**:
   ```bash
   pip install gradio huggingface_hub gspread google-auth
   ```

2. **Configure credentials**:
   - Set `HF_TOKEN` in `app.py` (line 16)
   - Set `SHEET_ID` in `app.py` (line 11)
   - Update `SERVICE_ACCOUNT_INFO` (lines 20-32)

3. **Enable/disable IP logging**:
   ```python
   RECORD_IP = True  # Line 10
   ```

4. **Run the app**:
   ```bash
   python app.py
   ```

The app will launch at: `http://localhost:7860`

## 🔒 Security Notes

**⚠️ WARNING**: The current implementation has hardcoded credentials in `app.py`. For production:

1. Move credentials to environment variables:
   ```python
   HF_TOKEN = os.getenv("HF_TOKEN")
   SHEET_ID = os.getenv("SHEET_ID")
   ```

2. Use `.env` file:
   ```bash
   HF_TOKEN=your_token_here
   SHEET_ID=your_sheet_id
   ```

3. Load with `python-dotenv`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## 📊 Data Flow

```
User Input → Gradio Interface
               ↓
         Session ID (UUID)
               ↓
    Hugging Face Inference API
               ↓
      Streaming Response
               ↓
         Gradio Output
               ↓
    Async Google Sheets Log
    (Session, Message, IP)
```

## 🌟 Advanced Features

### Chat History
- Messages logged with timestamps
- Persistent storage in Google Sheets
- Queryable by session ID

### Error Handling
- Graceful API failure handling
- Auto-fallback for IP extraction
- Silent logging failures (non-blocking)

### Performance
- Non-blocking I/O for logging
- Streaming for instant feedback
- Efficient message history management

## 📝 Configuration

```python
# Line 10: Enable/disable IP tracking
RECORD_IP = True

# Line 11: Your Google Sheet ID
SHEET_ID = "your_sheet_id_here"

# Line 15: AI Model selection
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"

# Lines 94-97: Model parameters
max_tokens=1024
temperature=0.7
top_p=0.9
stream=True
```

## 🔧 Customization

### Change AI Model
Replace `MODEL_ID` with any Hugging Face chat model:
- `meta-llama/Llama-2-70b-chat-hf`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `HuggingFaceH4/zephyr-7b-beta`

### Modify UI Theme
Edit `theme` variable (lines 228-241) or `custom_css` (lines 127-225)

## 📖 Usage

1. Open the app in browser
2. Type message in chat input
3. Receive AI response in real-time
4. All conversations logged to Google Sheets
5. Session tracked via unique ID


## 📄 License
Distributed under the **MIT License**. See `LICENSE` for more information (coming soon).

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for suggestions.
