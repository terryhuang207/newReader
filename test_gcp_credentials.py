#!/usr/bin/env python3
"""
Test Google Cloud Vision API credentials
"""

import os
import sys

# Add the parent directory to the path to import the credentials
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_google_cloud_credentials():
    """Test if Google Cloud credentials are working"""
    try:
        # Set the credentials path
        credentials_path = os.path.join(os.path.dirname(os.getcwd()), 'googleapi.json')
        print(f"🔍 Checking credentials at: {credentials_path}")
        
        if not os.path.exists(credentials_path):
            print("❌ Credentials file not found!")
            return False
            
        print("✅ Credentials file found")
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        print("✅ Environment variable set")
        
        # Try to import and initialize the client
        from google.cloud import vision
        print("✅ Google Cloud Vision library imported")
        
        # Test client initialization
        client = vision.ImageAnnotatorClient()
        print("✅ Google Cloud Vision client initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Testing Google Cloud Vision API Credentials")
    print("=" * 50)
    
    if test_google_cloud_credentials():
        print("\n🎉 Google Cloud Vision API is ready to use!")
    else:
        print("\n❌ Google Cloud Vision API setup failed!")
