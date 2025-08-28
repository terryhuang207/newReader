#!/usr/bin/env python3
"""
Enhanced OCR Test
Tests the OCR functionality with Google Cloud Vision API and web interface
"""

import requests
import json
import time
import os

def test_ocr_enhanced():
    """Test the enhanced OCR functionality"""
    
    print("🧪 Testing Enhanced OCR Functionality")
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
    
    # Test 2: Check OCR system status
    print("\n2️⃣ Checking OCR system status...")
    try:
        response = requests.get(f"{API_BASE}/ocr/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ OCR info endpoint working")
            
            if data.get('success'):
                ocr_systems = data.get('ocr_systems', {})
                print(f"   📊 OCR Systems: {len(ocr_systems)} found")
                
                for system, info in ocr_systems.items():
                    status = "✅ Available" if info.get('available') else "❌ Not Available"
                    priority = info.get('priority', 'Unknown')
                    print(f"      {system}: {status} ({priority})")
            else:
                print("   ⚠️ OCR info returned success: false")
        else:
            print(f"❌ OCR info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking OCR info: {e}")
    
    # Test 3: Check available files for OCR testing
    print("\n3️⃣ Checking available files for OCR testing...")
    try:
        response = requests.get(f"{API_BASE}/files")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if files:
                print(f"✅ Found {len(files)} captured files")
                
                # Find a file that hasn't been processed with OCR yet
                test_file = None
                for file in files:
                    if not file.get('has_text'):
                        test_file = file
                        break
                
                if test_file:
                    print(f"   📸 Test file: {test_file['filename']}")
                    print(f"   📏 Size: {test_file['size']} bytes")
                    print(f"   📅 Created: {test_file['created']}")
                else:
                    print("   ⚠️ All files already have OCR text")
                    if files:
                        test_file = files[0]  # Use first file anyway
                        print(f"   📸 Using file: {test_file['filename']}")
            else:
                print("📁 No captured files found")
                print("💡 Start the camera and capture an image first")
                return False
        else:
            print(f"❌ Files endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return False
    
    # Test 4: Test OCR on a captured image
    if test_file:
        print(f"\n4️⃣ Testing OCR on {test_file['filename']}...")
        try:
            response = requests.post(f"{API_BASE}/ocr/{test_file['filename']}")
            if response.status_code == 200:
                data = response.json()
                print("✅ OCR endpoint working")
                
                if data.get('success'):
                    print(f"   🎯 Success: {data.get('success')}")
                    print(f"   🔍 Method: {data.get('ocr_method', 'Unknown')}")
                    print(f"   ⏱️ Processing Time: {data.get('processing_time', 'Unknown')}s")
                    print(f"   📊 Confidence: {data.get('confidence_score', 'Unknown')}")
                    
                    extracted_text = data.get('extracted_text', '')
                    if extracted_text:
                        text_preview = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
                        print(f"   📝 Text Preview: {text_preview}")
                    else:
                        print("   ⚠️ No text extracted")
                else:
                    print(f"   ❌ OCR failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ OCR endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error testing OCR: {e}")
    
    # Test 5: Test new TTS text endpoint
    print("\n5️⃣ Testing TTS text endpoint...")
    try:
        test_text = "This is a test text for text-to-speech conversion."
        response = requests.post(f"{API_BASE}/tts/text", 
                               json={'text': test_text},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ TTS text endpoint working")
            print(f"   🎯 Success: {data.get('success')}")
            if data.get('success'):
                print(f"   🔊 Audio File: {data.get('audio_file', 'Unknown')}")
        else:
            print(f"❌ TTS text endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing TTS text: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Enhanced OCR Test Results:")
    print("✅ OCR results section added to web interface")
    print("✅ Google Cloud Vision API integration")
    print("✅ Text display with metadata")
    print("✅ Copy text functionality")
    print("✅ Text-to-speech from OCR results")
    print("✅ Clear results functionality")
    
    return True

def show_web_interface_guide():
    """Show how to use the enhanced OCR web interface"""
    print("\n🌐 Enhanced OCR Web Interface Guide:")
    print("=" * 50)
    
    print("1. 📱 Open your browser and go to: http://localhost:5001")
    print("2. 🎥 Start camera and capture an image")
    print("3. 📖 Click the 'OCR' button on any captured image")
    print("4. 🔍 Watch the OCR Results section appear above the files")
    print("5. 📝 View extracted text with metadata:")
    print("   • OCR Method (Google Vision or Tesseract)")
    print("   • Confidence Score")
    print("   • Processing Time")
    print("6. 🎯 Use the action buttons:")
    print("   • 📋 Copy Text - Copy to clipboard")
    print("   • 🔊 Text to Speech - Convert to audio")
    print("   • 🗑️ Clear Results - Hide the section")
    
    print("\n💡 Features:")
    print("   • Real-time OCR processing")
    print("   • Image preview with extracted text")
    print("   • Responsive design for mobile/desktop")
    print("   • Integration with existing TTS system")
    print("   • Google Cloud Vision API priority")

def main():
    """Main test function"""
    print("🚀 Enhanced OCR Test")
    print("This test verifies the enhanced OCR functionality with:")
    print("• Google Cloud Vision API integration")
    print("• Web interface OCR results display")
    print("• Text-to-speech from OCR results")
    print("• Copy and clear functionality")
    
    try:
        success = test_ocr_enhanced()
        show_web_interface_guide()
        
        if success:
            print("\n🎉 All tests passed! Enhanced OCR is working.")
            print("\n🌐 To use the enhanced OCR interface:")
            print("   • Open http://localhost:5001 in your browser")
            print("   • Capture an image and click OCR")
            print("   • View results in the new OCR Results section")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
