"""
Test script to verify that all modules are working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        import config
        print("✓ config module imported successfully")
        
        import db
        print("✓ db module imported successfully")
        
        import ai_core
        print("✓ ai_core module imported successfully")
        
        import utils.audio
        print("✓ utils.audio module imported successfully")
        
        import app
        print("✓ app module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error importing modules: {e}")
        return False

def test_database():
    """Test database initialization and basic operations."""
    try:
        from db import init_db, insert_ticket, fetch_recent_tickets, get_ticket_count
        
        # Initialize database
        init_db()
        print("✓ Database initialized successfully")
        
        # Test inserting a dummy ticket
        dummy_ticket = {
            "caller_name": "Test User",
            "caller_contact": "test@example.com",
            "intent_category": "general_query",
            "department": "General",
            "priority": "low",
            "sentiment": "neutral",
            "transcript": "This is a test transcript.",
            "summary_short": "Test summary",
            "summary_full": "This is a detailed test summary for validation purposes."
        }
        
        ticket_id = insert_ticket(dummy_ticket)
        print(f"✓ Dummy ticket inserted with ID: {ticket_id}")
        
        # Test fetching tickets
        tickets = fetch_recent_tickets(5)
        print(f"✓ Fetched {len(tickets)} tickets from database")
        
        # Test ticket count
        count = get_ticket_count()
        print(f"✓ Total tickets in database: {count}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing database: {e}")
        return False

def test_ai_core():
    """Test AI core functions (requires API key)."""
    try:
        import google.generativeai as genai
        from config import GOOGLE_GEMINI_API_KEY, GEMINI_MODEL
        
        # Check if API key is set
        if not GOOGLE_GEMINI_API_KEY:
            print("ℹ️  Google Gemini API key not set - skipping AI tests")
            return True
            
        # Configure the Gemini client
        genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
        
        # Test the model
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = model.generate_content("Hello, world!")
        print("✓ Google Gemini client initialized successfully")
        print(f"✓ Test response: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Error testing AI core: {e}")
        return False

def test_utils():
    """Test utility functions."""
    try:
        from utils.audio import get_file_extension
        import io
        
        # Create a mock uploaded file object
        class MockUploadedFile:
            def __init__(self, name, file_type):
                self.name = name
                self.type = file_type
                self._data = b"fake audio data"
                
            def getvalue(self):
                return self._data
        
        # Test with different file types
        test_files = [
            ("test.wav", "audio/wav"),
            ("recording.mp3", "audio/mpeg"),
            ("message.m4a", "audio/mp4"),
            ("call.ogg", "audio/ogg")
        ]
        
        for name, file_type in test_files:
            mock_file = MockUploadedFile(name, file_type)
            ext = get_file_extension(mock_file)
            print(f"✓ File extension for {name} ({file_type}): {ext}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing utilities: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Smart Reception AI Agent modules...\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Operations", test_database),
        ("AI Core Functions", test_ai_core),
        ("Utility Functions", test_utils)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print(f"\n--- Test Results ---")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)