# Mobile Camera Setup Guide

## Overview
The Story Reader app now supports mobile camera access via the local network. This allows you to use your mobile device's camera to capture book pages directly through the web interface.

## Features
- 📱 **Mobile Device Detection**: Automatically detects mobile devices and switches to mobile camera mode
- 📷 **Direct Camera Access**: Uses the device's camera via getUserMedia API
- 🎯 **Back Camera Priority**: Automatically selects the back camera for better document capture
- 📸 **High-Quality Capture**: Captures images at up to 1280x720 resolution
- 🌐 **Local Network Access**: Works over your local WiFi network

## Setup Instructions

### 1. Start the Server
```bash
python3 app.py
```

### 2. Find Your Local IP Address
The server will start on `0.0.0.0:5001`. Find your local IP address:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### 3. Access from Mobile Device
1. Connect your mobile device to the same WiFi network as your computer
2. Open a web browser on your mobile device
3. Navigate to: `http://YOUR_LOCAL_IP:5001`
   - Example: `http://10.0.0.15:5001`

### 4. Grant Camera Permissions
When you first access the app on your mobile device:
1. Click "📱 Start Mobile Camera"
2. Grant camera permissions when prompted
3. The app will automatically use your device's back camera

## Mobile Interface Features

### Automatic Detection
- The app automatically detects mobile devices
- Shows mobile-specific UI indicators
- Displays mobile camera features and benefits

### Touch-Friendly Controls
- Larger buttons optimized for touch
- Responsive design that works on all screen sizes
- Touch-to-capture functionality

### Camera Controls
- **Start Mobile Camera**: Initiates camera access
- **Capture Photo**: Takes a high-quality photo
- **Stop Camera**: Releases camera resources

## Technical Details

### Mobile Camera Implementation
- Uses `navigator.mediaDevices.getUserMedia()` API
- Automatically selects back camera with `facingMode: 'environment'`
- Captures images using HTML5 Canvas
- Uploads images to server via FormData

### File Naming
Mobile captures are saved with the prefix `mobile_` followed by timestamp:
- Example: `mobile_20250128_143022_p001.jpg`

### Supported Devices
- iOS Safari (iOS 11+)
- Android Chrome (Android 5+)
- Other modern mobile browsers with getUserMedia support

## Troubleshooting

### Camera Permission Issues
- Ensure you grant camera permissions when prompted
- Check browser settings if camera access is denied
- Try refreshing the page and granting permissions again

### Network Connection Issues
- Verify both devices are on the same WiFi network
- Check that the server is running and accessible
- Try accessing the local IP address directly

### Camera Not Working
- Close other camera applications (Camera app, FaceTime, etc.)
- Restart the browser
- Try a different mobile browser

## Security Notes
- The app runs on your local network only
- No images are sent to external servers
- All processing happens locally on your computer
- Camera access is only requested when needed

## Browser Compatibility
- **iOS**: Safari 11+, Chrome for iOS
- **Android**: Chrome, Firefox, Samsung Internet
- **Desktop**: Chrome, Firefox, Safari, Edge

## Performance Tips
- Use a stable WiFi connection for best performance
- Close unnecessary apps on your mobile device
- Ensure good lighting for better image quality
- Hold the device steady when capturing
