# 📚 Story Reader

A lightweight Flask-based web application that captures book pages via camera and converts them to text and audio. Perfect for students, researchers, and anyone who needs to digitize printed text.

## ✨ Features

- **📷 Camera Capture**: Real-time camera feed with multiple capture methods
- **🔤 OCR Processing**: Extract text from captured images using Tesseract
- **🎵 Text-to-Speech**: Convert extracted text to audio files
- **💾 File Management**: Organize and manage captured pages
- **🌐 Web Interface**: Beautiful, responsive web UI accessible from any device
- **🔒 Local & LAN**: Runs locally and accessible over your local network

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam or camera device
- Tesseract OCR engine (for text extraction)

### Installation

1. **Clone or download the project**
   ```bash
   cd simple_reader
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**

   **macOS:**
   ```bash
   brew install tesseract
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```

   **Windows:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH environment variable

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   - Local: http://localhost:5000
   - LAN: http://[your-ip]:5000

## 🎯 Usage Guide

### Camera Controls

1. **Start Camera**: Click "Start Camera" to begin video feed
2. **Capture Methods**:
   - 🎯 **Capture Button**: Click the green "Capture" button
   - 🎥 **Click Video**: Click directly on the video feed
   - ⌨️ **Spacebar**: Press spacebar while camera is active

### File Management

- **Images**: Automatically saved with timestamp and page number
- **Text**: Use OCR button to extract text from images
- **Audio**: Use TTS button to convert text to speech
- **Delete**: Remove files and all associated data

### File Naming Convention

Images are automatically named using the format:
```
YYYYMMDD_HHMMSS_pXXX.jpg
```
Example: `20241201_143022_p001.jpg`

## 🏗️ Project Structure

```
simple_reader/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   └── index.html    # Main web interface
├── images/           # Captured images (auto-created)
├── text/            # Extracted text files (auto-created)
└── audio/           # Generated audio files (auto-created)
```

## 🔧 API Endpoints

### Camera Control
- `POST /api/camera/start` - Start camera
- `POST /api/camera/stop` - Stop camera
- `GET /api/camera/status` - Get camera status

### Capture & Processing
- `POST /api/capture` - Capture image
- `POST /api/ocr/<filename>` - Perform OCR on image
- `POST /api/tts/<filename>` - Convert text to speech

### File Management
- `GET /api/files` - List all files
- `GET /api/files/<filename>` - Download specific file
- `DELETE /api/files/<filename>` - Delete file and associated data

### Video Stream
- `GET /api/stream` - Live camera feed stream

## 🎨 Features in Detail

### Camera Capture
- **Debounce Protection**: Prevents rapid successive captures (1-second delay)
- **Unified Interface**: Live camera feed and captured images in one view
- **Multiple Input Methods**: Button, click, and keyboard shortcuts

### OCR Processing
- **Tesseract Integration**: Industry-standard OCR engine
- **Automatic Text Saving**: Extracted text saved as separate files
- **Error Handling**: Graceful fallback for OCR failures

### Text-to-Speech
- **Google TTS**: High-quality speech synthesis
- **Automatic OCR**: Performs OCR if text doesn't exist
- **MP3 Output**: Standard audio format for compatibility

### File Organization
- **Automatic Categorization**: Images, text, and audio organized by type
- **Status Tracking**: Visual indicators for processing status
- **Bulk Operations**: Delete associated files together

## 🌐 Network Access

The application runs on `0.0.0.0:5000`, making it accessible:

- **Locally**: http://localhost:5000
- **On LAN**: http://[your-computer-ip]:5000
- **From other devices**: Access from phones, tablets, or other computers on your network

## 🔒 Security Notes

- **Local Network Only**: Designed for personal/local network use
- **No Authentication**: Anyone on your network can access the app
- **File Access**: All captured files are stored locally on your machine

## 🐛 Troubleshooting

### Camera Issues
- **"Failed to start camera"**: Check if camera is in use by another application
- **No video feed**: Ensure camera permissions are granted in your browser
- **Camera not found**: Verify camera is properly connected and recognized

### OCR Issues
- **"OCR Error"**: Ensure Tesseract is properly installed and in PATH
- **Poor text quality**: Improve lighting and image clarity for better results

### Dependencies Issues
- **Import errors**: Ensure virtual environment is activated
- **Package conflicts**: Try updating pip: `pip install --upgrade pip`

## 🚀 Future Enhancements

- **Cloud Storage**: Save files to cloud services
- **Advanced OCR**: Support for multiple languages and handwriting
- **Audio Playback**: Built-in audio player for generated files
- **Batch Processing**: Process multiple images at once
- **Export Options**: PDF, Word, or other document formats
- **User Accounts**: Multi-user support with file sharing

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to:

- Report bugs or issues
- Suggest new features
- Improve documentation
- Optimize performance

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Flask**: Web framework
- **OpenCV**: Computer vision and camera handling
- **Tesseract**: OCR engine
- **gTTS**: Text-to-speech conversion
- **Pillow**: Image processing

---

**Happy Reading! 📖✨**
