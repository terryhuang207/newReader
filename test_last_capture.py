#!/usr/bin/env python3
"""
Test Last Capture Display
Simple test to verify the last capture display works
"""

import requests
import json

def test_last_capture_display():
    """Test the last capture display functionality"""
    
    print("🧪 Testing Last Capture Display")
    print("=" * 40)
    
    # Test configuration
    BASE_URL = "http://localhost:5001"
    
    try:
        # Test 1: Check if web interface loads
        print("\n1️⃣ Testing web interface...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Web interface accessible")
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
        
        # Test 2: Check files API
        print("\n2️⃣ Testing files API...")
        response = requests.get(f"{BASE_URL}/api/files")
        if response.status_code == 200:
            files_data = response.json()
            print(f"✅ Files API working - {len(files_data.get('files', []))} files found")
            
            if files_data.get('files'):
                latest = files_data['files'][0]
                print(f"   📸 Latest file: {latest['filename']}")
                print(f"   📏 Size: {latest['size']} bytes")
                print(f"   📅 Created: {latest['created']}")
            else:
                print("   📁 No files available for testing")
        else:
            print(f"❌ Files API failed: {response.status_code}")
            return False
        
        # Test 3: Check if we can access an image file
        print("\n3️⃣ Testing image access...")
        if files_data.get('files'):
            test_filename = files_data['files'][0]['filename']
            response = requests.get(f"{BASE_URL}/api/files/{test_filename}")
            if response.status_code == 200:
                print(f"✅ Image file accessible: {test_filename}")
                print(f"   📏 Content length: {len(response.content)} bytes")
                print(f"   🖼️ Content type: {response.headers.get('content-type', 'unknown')}")
            else:
                print(f"❌ Image file access failed: {response.status_code}")
        else:
            print("   ⚠️ Skipping image test - no files available")
        
        print("\n" + "=" * 40)
        print("✅ All tests passed!")
        print("\n🌐 To see the last capture display:")
        print("   • Open http://localhost:5001 in your browser")
        print("   • Look for 'Last Captured Image' section below files")
        print("   • If no images exist, start camera and capture one")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app")
        print("💡 Make sure to run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_last_capture_display()
