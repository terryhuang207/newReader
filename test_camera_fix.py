#!/usr/bin/env python3
"""
Comprehensive Camera Test Script
Tests the enhanced camera functionality and provides detailed diagnostics
"""

import requests
import json
import time
import os
import subprocess
import sys

# Configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint and return the response"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
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

def check_system_camera_devices():
    """Check system-level camera device information"""
    print_section("System Camera Device Check")
    
    try:
        # Check if we're on macOS
        if sys.platform == "darwin":
            print("🍎 macOS detected - checking camera devices...")
            
            # Check for camera devices using system_profiler
            try:
                result = subprocess.run(['system_profiler', 'SPCameraDataType'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✅ Camera devices found:")
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Camera:' in line or 'Webcam:' in line:
                            print(f"   📷 {line.strip()}")
                else:
                    print("⚠️ Could not retrieve camera device information")
            except Exception as e:
                print(f"⚠️ Error checking system camera info: {e}")
            
            # Check camera permissions
            print("\n🔐 Checking camera permissions...")
            try:
                result = subprocess.run(['tccutil', 'reset', 'Camera'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ Camera permissions can be reset")
                else:
                    print("⚠️ Camera permissions check failed")
            except Exception:
                print("⚠️ Could not check camera permissions (requires admin)")
                
        else:
            print(f"🖥️ Platform: {sys.platform}")
            print("Camera device check not implemented for this platform")
            
    except Exception as e:
        print(f"❌ System camera check failed: {e}")

def test_camera_diagnostics():
    """Test the camera diagnostics endpoint"""
    print_section("Camera Diagnostics API Test")
    
    print("🔍 Getting comprehensive camera diagnostics...")
    diagnostics = test_api_endpoint("/camera/diagnostics")
    
    if diagnostics:
        print("✅ Diagnostics retrieved successfully!")
        
        # Display system information
        if 'system_info' in diagnostics:
            sys_info = diagnostics['system_info']
            print(f"\n💻 System Information:")
            print(f"   Platform: {sys_info.get('platform', 'Unknown')}")
            print(f"   OpenCV Version: {sys_info.get('opencv_version', 'Unknown')}")
            print(f"   Python Version: {sys_info.get('python_version', 'Unknown')}")
        
        # Display camera status
        if 'camera_status' in diagnostics:
            cam_status = diagnostics['camera_status']
            print(f"\n📷 Camera Status:")
            print(f"   Active: {cam_status.get('active', 'Unknown')}")
            print(f"   Opened: {cam_status.get('opened', 'Unknown')}")
        
        # Display available devices
        if 'device_scan' in diagnostics:
            device_scan = diagnostics['device_scan']
            available_devices = device_scan.get('available_devices', [])
            print(f"\n🔍 Device Scan Results:")
            print(f"   Available Devices: {available_devices}")
            
            if 'device_details' in device_scan:
                for device in device_scan['device_details']:
                    print(f"\n   📷 Device {device.get('device_id', 'Unknown')}:")
                    print(f"      Status: {device.get('status', 'Unknown')}")
                    if 'resolution' in device:
                        print(f"      Resolution: {device['resolution']}")
                    if 'fps' in device:
                        print(f"      FPS: {device['fps']}")
                    if 'frame_capture' in device:
                        print(f"      Frame Capture: {device['frame_capture']}")
        
        # Display permissions
        if 'permissions_check' in diagnostics:
            perms = diagnostics['permissions_check']
            print(f"\n🔐 Permissions Check:")
            print(f"   Camera Access: {perms.get('camera_access', 'Unknown')}")
            print(f"   File Access: {perms.get('file_access', 'Unknown')}")
        
        # Display recommendations
        if 'recommendations' in diagnostics and diagnostics['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in diagnostics['recommendations']:
                print(f"   • {rec}")
        
        return diagnostics
    else:
        print("❌ Failed to retrieve camera diagnostics")
        return None

def test_camera_status():
    """Test the enhanced camera status endpoint"""
    print_section("Enhanced Camera Status Test")
    
    print("📊 Getting detailed camera status...")
    status = test_api_endpoint("/camera/status")
    
    if status:
        print("✅ Camera status retrieved successfully!")
        print(f"   Active: {status.get('active', 'Unknown')}")
        print(f"   Opened: {status.get('opened', 'Unknown')}")
        
        if 'available_devices' in status:
            print(f"   Available Devices: {status.get('available_devices', [])}")
        
        if 'system_info' in status:
            sys_info = status['system_info']
            print(f"   Platform: {sys_info.get('platform', 'Unknown')}")
            print(f"   Camera Detection: {sys_info.get('camera_detection', 'Unknown')}")
        
        return status
    else:
        print("❌ Failed to retrieve camera status")
        return None

def test_camera_start_stop():
    """Test camera start and stop functionality"""
    print_section("Camera Start/Stop Test")
    
    # Check initial status
    print("🔍 Checking initial camera status...")
    initial_status = test_api_endpoint("/camera/status")
    if initial_status:
        print(f"   Initial Status: Active={initial_status.get('active')}, Opened={initial_status.get('opened')}")
    
    # Start camera
    print("\n🚀 Starting camera...")
    start_result = test_api_endpoint("/camera/start", method="POST")
    if start_result:
        print(f"✅ Camera start result: {start_result.get('message', 'Unknown')}")
        
        # Wait a moment for camera to initialize
        print("⏳ Waiting for camera initialization...")
        time.sleep(3)
        
        # Check status after start
        print("\n📊 Checking camera status after start...")
        status_after_start = test_api_endpoint("/camera/status")
        if status_after_start:
            print(f"   Status after start: Active={status_after_start.get('active')}, Opened={status_after_start.get('opened')}")
            
            # Check camera info if available
            if 'camera_info' in status_after_start:
                cam_info = status_after_start['camera_info']
                print(f"   Camera Info: {cam_info.get('width', 'Unknown')}x{cam_info.get('height', 'Unknown')} @ {cam_info.get('fps', 'Unknown')}fps")
        
        # Stop camera
        print("\n🛑 Stopping camera...")
        stop_result = test_api_endpoint("/camera/stop", method="POST")
        if stop_result:
            print(f"✅ Camera stop result: {stop_result.get('message', 'Unknown')}")
        
        # Check final status
        print("\n📊 Checking final camera status...")
        final_status = test_api_endpoint("/camera/status")
        if final_status:
            print(f"   Final Status: Active={final_status.get('active')}, Opened={final_status.get('opened')}")
        
        return True
    else:
        print("❌ Camera start failed")
        return False

def test_video_stream():
    """Test video stream functionality"""
    print_section("Video Stream Test")
    
    print("🎥 Testing video stream endpoint...")
    
    try:
        # Start camera first
        start_result = test_api_endpoint("/camera/start", method="POST")
        if not start_result or not start_result.get('success'):
            print("❌ Cannot test video stream - camera failed to start")
            return False
        
        # Wait for camera to initialize
        time.sleep(2)
        
        # Test video stream
        print("📹 Testing video stream...")
        stream_response = requests.get(f"{API_BASE}/stream", stream=True, timeout=5)
        
        if stream_response.status_code == 200:
            print("✅ Video stream endpoint responding")
            
            # Check if we're getting actual video data
            content_type = stream_response.headers.get('content-type', '')
            if 'multipart/x-mixed-replace' in content_type:
                print("✅ Video stream content type correct")
                
                # Try to read a few frames
                frame_count = 0
                for chunk in stream_response.iter_content(chunk_size=1024):
                    if b'--frame' in chunk:
                        frame_count += 1
                    if frame_count >= 3:  # Got at least 3 frames
                        break
                
                print(f"✅ Video stream frames detected: {frame_count}")
                
            else:
                print(f"⚠️ Unexpected content type: {content_type}")
        else:
            print(f"❌ Video stream failed with status: {stream_response.status_code}")
        
        # Stop camera
        test_api_endpoint("/camera/stop", method="POST")
        return True
        
    except Exception as e:
        print(f"❌ Video stream test failed: {e}")
        return False

def provide_troubleshooting_guide():
    """Provide comprehensive troubleshooting guide"""
    print_section("Troubleshooting Guide")
    
    print("🔧 Common Camera Issues and Solutions:")
    print()
    
    print("1. 📱 Camera Permission Issues (macOS):")
    print("   • Go to System Preferences > Security & Privacy > Camera")
    print("   • Ensure your terminal/application has camera access")
    print("   • Try: tccutil reset Camera (requires admin)")
    print()
    
    print("2. 🎥 Camera Already in Use:")
    print("   • Close FaceTime, Photo Booth, Zoom, or other camera apps")
    print("   • Check Activity Monitor for camera-using processes")
    print("   • Restart your computer if needed")
    print()
    
    print("3. 🔌 Hardware Issues:")
    print("   • Check USB connections for external cameras")
    print("   • Try different USB ports")
    print("   • Test camera in other applications")
    print()
    
    print("4. 🐍 Python/OpenCV Issues:")
    print("   • Ensure OpenCV is properly installed")
    print("   • Check Python environment and dependencies")
    print("   • Try: pip install --upgrade opencv-python")
    print()
    
    print("5. 🌐 Network/Port Issues:")
    print("   • Ensure Flask app is running on correct port")
    print("   • Check firewall settings")
    print("   • Verify localhost access")

def main():
    """Main test function"""
    print("🔍 Story Reader Enhanced Camera Test & Diagnostics")
    print(f"🌐 Testing against: {BASE_URL}")
    
    try:
        # Check basic connectivity
        print("\n🔗 Testing basic connectivity...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Web interface accessible")
        else:
            print(f"❌ Web interface not accessible: {response.status_code}")
            return
        
        # Run comprehensive tests
        check_system_camera_devices()
        test_camera_diagnostics()
        test_camera_status()
        test_camera_start_stop()
        test_video_stream()
        
        # Provide troubleshooting guide
        provide_troubleshooting_guide()
        
        print_section("Test Summary")
        print("✅ All camera tests completed!")
        print(f"🌐 Web interface: {BASE_URL}")
        print("📖 Check the troubleshooting guide above for any issues")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
