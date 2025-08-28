#!/usr/bin/env python3
"""
Quick Camera Test Script
Immediate camera troubleshooting and testing
"""

import cv2
import sys
import os

def test_camera_directly():
    """Test camera directly using OpenCV"""
    print("🔍 Quick Camera Test")
    print("=" * 40)
    
    # Check OpenCV version
    print(f"📦 OpenCV Version: {cv2.__version__}")
    
    # Test camera devices
    print("\n🔍 Testing camera devices...")
    working_devices = []
    
    for device_id in range(5):  # Test first 5 devices
        try:
            print(f"   Testing device {device_id}...")
            cap = cv2.VideoCapture(device_id)
            
            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"   ✅ Device {device_id}: Working (Resolution: {frame.shape[1]}x{frame.shape[0]})")
                    working_devices.append(device_id)
                else:
                    print(f"   ⚠️ Device {device_id}: Opened but can't read frames")
                cap.release()
            else:
                print(f"   ❌ Device {device_id}: Not available")
                
        except Exception as e:
            print(f"   ❌ Device {device_id}: Error - {e}")
    
    print(f"\n📊 Summary: {len(working_devices)} working camera device(s) found")
    
    if working_devices:
        print(f"   Working devices: {working_devices}")
        
        # Test the first working device
        test_device = working_devices[0]
        print(f"\n🎥 Testing device {test_device} with live preview...")
        print("   Press 'q' to quit, 'c' to capture test image")
        
        cap = cv2.VideoCapture(test_device)
        if cap.isOpened():
            # Set reasonable resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if ret:
                    frame_count += 1
                    
                    # Add frame counter and instructions
                    cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to quit, 'c' to capture", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Camera Test', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('c'):
                        # Capture test image
                        test_image_path = f"camera_test_device_{test_device}.jpg"
                        cv2.imwrite(test_image_path, frame)
                        print(f"   📸 Test image captured: {test_image_path}")
                
                if frame_count > 1000:  # Prevent infinite loop
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            print(f"   ✅ Camera test completed. {frame_count} frames processed.")
        else:
            print("   ❌ Failed to open camera for live test")
    else:
        print("   ❌ No working camera devices found")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if camera is connected")
        print("   2. Close other camera applications (FaceTime, Zoom, etc.)")
        print("   3. Check camera permissions in System Preferences")
        print("   4. Try restarting your computer")

def check_system_info():
    """Check system information"""
    print("\n💻 System Information")
    print("=" * 40)
    
    print(f"Platform: {sys.platform}")
    print(f"Python Version: {sys.version}")
    
    # Check if we're on macOS
    if sys.platform == "darwin":
        print("🍎 macOS detected")
        print("\n🔐 Camera Permission Check:")
        print("   Go to: System Preferences > Security & Privacy > Camera")
        print("   Ensure your terminal/application has camera access")
        
        # Try to check camera permissions using system command
        try:
            import subprocess
            result = subprocess.run(['tccutil', 'reset', 'Camera'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ Camera permissions can be reset (requires admin)")
            else:
                print("   ⚠️ Camera permissions check failed")
        except Exception:
            print("   ⚠️ Could not check camera permissions")
    
    print(f"\n📁 Current Directory: {os.getcwd()}")
    print(f"📁 Python Path: {sys.executable}")

def main():
    """Main function"""
    try:
        check_system_info()
        test_camera_directly()
        
        print("\n" + "=" * 40)
        print("✅ Camera test completed!")
        print("📖 Check the troubleshooting tips above if issues persist")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Try running with: python3 quick_camera_test.py")

if __name__ == "__main__":
    main()
