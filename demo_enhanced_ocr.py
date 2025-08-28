#!/usr/bin/env python3
"""
Enhanced OCR Demo
Demonstrates the enhanced OCR functionality with web interface
"""

import requests
import json
import time
import os

def demo_enhanced_ocr():
    """Demo the enhanced OCR functionality"""
    
    print("🎭 Enhanced OCR Demo")
    print("=" * 50)
    
    BASE_URL = "http://localhost:5001"
    API_BASE = f"{BASE_URL}/api"
    
    print("\n🌐 Web Interface Demo:")
    print("1. Open your browser and go to: http://localhost:5001")
    print("2. You'll see the enhanced interface with:")
    print("   • Camera capture section")
    print("   • OCR Results section (initially hidden)")
    print("   • Captured files section")
    print("   • Last captured image section")
    
    print("\n📸 Step-by-step OCR process:")
    print("1. Start the camera")
    print("2. Capture an image")
    print("3. Click the 'OCR' button on the captured image")
    print("4. Watch the OCR Results section appear above the files")
    print("5. View the extracted text with metadata")
    print("6. Use the action buttons:")
    print("   • 📋 Copy Text - Copy to clipboard")
    print("   • 🔊 Text to Speech - Convert to audio")
    print("   • 🗑️ Clear Results - Hide the section")
    
    print("\n🔍 OCR Results Section Features:")
    print("• Image preview of the processed image")
    print("• Extracted text display with proper formatting")
    print("• Metadata: OCR method, confidence, processing time")
    print("• Action buttons for text manipulation")
    print("• Responsive design for mobile and desktop")
    
    print("\n💡 Technical Features:")
    print("• Google Cloud Vision API integration (primary)")
    print("• Tesseract OCR fallback")
    print("• Smart text formatting and line break handling")
    print("• Real-time processing with loading states")
    print("• Error handling and user feedback")
    
    print("\n🎯 API Endpoints:")
    print("• POST /api/ocr/{filename} - Process image with OCR")
    print("• POST /api/tts/text - Convert text to speech")
    print("• GET /api/ocr/info - Check OCR system status")
    print("• GET /api/files - List captured files")
    
    print("\n🚀 Ready to test!")
    print("Open http://localhost:5001 in your browser and try the OCR functionality.")

def test_ocr_workflow():
    """Test the complete OCR workflow"""
    
    print("\n🧪 Testing OCR Workflow:")
    print("=" * 30)
    
    BASE_URL = "http://localhost:5001"
    API_BASE = f"{BASE_URL}/api"
    
    # Check if we have any captured images
    try:
        response = requests.get(f"{API_BASE}/files")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if files:
                print(f"✅ Found {len(files)} captured files")
                
                # Find a file that hasn't been processed with OCR
                test_file = None
                for file in files:
                    if not file.get('has_text'):
                        test_file = file
                        break
                
                if test_file:
                    print(f"📸 Test file: {test_file['filename']}")
                    print(f"📏 Size: {test_file['size']} bytes")
                    
                    # Test OCR
                    print(f"\n🔍 Testing OCR on {test_file['filename']}...")
                    ocr_response = requests.post(f"{API_BASE}/ocr/{test_file['filename']}")
                    
                    if ocr_response.status_code == 200:
                        ocr_data = ocr_response.json()
                        if ocr_data.get('success'):
                            print("✅ OCR successful!")
                            print(f"   Method: {ocr_data.get('ocr_method', 'Unknown')}")
                            print(f"   Time: {ocr_data.get('processing_time', 'Unknown')}s")
                            print(f"   Confidence: {ocr_data.get('confidence_score', 'Unknown')}")
                            
                            # Test TTS on extracted text
                            extracted_text = ocr_data.get('extracted_text', '')
                            if extracted_text and extracted_text.strip():
                                print(f"\n🔊 Testing TTS on extracted text...")
                                tts_response = requests.post(f"{API_BASE}/tts/text", 
                                                           json={'text': extracted_text[:100]},
                                                           headers={'Content-Type': 'application/json'})
                                
                                if tts_response.status_code == 200:
                                    tts_data = tts_response.json()
                                    if tts_data.get('success'):
                                        print("✅ TTS successful!")
                                        print(f"   Audio file: {tts_data.get('audio_file', 'Unknown')}")
                                    else:
                                        print(f"❌ TTS failed: {tts_data.get('message', 'Unknown error')}")
                                else:
                                    print(f"❌ TTS endpoint error: {tts_response.status_code}")
                            else:
                                print("⚠️ No text extracted, skipping TTS test")
                        else:
                            print(f"❌ OCR failed: {ocr_data.get('error', 'Unknown error')}")
                    else:
                        print(f"❌ OCR endpoint error: {ocr_response.status_code}")
                else:
                    print("⚠️ All files already have OCR text")
            else:
                print("📁 No captured files found")
                print("💡 Start the camera and capture an image first")
        else:
            print(f"❌ Files endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")

def main():
    """Main demo function"""
    print("🎉 Enhanced OCR Interface Demo")
    print("This demo showcases the new OCR functionality:")
    print("• OCR Results section in the web interface")
    print("• Google Cloud Vision API integration")
    print("• Text display with metadata")
    print("• Copy and TTS functionality")
    
    try:
        # Check if Flask app is running
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("\n✅ Flask app is running")
            demo_enhanced_ocr()
            test_ocr_workflow()
            
            print("\n🎯 Demo Summary:")
            print("✅ Enhanced OCR interface implemented")
            print("✅ OCR Results section added above files")
            print("✅ Google Cloud Vision API integration")
            print("✅ Text display with metadata")
            print("✅ Copy text functionality")
            print("✅ Text-to-speech from OCR results")
            print("✅ Clear results functionality")
            print("✅ Responsive design for mobile/desktop")
            
            print("\n🌐 Open http://localhost:5001 in your browser to see it in action!")
            
        else:
            print(f"❌ Flask app not responding: {response.status_code}")
            print("💡 Make sure to run: python app.py")
            
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Flask app")
        print("💡 Make sure to run: python app.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
