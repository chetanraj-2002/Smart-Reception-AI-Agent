# Smart Reception AI Agent

An AI-powered reception assistant that converts voice messages to structured tickets with sentiment analysis and intent recognition.

## Features

- Audio file upload (WAV, MP3, M4A, OGG)
- Speech-to-text conversion using Google Gemini
- Intent recognition and sentiment analysis using Google Gemini
- Automatic ticket generation with priority assignment
- Department routing suggestions
- SQLite database storage
- Streamlit web interface with dashboard

## Architecture

```
smart-reception-agent/
├── app.py              # Streamlit UI and main application flow
├── ai_core.py          # AI processing functions (STT, LLM analysis)
├── db.py               # Database initialization and operations
├── config.py           # Configuration constants
├── utils/
│   └── audio.py        # Audio file handling utilities
├── requirements.txt    # Python dependencies
└── reception_agent.db  # SQLite database (created on first run)
```

## Tech Stack

- **Language**: Python 3.9+
- **UI**: Streamlit
- **AI**: 
  - Google Gemini API (speech-to-text and analysis)
- **Database**: SQLite (via Python's sqlite3 module)

## Setup Instructions

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Google Gemini API key in the `.env` file:
   ```
   GOOGLE_GEMINI_API_KEY=your-api-key-here
   ```

## How to Run Locally

```bash
streamlit run app.py
```

Then open your browser to http://localhost:8501

**Note**: The application requires a Google Gemini API key to function. Without it, the application will display an error message.

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and select your repository
4. Set the main file as `app.py`
5. Add your `GOOGLE_GEMINI_API_KEY` as a secret

### HuggingFace Spaces

1. Create a new Space on [HuggingFace](https://huggingface.co/spaces)
2. Select Streamlit as the SDK
3. Upload your files
4. Add your `GOOGLE_GEMINI_API_KEY` as a secret

## Usage

1. Ensure the GOOGLE_GEMINI_API_KEY is set in the `.env` file
2. Open the application in your browser
3. Upload an audio file (WAV, MP3, M4A, or OGG format)
4. Click "Transcribe and Generate Ticket"
5. View the transcription, analysis, and ticket information
6. Check the "Recent Tickets" section to see stored tickets

## Potential Improvements

- Real phone system integration (Twilio, SIP, etc.)
- Authentication and authorization
- Role-based access control
- Analytics dashboard
- Email/SMS notifications
- Multi-language support
- Advanced audio preprocessing