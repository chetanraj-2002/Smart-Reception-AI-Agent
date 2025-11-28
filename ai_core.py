import json
import google.generativeai as genai
from typing import Dict, Any
from config import GOOGLE_GEMINI_API_KEY, GEMINI_MODEL, GEMINI_STT_MODEL, INTENT_CATEGORIES, PRIORITIES, SENTIMENTS, DEPARTMENTS

def get_gemini_client():
    """
    Get a Google Gemini client instance.
    Raises an error if API key is not set.
    """
    if not GOOGLE_GEMINI_API_KEY:
        raise ValueError("Google Gemini API key is not set. Please set the GOOGLE_GEMINI_API_KEY environment variable.")
    
    # Configure the Gemini client
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    return genai

def transcribe_audio(file_path: str) -> str:
    """
    Convert audio file to text using Google Gemini.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    # Configure the Gemini client
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    
    # Upload the audio file
    audio_file = genai.upload_file(path=file_path)
    
    # Use the correct model name for speech-to-text
    model = genai.GenerativeModel(model_name=GEMINI_STT_MODEL)
    
    # Generate transcription
    prompt = "Transcribe this audio file. Provide only the transcription text without any additional explanation."
    response = model.generate_content([prompt, audio_file])
    
    # Delete the uploaded file
    genai.delete_file(audio_file.name)
    
    return response.text

def analyze_call(transcript: str) -> Dict[str, Any]:
    """
    Analyze a call transcript using Google Gemini to extract structured information.
    
    Args:
        transcript (str): The transcribed text from the call
        
    Returns:
        Dict[str, Any]: Structured analysis of the call including intent, sentiment, etc.
    """
    # Configure the Gemini client
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    
    # Use the correct model name for text analysis
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    
    # System prompt to guide the AI's response format
    system_prompt = f"""
    You are an AI assistant that analyzes customer service calls and extracts structured information.
    
    Please analyze the following call transcript and respond ONLY with a JSON object that follows this exact schema:
    {{
        "caller_name": "string or null",
        "caller_contact": "string or null",
        "intent_category": "one of: {', '.join(INTENT_CATEGORIES)}",
        "sentiment": "one of: {', '.join(SENTIMENTS)}",
        "priority": "one of: {', '.join(PRIORITIES)}",
        "department": "one of: {', '.join(DEPARTMENTS)}",
        "summary_short": "1-2 line summary",
        "summary_full": "3-6 line detailed summary"
    }}
    
    Guidelines:
    - Extract caller information (name, contact) only if explicitly mentioned in the transcript
    - For contact information, prioritize email over phone number if both are available
    - Choose the most appropriate intent category from the provided list
    - Assess sentiment based on the tone and content of the call
    - Assign priority based on urgency and importance of the issue
    - Route to the most appropriate department
    - Provide a concise summary and a more detailed summary
    - Respond ONLY with valid JSON, no additional text or markdown
    """

    # User prompt with the actual transcript
    user_prompt = f"Please analyze this call transcript:\n\n{transcript}"

    # Make the API call
    try:
        response = model.generate_content(
            [system_prompt, user_prompt],
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON response
        analysis_result = json.loads(response.text)
        return analysis_result
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a default structure with error info
        return {
            "error": f"Failed to parse AI response as JSON: {str(e)}",
            "raw_response": response.text if 'response' in locals() else "No response received",
            "caller_name": None,
            "caller_contact": None,
            "intent_category": "other",
            "sentiment": "neutral",
            "priority": "medium",
            "department": "General",
            "summary_short": "Analysis failed",
            "summary_full": f"Failed to parse AI response: {response.text if 'response' in locals() else 'No response received'}"
        }
    except Exception as e:
        # Handle any other exceptions
        return {
            "error": f"Failed to analyze call: {str(e)}",
            "caller_name": None,
            "caller_contact": None,
            "intent_category": "other",
            "sentiment": "neutral",
            "priority": "medium",
            "department": "General",
            "summary_short": "Analysis failed",
            "summary_full": f"Failed to analyze call: {str(e)}"
        }

def validate_analysis(analysis: Dict[str, Any]) -> bool:
    """
    Validate that the analysis contains all required fields with valid values.
    
    Args:
        analysis (Dict[str, Any]): The analysis result to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        "caller_name", "caller_contact", "intent_category", 
        "sentiment", "priority", "department", 
        "summary_short", "summary_full"
    ]
    
    # Check that all required fields are present
    for field in required_fields:
        if field not in analysis:
            return False
    
    # Check that categorical fields have valid values
    if analysis["intent_category"] not in INTENT_CATEGORIES:
        return False
        
    if analysis["sentiment"] not in SENTIMENTS:
        return False
        
    if analysis["priority"] not in PRIORITIES:
        return False
        
    if analysis["department"] not in DEPARTMENTS:
        return False
    
    return True