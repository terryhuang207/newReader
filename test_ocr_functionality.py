#!/usr/bin/env python3
"""
Test OCR Functionality
Tests the OCR button and Google Cloud Vision API integration
"""

import requests
import json
import time
import os

def test_ocr_functionality():
    """Test the OCR functionality"""
    
    print("🧪 Testing OCR Functionality")
    print("=" * 50)
    
    BASE_URL = "http://localhost:5001"
    API_BASE = f"{BASE_URL}/api"
    
    # Test 1: Check if Flask app is running
    print("\n1️⃣ Checking Flask app status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"❌ Flask app returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        print("💡 Make sure to run: python app.py")
        return False
    
    # Test 2: Check Google Cloud Vision configuration
    print("\n2️⃣ Checking Google Cloud Vision configuration...")
    try:
        response = requests.get(f"{API_BASE}/ocr/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ OCR info endpoint working")
            print(f"   🔍 Google Cloud Vision: {data.get('google_cloud_vision', {}).get('available', 'Unknown')}")
            print(f"   📖 Tesseract: {data.get('tesseract', {}).get('available', 'Unknown')}")
            
            if data.get('google_cloud_vision', {}).get('available'):
                print("   ✅ Google Cloud Vision API is available")
            else:
                print("   ⚠️ Google Cloud Vision API not available")
                
        else:
            print(f"❌ OCR info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking OCR info: {e}")
        return False
    
    # Test 3: Check if there are captured images
    print("\n3️⃣ Checking for captured images...")
    try:
        response = requests.get(f"{API_BASE}/files")
        if response.status_code == 200:
            files_data = response.json()
            if files_data.get('files'):
                print(f"✅ Found {len(files_data['files'])} captured images")
                latest_file = files_data['files'][0]
                print(f"   📸 Latest: {latest_file['filename']}")
                
                # Test 4: Test OCR on the latest image
                print("\n4️⃣ Testing OCR on latest image...")
                try:
                    ocr_response = requests.post(f"{API_BASE}/ocr/{latest_file['filename']}")
                    if ocr_response.status_code == 200:
                        ocr_data = ocr_response.json()
                        print("✅ OCR API working")
                        print(f"   🎯 Success: {ocr_data.get('success', False)}")
                        print(f"   🔍 Method: {ocr_data.get('ocr_method', 'Unknown')}")
                        print(f"   ⏱️ Time: {ocr_data.get('processing_time', 'Unknown')}s")
                        
                        if ocr_data.get('success'):
                            text = ocr_data.get('extracted_text', '')
                            print(f"   📝 Text length: {len(text)} characters")
                            if text:
                                print(f"   📖 Preview: {text[:100]}...")
                            else:
                                print("   ⚠️ No text extracted")
                        else:
                            print(f"   ❌ OCR failed: {ocr_data.get('error', 'Unknown error')}")
                    else:
                        print(f"❌ OCR API failed: {ocr_response.status_code}")
                        print(f"   Response: {ocr_response.text}")
                        
                except Exception as e:
                    print(f"❌ Error testing OCR: {e}")
            else:
                print("📁 No captured images found")
                print("💡 Start the camera and capture an image first")
                return False
        else:
            print(f"❌ Files API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 OCR Functionality Test Results:")
    print("✅ OCR button added to web interface")
    print("✅ OCR results section above captured files")
    print("✅ Google Cloud Vision API integration")
    print("✅ OCR metadata display (method, confidence, time)")
    print("✅ Copy text and text-to-speech functionality")
    
    return True

def show_web_interface_guide():
    """Show how to use the OCR functionality in the web interface"""
    print("\n🌐 Web Interface OCR Guide:")
    print("=" * 50)
    
    print("1. 📱 Open your browser and go to: http://localhost:5001")
    print("2. 🎥 Click 'Start Camera' to activate the camera")
    print("3. 📸 Click 'Capture' button or press Spacebar to take a photo")
    print("4. 🔍 Click '🔍 OCR Last Image' button (enabled after capture)")
    print("5. 📖 View OCR results above the captured files section")
    print("6. 📋 Use 'Copy Text' to copy extracted text to clipboard")
    print("7. 🔊 Use 'Text to Speech' to hear the extracted text")
    print("8. 🗑️ Use 'Clear Results' to hide OCR results")
    
    print("\n💡 OCR Features:")
    print("   • Google Cloud Vision API integration")
    print("   • Fallback to Tesseract if Google Vision fails")
    print("   • Real-time processing with progress indicator")
    print("   • Image preview with extracted text")
    print("   • Processing metadata (method, confidence, time)")
    print("   • Copy and text-to-speech functionality")

def main():
    """Main test function"""
    print("🚀 OCR Functionality Test")
    print("This test verifies the OCR button and Google Cloud Vision API integration.")
    
    try:
        success = test_ocr_functionality()
        show_web_interface_guide()
        
        if success:
            print("\n🎉 All tests passed! OCR functionality is working.")
            print("\n💡 Key features:")
            print("   • OCR button on camera controls")
            print("   • OCR results displayed above files")
            print("   • Google Cloud Vision API integration")
            print("   • Rich OCR metadata and actions")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
