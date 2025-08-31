# Story Reader - Product Requirements Document (Updated)

## 📋 **Product Overview**

**Product Name**: Story Reader  
**Version**: 2.0  
**Last Updated**: August 30, 2025  
**Target Platform**: Mobile Web Application (Mobile-First Design)

### 🎯 **Product Vision**
A mobile-optimized web application that captures book pages using device cameras, extracts text via OCR, and converts text to high-quality speech using Google Cloud services.

---

## 🚀 **Core Features**

### 1. **Mobile Camera Integration**
- **Primary Function**: Real-time camera access via mobile device
- **Technology**: HTML5 `getUserMedia` API with HTTPS requirement
- **Camera Modes**: 
  - Environment-facing camera (back camera) preferred
  - Progressive fallback constraints for device compatibility
- **Video Display**: 
  - Dynamic sizing that matches actual camera resolution
  - Real-time resolution indicator
  - Responsive design for all mobile screen sizes
  - Aspect ratio preservation with `object-fit: contain`

### 2. **Image Capture System**
- **Capture Method**: Canvas-based image capture from video stream
- **Image Quality**: JPEG format at 95% quality
- **Dimensions**: Exact match to video stream dimensions (no cropping/stretching)
- **File Management**: Automatic timestamped naming convention
- **Storage**: Local server storage with metadata tracking

### 3. **OCR (Optical Character Recognition)**
- **Primary Engine**: Google Cloud Vision API
- **Fallback**: None (Google Cloud Vision is required)
- **Features**:
  - High-accuracy text extraction
  - Confidence scoring
  - Processing time tracking
  - Error handling and user feedback
- **Output**: Plain text with metadata (method, confidence, processing time)

### 4. **Text-to-Speech (TTS)**
- **Primary Engine**: Google Cloud Text-to-Speech API
- **Voice Quality**: High-quality neural voices (en-US-Wavenet-D)
- **Fallback**: gTTS (Google Text-to-Speech free version)
- **Audio Controls**:
  - Play button to start TTS conversion
  - Stop button to halt audio playback
  - Audio plays once until completion
  - Real-time status notifications
- **Audio Format**: MP3 with configurable parameters (rate, pitch, volume)

### 5. **User Interface**
- **Design Philosophy**: Mobile-first responsive design
- **Layout**: Single-page application with collapsible sections
- **Navigation**: Touch-optimized buttons and controls
- **Responsive Breakpoints**:
  - Desktop: >768px
  - Tablet: ≤768px
  - Mobile: ≤480px
  - Small Mobile: ≤375px

---

## 🛠 **Technical Architecture**

### **Backend (Flask)**
- **Framework**: Flask with CORS support
- **Security**: HTTPS with self-signed certificates
- **APIs**:
  - `/api/upload/mobile` - Image upload endpoint
  - `/api/ocr/<filename>` - OCR processing endpoint
  - `/api/tts/text` - Text-to-speech conversion
  - `/api/tts/<filename>` - TTS for OCR results
  - `/api/files` - File listing and management
  - `/api/ocr/info` - System status and configuration

### **Frontend (HTML5/CSS3/JavaScript)**
- **Camera Access**: `getUserMedia` API with progressive constraints
- **Video Processing**: Canvas API for image capture
- **Audio Playback**: HTML5 Audio API with event handling
- **Responsive Design**: CSS Grid and Flexbox with media queries
- **State Management**: JavaScript with global variables for camera/audio state

### **External Services**
- **Google Cloud Vision API**: OCR processing
- **Google Cloud Text-to-Speech API**: High-quality speech synthesis
- **Authentication**: Service account JSON credentials

---

## 📱 **Mobile Optimization**

### **Camera Requirements**
- **HTTPS**: Required for camera access in modern browsers
- **Permissions**: Camera permission must be granted
- **Browser Support**: Modern browsers with `getUserMedia` support
- **Device Compatibility**: iOS Safari, Chrome Mobile, Firefox Mobile

### **Responsive Design**
- **Video Sizing**: Dynamic height based on actual camera resolution
- **Button Sizing**: Minimum 44px touch targets
- **Typography**: Scalable font sizes for readability
- **Spacing**: Optimized padding and margins for touch interaction

### **Performance**
- **Image Compression**: 95% JPEG quality for optimal file size
- **Audio Streaming**: Efficient MP3 playback
- **Caching**: Browser caching for static assets
- **Loading States**: Visual feedback during processing

---

## 🔧 **Configuration & Setup**

### **Environment Requirements**
- **Python**: 3.12+
- **Dependencies**: 
  - Flask, Flask-CORS
  - OpenCV (cv2), NumPy
  - Google Cloud Vision, Google Cloud Text-to-Speech
  - gTTS (fallback)
- **SSL Certificates**: Self-signed certificates for HTTPS
- **Firewall**: Port 5001 must be open for network access

### **Google Cloud Setup**
- **Service Account**: JSON credentials file required
- **APIs Enabled**:
  - Cloud Vision API
  - Cloud Text-to-Speech API
- **Billing**: Pay-per-use model

---

## 🎨 **User Experience**

### **Workflow**
1. **Access**: Navigate to `https://[IP]:5001` on mobile device
2. **Camera**: Click "Start Mobile Camera" and grant permissions
3. **Capture**: Position book page and click "Quick Capture"
4. **OCR**: Click "OCR" button to extract text
5. **TTS**: Click "🔊 Text to Speech" to hear the text
6. **Control**: Use "⏹️ Stop Audio" to halt playback

### **Visual Feedback**
- **Status Notifications**: Real-time feedback for all actions
- **Loading Indicators**: Progress feedback during processing
- **Error Handling**: Clear error messages with suggestions
- **Resolution Display**: Live camera resolution indicator

### **Accessibility**
- **Touch Targets**: Minimum 44px for all interactive elements
- **Color Contrast**: High contrast for readability
- **Audio Feedback**: Visual notifications for audio events
- **Error States**: Clear indication of system status

---

## 📊 **Success Metrics**

### **Performance Targets**
- **Camera Startup**: <3 seconds
- **Image Capture**: <1 second
- **OCR Processing**: <5 seconds
- **TTS Generation**: <3 seconds
- **Audio Playback**: Immediate start

### **Quality Targets**
- **OCR Accuracy**: >95% for clear text
- **Audio Quality**: High-quality neural voice synthesis
- **Mobile Compatibility**: 100% on modern mobile browsers
- **Responsive Design**: Optimal on all screen sizes

---

## 🔒 **Security & Privacy**

### **Data Handling**
- **Images**: Stored locally on server, not transmitted to external services
- **Text**: Processed by Google Cloud APIs, not stored permanently
- **Audio**: Generated locally, stored temporarily
- **Credentials**: Secure service account authentication

### **Network Security**
- **HTTPS**: Required for camera access and secure communication
- **CORS**: Configured for cross-origin requests
- **Firewall**: Controlled port access

---

## 🚀 **Future Enhancements**

### **Planned Features**
- **Multiple Languages**: Support for non-English OCR and TTS
- **Voice Selection**: Multiple TTS voice options
- **Batch Processing**: Multiple image processing
- **Cloud Storage**: Optional cloud backup of images
- **Offline Mode**: Local OCR processing capability

### **Technical Improvements**
- **Progressive Web App**: PWA capabilities for app-like experience
- **WebRTC**: Enhanced camera controls
- **Service Workers**: Offline functionality
- **Push Notifications**: Processing completion alerts

---

## 📝 **Change Log**

### **Version 2.0 (August 30, 2025)**
- ✅ **Dynamic Video Sizing**: Video window matches camera resolution exactly
- ✅ **Enhanced TTS Controls**: Play/Stop buttons with audio control
- ✅ **Google Cloud TTS**: High-quality neural voice synthesis
- ✅ **Mobile Optimization**: Responsive design for all screen sizes
- ✅ **Real-time Resolution Display**: Live camera resolution indicator
- ✅ **Improved Error Handling**: Better user feedback and error recovery
- ✅ **Audio State Management**: Proper audio playback control
- ✅ **Responsive TTS Buttons**: Mobile-optimized button sizing

### **Version 1.0 (Previous)**
- Basic camera access and image capture
- Google Cloud Vision OCR integration
- Simple TTS with gTTS
- Basic mobile interface

---

## 🎯 **Success Criteria**

The Story Reader application successfully meets its requirements when:

1. **Mobile users can access the camera** via HTTPS on their devices
2. **Images are captured** with exact dimensions matching the video display
3. **Text is extracted** with high accuracy using Google Cloud Vision
4. **Text is converted to speech** using high-quality Google Cloud TTS
5. **Audio playback is controlled** with play/stop functionality
6. **Interface is responsive** and optimized for all mobile screen sizes
7. **System provides clear feedback** for all user actions and system states

---

*This PRD reflects the current state of the Story Reader application as of August 30, 2025, including all implemented features and optimizations.*
