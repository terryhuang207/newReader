#!/usr/bin/env python3
"""
Minimal Demo: Last Capture Display
Demonstrates the last captured image display functionality
"""

import requests
import json
import time
from datetime import datetime

def demo_last_capture():
    """Demo the last capture display functionality"""
    
    # Configuration
    BASE_URL = "http://localhost:5001"
    API_BASE = f"{BASE_URL}/api"
    
    print("🎯 Last Capture Display Demo")
    print("=" * 50)
    
    # Step 1: Check if the Flask app is running
    print("\n1️⃣ Checking Flask app status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"❌ Flask app returned status: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        print("💡 Make sure to run: python app.py")
        return
    
    # Step 2: Check current files
    print("\n2️⃣ Checking current captured files...")
    try:
        response = requests.get(f"{API_BASE}/files")
        files_data = response.json()
        
        if files_data.get('files'):
            print(f"✅ Found {len(files_data['files'])} captured files")
            latest_file = files_data['files'][0]  # First file is most recent
            print(f"   📸 Latest: {latest_file['filename']}")
            print(f"   📏 Size: {latest_file['size']} bytes")
            print(f"   📅 Created: {latest_file['created']}")
        else:
            print("📁 No captured files found")
            print("💡 Start the camera and capture an image first")
            return
            
    except Exception as e:
        print(f"❌ Error checking files: {e}")
        return
    
    # Step 3: Display the last captured image info
    print("\n3️⃣ Last Captured Image Display:")
    print("   🌐 Open your browser and go to: http://localhost:5001")
    print("   📸 Look for the 'Last Captured Image' section below the files")
    print("   🖼️ It should show:")
    print("      • The actual image thumbnail")
    print("      • Date and time of capture")
    print("      • File size in KB")
    print("      • Image dimensions")
    
    # Step 4: Test capture functionality
    print("\n4️⃣ To test live capture:")
    print("   🎥 Click 'Start Camera' on the web interface")
    print("   📸 Click 'Capture' or press Spacebar")
    print("   🔄 The last capture display will update automatically")
    
    # Step 5: Show API endpoints
    print("\n5️⃣ API Endpoints used:")
    print("   📁 GET /api/files - List all captured files")
    print("   📸 POST /api/capture - Capture new image")
    print("   🖼️ GET /api/files/{filename} - Get image file")
    
    print("\n" + "=" * 50)
    print("🎉 Demo complete! Check the web interface at http://localhost:5001")

def show_web_interface_guide():
    """Show how to use the web interface"""
    print("\n🌐 Web Interface Guide:")
    print("=" * 50)
    
    print("1. 📱 Open your browser and go to: http://localhost:5001")
    print("2. 🎥 Click 'Start Camera' to activate the camera")
    print("3. 📸 Click 'Capture' button or press Spacebar to take a photo")
    print("4. 🔍 Look below the 'Captured Files' section for:")
    print("   📸 Last Captured Image - Shows the most recent photo")
    print("   📅 Date - When the image was captured")
    print("   ⏰ Time - Exact time of capture")
    print("   📏 Size - File size in KB")
    print("   🖼️ Dimensions - Image width × height")
    
    print("\n💡 Features:")
    print("   • Image automatically updates after each capture")
    print("   • Responsive design - works on mobile and desktop")
    print("   • Image thumbnail with orange border styling")
    print("   • Detailed metadata display")
    print("   • Hides when no images are available")

def main():
    """Main demo function"""
    print("🚀 Last Capture Display Demo")
    print("This demo shows how the last captured image is displayed")
    print("underneath the captured files section in the web interface.")
    
    try:
        demo_last_capture()
        show_web_interface_guide()
        
        print("\n🎯 Key Implementation Details:")
        print("=" * 50)
        print("• HTML: Added last-capture-section with image and metadata")
        print("• CSS: Styled with orange theme, responsive layout")
        print("• JavaScript: updateLastCaptureDisplay() function")
        print("• Auto-updates: Called after capture and file load")
        print("• Filename parsing: Extracts date/time from YYYYMMDD_HHMMSS format")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
