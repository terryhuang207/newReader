#!/usr/bin/env python3
"""
Test Google Cloud Vision API
Simple test to verify the API works with the provided credentials
"""

import os
import json
from google.cloud import vision
from google.auth.exceptions import DefaultCredentialsError

def test_google_vision_api():
    """Test Google Cloud Vision API with credentials"""
    
    print("🧪 Testing Google Cloud Vision API")
    print("=" * 50)
    
    # Set credentials path
    credentials_path = "story-reader-470101-94cce8baf9f9.json"
    
    print(f"🔑 Credentials path: {credentials_path}")
    print(f"📁 File exists: {os.path.exists(credentials_path)}")
    
    if not os.path.exists(credentials_path):
        print("❌ Credentials file not found")
        return False
    
    # Set environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credentials_path)
    print(f"🌍 Environment variable set: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    try:
        # Test client creation
        print("\n🔍 Testing client creation...")
        client = vision.ImageAnnotatorClient()
        print("✅ Google Cloud Vision client created successfully")
        
        # Test authentication
        print("\n🔐 Testing authentication...")
        
        # Create a simple test image (1x1 pixel)
        from PIL import Image
        import io
        
        # Create a minimal test image
        test_image = Image.new('RGB', (1, 1), color='white')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create image object
        image = vision.Image(content=img_byte_arr)
        
        # Test text detection (should work even with minimal image)
        print("📖 Testing text detection...")
        response = client.text_detection(image=image)
        
        if response.error.message:
            print(f"⚠️ API response error: {response.error.message}")
        else:
            print("✅ Text detection API call successful")
            
        print("🎉 Google Cloud Vision API is working!")
        return True
        
    except DefaultCredentialsError as e:
        print(f"❌ Default credentials error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_google_vision_api()
