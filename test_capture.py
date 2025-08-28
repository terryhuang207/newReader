#!/usr/bin/env python3
"""
Test script for Story Reader capture functionality
This script demonstrates the various API endpoints and capture features
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint and return the response"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ {method} {endpoint} failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def test_camera_control():
    """Test camera control endpoints"""
    print_section("Testing Camera Control")
    
    # Check initial status
    print("📷 Checking initial camera status...")
    status = test_api_endpoint("/camera/status")
    if status:
        print(f"✅ Camera status: {json.dumps(status, indent=2)}")
    
    # Start camera
    print("\n📷 Starting camera...")
    start_result = test_api_endpoint("/camera/start", method="POST")
    if start_result:
        print(f"✅ Camera start result: {json.dumps(start_result, indent=2)}")
    
    # Check status after start
    print("\n📷 Checking camera status after start...")
    status = test_api_endpoint("/camera/status")
    if status:
        print(f"✅ Camera status: {json.dumps(status, indent=2)}")
    
    # Stop camera
    print("\n📷 Stopping camera...")
    stop_result = test_api_endpoint("/camera/stop", method="POST")
    if stop_result:
        print(f"✅ Camera stop result: {json.dumps(stop_result, indent=2)}")

def test_capture_functionality():
    """Test capture functionality"""
    print_section("Testing Capture Functionality")
    
    # Start camera first
    print("📷 Starting camera for capture test...")
    start_result = test_api_endpoint("/camera/start", method="POST")
    if not start_result or not start_result.get('success'):
        print("❌ Cannot test capture - camera failed to start")
        return
    
    # Wait a moment for camera to initialize
    print("⏳ Waiting for camera to initialize...")
    time.sleep(2)
    
    # Test capture
    print("📸 Testing image capture...")
    capture_result = test_api_endpoint("/capture", method="POST")
    if capture_result:
        if capture_result.get('success'):
            print(f"✅ Capture successful: {capture_result.get('filename')}")
            print(f"📊 Image info: {json.dumps(capture_result.get('image_info', {}), indent=2)}")
        else:
            print(f"❌ Capture failed: {capture_result.get('message')}")
    
    # Check capture statistics
    print("\n📊 Checking capture statistics...")
    stats = test_api_endpoint("/capture/stats")
    if stats:
        print(f"✅ Capture stats: {json.dumps(stats.get('statistics', {}), indent=2)}")
    
    # Stop camera
    print("\n📷 Stopping camera...")
    test_api_endpoint("/camera/stop", method="POST")

def test_file_management():
    """Test file management endpoints"""
    print_section("Testing File Management")
    
    # List files
    print("📁 Listing captured files...")
    files = test_api_endpoint("/files")
    if files:
        file_count = len(files.get('files', []))
        print(f"✅ Found {file_count} files")
        
        if file_count > 0:
            # Get info for first file
            first_file = files['files'][0]['filename']
            print(f"\n📊 Getting info for {first_file}...")
            file_info = test_api_endpoint(f"/files/{first_file}/info")
            if file_info:
                print(f"✅ File info: {json.dumps(file_info.get('info', {}), indent=2)}")

def test_ocr_and_tts():
    """Test OCR and TTS functionality"""
    print_section("Testing OCR and TTS")
    
    # List files to find an image
    files = test_api_endpoint("/files")
    if not files or not files.get('files'):
        print("❌ No files available for OCR/TTS testing")
        return
    
    # Find an image file
    image_file = None
    for file_info in files['files']:
        if file_info['filename'].endswith('.jpg'):
            image_file = file_info['filename']
            break
    
    if not image_file:
        print("❌ No image files found for OCR testing")
        return
    
    print(f"🔤 Testing OCR on {image_file}...")
    ocr_result = test_api_endpoint(f"/ocr/{image_file}", method="POST")
    if ocr_result:
        if ocr_result.get('success'):
            print(f"✅ OCR successful")
            text_preview = ocr_result.get('text', '')[:100]
            print(f"📝 Text preview: {text_preview}...")
        else:
            print(f"❌ OCR failed: {ocr_result.get('message', 'Unknown error')}")
    
    # Test TTS
    print(f"\n🎵 Testing TTS on {image_file}...")
    tts_result = test_api_endpoint(f"/tts/{image_file}", method="POST")
    if tts_result:
        if tts_result.get('success'):
            print(f"✅ TTS successful: {tts_result.get('audio_file')}")
        else:
            print(f"❌ TTS failed: {tts_result.get('message', 'Unknown error')}")

def main():
    """Main test function"""
    print("🚀 Story Reader Capture Functionality Test")
    print(f"🌐 Testing against: {BASE_URL}")
    
    try:
        # Test basic connectivity
        print("\n🔗 Testing basic connectivity...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Web interface accessible")
        else:
            print(f"❌ Web interface not accessible: {response.status_code}")
            return
        
        # Run tests
        test_camera_control()
        test_capture_functionality()
        test_file_management()
        test_ocr_and_tts()
        
        print_section("Test Summary")
        print("✅ All tests completed!")
        print(f"🌐 Web interface: {BASE_URL}")
        print("📱 You can now open the web interface in your browser")
        print("📷 Use the web interface to capture images with your camera")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
