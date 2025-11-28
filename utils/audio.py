import os
import tempfile
from typing import Optional

def save_uploaded_file(uploaded_file) -> str:
    """
    Save an uploaded Streamlit file to a temporary location and return the path.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Path to the saved temporary file
    """
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(uploaded_file))
    temp_file.write(uploaded_file.getvalue())
    temp_file.close()
    
    return temp_file.name

def get_file_extension(uploaded_file) -> str:
    """
    Determine the file extension of an uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: File extension including the dot (e.g., '.wav')
    """
    # Try to get extension from filename first
    if uploaded_file.name:
        _, ext = os.path.splitext(uploaded_file.name)
        if ext:
            return ext.lower()
    
    # Fallback to common extensions based on file type
    # We'll use the file type detection from Streamlit
    file_type = uploaded_file.type if hasattr(uploaded_file, 'type') else None
    
    type_to_ext = {
        'audio/wav': '.wav',
        'audio/x-wav': '.wav',
        'audio/mpeg': '.mp3',
        'audio/mp4': '.m4a',
        'audio/x-m4a': '.m4a',
        'audio/ogg': '.ogg',
        'application/octet-stream': '.m4a'  # Sometimes M4A files have this MIME type
    }
    
    if file_type in type_to_ext:
        return type_to_ext[file_type]
    
    # Default fallback
    return '.tmp'

def cleanup_temp_file(file_path: str):
    """
    Remove a temporary file.
    
    Args:
        file_path (str): Path to the temporary file to remove
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass  # Ignore errors during cleanup