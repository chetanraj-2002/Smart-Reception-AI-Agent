import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Gemini Configuration
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
GEMINI_MODEL = "models/gemini-2.0-flash"
GEMINI_STT_MODEL = "models/gemini-2.0-flash"

# Database Configuration
DB_NAME = "reception_agent.db"

# Audio Configuration
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "m4a", "ogg"]

# Analysis Configuration
INTENT_CATEGORIES = [
    "complaint",
    "support_request", 
    "appointment",
    "billing_issue",
    "hr_request",
    "general_query",
    "other"
]

PRIORITIES = ["low", "medium", "high", "critical"]
SENTIMENTS = ["positive", "neutral", "negative"]
DEPARTMENTS = ["Support", "Billing", "HR", "Sales", "Administration", "General"]

# UI Configuration
RECENT_TICKETS_LIMIT = 20