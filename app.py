from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import json
import sys
from datetime import datetime

from gtts import gTTS
import threading
import time
import base64
from PIL import Image
import io
import re
from google.cloud import vision
from google.cloud import texttospeech
from google.auth.exceptions import DefaultCredentialsError
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'images'
TEXT_FOLDER = 'text'
AUDIO_FOLDER = 'audio'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Google Cloud Vision configuration
GOOGLE_CLOUD_VISION_ENABLED = True  # Set to False to disable Google Cloud Vision
GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'story-reader-470101')
GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', os.path.join(os.path.dirname(os.getcwd()), 'googleapi.json'))

# Google Cloud Text-to-Speech configuration
GOOGLE_CLOUD_TTS_ENABLED = True  # Set to False to disable Google Cloud TTS

# Set Google credentials environment variable if credentials file exists
if os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CLOUD_CREDENTIALS_PATH

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, TEXT_FOLDER, AUDIO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Global variables for camera
camera = None
camera_active = False
capture_thread = None
last_capture_time = 0
DEBOUNCE_DELAY = 1.0  # 1 second debounce
camera_lock = threading.Lock()  # Prevent concurrent camera access

# Capture statistics
capture_stats = {
    'total_captures': 0,
    'successful_captures': 0,
    'failed_captures': 0,
    'total_capture_time': 0.0,
    'average_capture_time': 0.0,
    'last_capture_timestamp': None,
    'capture_errors': []
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename():
    """Generate filename in format: YYYYMMDD_HHMMSS_pXXX"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Find the next page number
    existing_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.jpg')]
    page_numbers = []
    
    for file in existing_files:
        try:
            parts = file.split('_')
            if len(parts) >= 3:
                page_num = int(parts[2].replace('p', '').replace('.jpg', ''))
                page_numbers.append(page_num)
        except:
            continue
    
    next_page = max(page_numbers) + 1 if page_numbers else 1
    return f"{timestamp}_p{next_page:03d}.jpg"

def capture_frame():
    """Capture a single frame from the camera"""
    global camera
    if camera is not None and camera.isOpened():
        ret, frame = camera.read()
        if ret:
            return frame
    return None

def start_camera():
    """Start the camera with enhanced error handling and device detection"""
    global camera, camera_active, capture_stats
    
    # Use lock to prevent concurrent camera access
    with camera_lock:
        # Check if camera is already active
        if camera_active and camera is not None:
            print("📷 Camera already active, skipping startup")
            return True
        
        print("🚀 Starting enhanced camera initialization...")
        
        # Try to find available camera devices
        available_devices = find_available_cameras()
        if not available_devices:
            print("❌ No camera devices found")
            return False
        
        # Try to open camera with the first available device
        for device_id in available_devices:
            try:
                print(f"🔍 Attempting to open camera device {device_id}")
                
                # Try multiple backend approaches
                backends = [
                    (cv2.CAP_AVFOUNDATION, "AVFoundation"),
                    (cv2.CAP_ANY, "Auto-detect"),
                    (cv2.CAP_DEFAULT, "Default")
                ]
                
                for backend_id, backend_name in backends:
                    try:
                        print(f"  🔧 Trying {backend_name} backend...")
                        camera = cv2.VideoCapture(device_id, backend_id)
                        
                        if camera.isOpened():
                            print(f"  ✅ {backend_name} backend opened device {device_id}")
                            
                            # Set camera properties for better compatibility
                            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            camera.set(cv2.CAP_PROP_FPS, 30)
                            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            
                            # Warm up the camera
                            import time
                            time.sleep(1.0)  # Increased warm-up time
                            
                            # Test if we can actually read frames with retries
                            frame_success = False
                            for attempt in range(5):  # Increased retry attempts
                                ret, test_frame = camera.read()
                                if ret and test_frame is not None:
                                    print(f"✅ Camera device {device_id} opened successfully with {backend_name} (Resolution: {test_frame.shape[1]}x{test_frame.shape[0]})")
                                    camera_active = True
                                    
                                    # Reset capture statistics when starting fresh
                                    capture_stats = {
                                        'total_captures': 0,
                                        'successful_captures': 0,
                                        'failed_captures': 0,
                                        'total_capture_time': 0.0,
                                        'average_capture_time': 0.0,
                                        'last_capture_timestamp': None,
                                        'capture_errors': []
                                    }
                                    frame_success = True
                                    break
                                else:
                                    print(f"⚠️ Frame read attempt {attempt + 1} failed for device {device_id} with {backend_name}")
                                    time.sleep(0.5)  # Increased delay between attempts
                            
                            if frame_success:
                                return True
                            else:
                                print(f"❌ Device {device_id} failed frame validation with {backend_name}")
                                camera.release()
                                camera = None
                        else:
                            print(f"  ❌ {backend_name} backend failed to open device {device_id}")
                            
                    except Exception as e:
                        print(f"  ❌ {backend_name} backend error: {e}")
                        if camera:
                            camera.release()
                            camera = None
                        continue
                
                print(f"❌ All backends failed for device {device_id}")
                    
            except Exception as e:
                print(f"❌ Error testing device {device_id}: {e}")
                if camera:
                    camera.release()
                    camera = None
                continue
        
        print("❌ No working camera devices found")
        
        # Try fallback methods
        print("🔄 Attempting fallback camera startup methods...")
        if start_camera_fallback():
            return True
        
        return False

def start_camera_fallback():
    """Fallback camera startup method for problematic systems"""
    global camera, camera_active, capture_stats
    
    print("🔄 Attempting fallback camera startup...")
    
    # Method 1: Try direct device 0 with longer timeout
    try:
        print("🔍 Method 1: Direct device 0 with timeout")
        camera = cv2.VideoCapture(0)
        
        # Wait a bit for camera to initialize
        import time
        time.sleep(2)
        
        if camera.isOpened():
            # Try multiple frame reads with retry
            for attempt in range(5):
                ret, test_frame = camera.read()
                if ret and test_frame is not None:
                    print("✅ Fallback method 1 successful")
                    camera_active = True
                    
                    # Reset capture statistics
                    capture_stats = {
                        'total_captures': 0,
                        'successful_captures': 0,
                        'failed_captures': 0,
                        'total_capture_time': 0.0,
                        'average_capture_time': 0.0,
                        'last_capture_timestamp': None,
                        'capture_errors': []
                    }
                    return True
                else:
                    print(f"⚠️ Frame read attempt {attempt + 1} failed, retrying...")
                    time.sleep(0.5)
            
            # If we get here, camera opened but can't read frames
            print("❌ Camera opened but frame reading failed after retries")
            camera.release()
            camera = None
            
    except Exception as e:
        print(f"❌ Fallback method 1 failed: {e}")
        if camera:
            camera.release()
            camera = None
    
    # Method 2: Try with specific camera properties
    try:
        print("🔍 Method 2: Device 0 with specific properties")
        camera = cv2.VideoCapture(0)
        
        if camera.isOpened():
            # Set specific camera properties that often help
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            time.sleep(1)
            
            ret, test_frame = camera.read()
            if ret and test_frame is not None:
                print("✅ Fallback method 2 successful")
                camera_active = True
                
                # Reset capture statistics
                capture_stats = {
                    'total_captures': 0,
                    'successful_captures': 0,
                    'failed_captures': 0,
                    'total_capture_time': 0.0,
                    'average_capture_time': 0.0,
                    'last_capture_timestamp': None,
                    'capture_errors': []
                }
                return True
            else:
                print("❌ Fallback method 2 failed - no frames")
                camera.release()
                camera = None
                
    except Exception as e:
        print(f"❌ Fallback method 2 failed: {e}")
        if camera:
            camera.release()
            camera = None
    
    print("❌ All fallback methods failed")
    return False

def find_available_cameras():
    """Find available camera devices for mobile web access"""
    available_devices = []
    
    print("🔍 Starting camera device scan for mobile web access...")
    
    # Simple camera detection for web-based mobile access
    for device_id in [0, 1]:
        try:
            print(f"🔍 Testing device {device_id}...")
            test_camera = cv2.VideoCapture(device_id)
            
            if test_camera.isOpened():
                # Set reasonable camera properties
                test_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                test_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                test_camera.set(cv2.CAP_PROP_FPS, 30)
                test_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Warm up the camera
                import time
                time.sleep(0.5)
                
                # Try to read a frame to ensure it's working
                ret, frame = test_camera.read()
                if ret and frame is not None:
                    available_devices.append(device_id)
                    print(f"✅ Found working camera at device {device_id} (Resolution: {frame.shape[1]}x{frame.shape[0]})")
                
                test_camera.release()
            else:
                print(f"❌ Device {device_id} could not be opened")
                
        except Exception as e:
            print(f"❌ Error testing device {device_id}: {e}")
            continue
    
    print(f"📊 Camera scan complete: {len(available_devices)} working devices found")
    
    if not available_devices:
        print("💡 Mobile web access tips:")
        print("   1. Use your mobile phone's camera through the web interface")
        print("   2. Ensure you're accessing the app via HTTPS for camera permissions")
        print("   3. Grant camera permissions when prompted by your browser")
    
    return available_devices

def get_camera_info():
    """Get detailed camera information"""
    if not camera or not camera.isOpened():
        return None
    
    try:
        # Get camera properties
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = camera.get(cv2.CAP_PROP_FPS)
        brightness = camera.get(cv2.CAP_PROP_BRIGHTNESS)
        contrast = camera.get(cv2.CAP_PROP_CONTRAST)
        
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'brightness': brightness,
            'contrast': contrast,
            'is_opened': camera.isOpened(),
            'device_id': getattr(camera, 'device_id', 'unknown')
        }
    except Exception as e:
        print(f"Error getting camera info: {e}")
        return None

def stop_camera():
    """Stop the camera"""
    global camera, camera_active
    
    with camera_lock:
        if camera is not None:
            print("🛑 Stopping camera...")
            camera.release()
            camera = None
        camera_active = False
        print("✅ Camera stopped")

def capture_image():
    """Capture and save an image with enhanced features"""
    global last_capture_time, capture_stats
    
    capture_start_time = time.time()
    current_time = time.time()
    
    # Update statistics
    capture_stats['total_captures'] += 1
    
    if current_time - last_capture_time < DEBOUNCE_DELAY:
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': 'Debounce delay active',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Debounce delay active"
    
    # Check if camera is active
    if not camera_active or camera is None:
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': 'Camera not active',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Camera not active"
    
    # Capture frame with retry mechanism
    frame = None
    max_retries = 3
    for attempt in range(max_retries):
        frame = capture_frame()
        if frame is not None:
            break
        time.sleep(0.1)  # Small delay between attempts
    
    if frame is None:
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': 'Failed to capture frame after multiple attempts',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Failed to capture frame after multiple attempts"
    
    # Image quality checks
    if frame.size == 0:
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': 'Captured frame is empty',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Captured frame is empty"
    
    # Check image dimensions (minimum 50x50 pixels) - relaxed for testing
    height, width = frame.shape[:2]
    if height < 50 or width < 50:  # Relaxed from 100x100 to 50x50 for testing
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': f'Image too small: {width}x{height} (minimum 50x50)',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Captured image too small (minimum 50x50 pixels)"
    
    # Check image brightness (basic quality check) - very relaxed for debugging
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
    mean_brightness = np.mean(gray)
    
    # For debugging, allow very dark images but log the brightness
    print(f"🔍 Debug: Image brightness = {mean_brightness:.1f}")
    
    if mean_brightness < 1:  # Only reject completely black images
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': f'Image completely black (brightness: {mean_brightness:.1f})',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Image completely black - check camera lens"
    elif mean_brightness > 250:  # Too bright
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': f'Image too bright (brightness: {mean_brightness:.1f})',
            'attempt_number': capture_stats['total_captures']
        })
        return None, "Image too bright - reduce lighting"
    
    # Generate filename
    filename = generate_filename()
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save image with quality settings
    try:
        # Save with high quality JPEG
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        success = cv2.imwrite(filepath, frame, encode_params)
        
        if not success:
            capture_stats['failed_captures'] += 1
            capture_stats['capture_errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': 'Failed to save image',
                'attempt_number': capture_stats['total_captures']
            })
            return None, "Failed to save image"
        
        # Verify file was created and has content
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            capture_stats['failed_captures'] += 1
            capture_stats['capture_errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': 'Image file creation failed',
                'attempt_number': capture_stats['total_captures']
            })
            return None, "Image file creation failed"
        
        # Update timestamp and statistics
        last_capture_time = current_time
        capture_stats['successful_captures'] += 1
        capture_stats['last_capture_timestamp'] = datetime.now().isoformat()
        
        # Calculate capture time
        capture_time = time.time() - capture_start_time
        capture_stats['total_capture_time'] += capture_time
        capture_stats['average_capture_time'] = capture_stats['total_capture_time'] / capture_stats['successful_captures']
        
        # Log successful capture
        print(f"Image captured successfully: {filename} ({width}x{height}, {os.path.getsize(filepath)} bytes, {capture_time:.3f}s)")
        
        return filename, "Image captured successfully"
        
    except Exception as e:
        # Clean up failed file if it exists
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        
        capture_stats['failed_captures'] += 1
        capture_stats['capture_errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': f'Error saving image: {str(e)}',
            'attempt_number': capture_stats['total_captures']
        })
        return None, f"Error saving image: {str(e)}"

def perform_ocr(image_path):
    """Perform OCR on the captured image using Google Cloud Vision API with smart formatting"""
    try:
        # Try Google Cloud Vision if enabled
        if GOOGLE_CLOUD_VISION_ENABLED and GOOGLE_CLOUD_CREDENTIALS_PATH:
            try:
                return perform_google_cloud_ocr(image_path)
            except Exception as e:
                print(f"Google Cloud Vision failed: {e}")
                return f"OCR Error: Google Cloud Vision unavailable - {str(e)}"
        else:
            return "OCR Error: Google Cloud Vision not configured"
            
    except Exception as e:
        return f"OCR Error: {str(e)}"

def perform_google_cloud_ocr(image_path):
    """Perform OCR using Google Cloud Vision API"""
    try:
        # Initialize the client
        client = vision.ImageAnnotatorClient()
        
        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Create image object
        image = vision.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return "No text detected in image"
        
        # Extract full text (first element contains all text)
        full_text = texts[0].description
        
        # Apply smart formatting
        formatted_text = smart_format_text(full_text)
        
        # Check for errors
        if response.error.message:
            raise Exception(f"Google Cloud Vision API error: {response.error.message}")
        
        return formatted_text
        
    except DefaultCredentialsError:
        raise Exception("Google Cloud credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
    except Exception as e:
        raise Exception(f"Google Cloud Vision API error: {str(e)}")



def smart_format_text(text):
    """Apply smart formatting to extracted text"""
    if not text:
        return text
    
    # Remove excessive whitespace while preserving paragraph structure
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Clean up the line
        cleaned_line = line.strip()
        
        # Skip empty lines
        if not cleaned_line:
            # Add paragraph break for consecutive empty lines
            if formatted_lines and formatted_lines[-1] != '':
                formatted_lines.append('')
            continue
        
        # Fix common OCR artifacts
        cleaned_line = re.sub(r'[^\w\s\.,!?;:()\[\]{}"\'-]', '', cleaned_line)
        
        # Fix spacing issues
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)  # Multiple spaces to single
        cleaned_line = re.sub(r'(\w)-(\w)', r'\1\2', cleaned_line)  # Remove hyphens in words
        
        # Fix common OCR mistakes
        cleaned_line = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', cleaned_line)  # Fix decimal numbers
        cleaned_line = re.sub(r'(\w+)\s*\.\s*(\w+)', r'\1. \2', cleaned_line)  # Fix sentence endings
        
        # Add the cleaned line
        formatted_lines.append(cleaned_line)
    
    # Remove trailing empty lines
    while formatted_lines and formatted_lines[-1] == '':
        formatted_lines.pop()
    
    # Join lines with proper spacing
    formatted_text = '\n'.join(formatted_lines)
    
    # Final cleanup
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)  # Max 2 consecutive newlines
    
    return formatted_text.strip()

def save_ocr_metadata(image_path, text, ocr_method, processing_time):
    """Save OCR metadata alongside the extracted text"""
    try:
        # Get image info
        image_info = get_image_info(image_path)
        
        # Create metadata
        metadata = {
            'ocr_method': ocr_method,
            'processing_time': processing_time,
            'image_info': image_info,
            'text_length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.splitlines()),
            'extraction_timestamp': datetime.now().isoformat(),
            'confidence_score': 'high' if ocr_method == 'google_cloud_vision' else 'medium'
        }
        
        # Save metadata as JSON
        base_filename = os.path.splitext(os.path.basename(image_path))[0]
        metadata_path = os.path.join(TEXT_FOLDER, f"{base_filename}_metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata_path
        
    except Exception as e:
        print(f"Error saving OCR metadata: {e}")
        return None

def text_to_speech(text, filename):
    """Convert text to speech using Google Cloud TTS or fallback to gTTS"""
    try:
        # Try Google Cloud TTS first if enabled
        if GOOGLE_CLOUD_TTS_ENABLED and os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
            return text_to_speech_google_cloud(text, filename)
        else:
            # Fallback to gTTS
            return text_to_speech_gtts(text, filename)
    except Exception as e:
        print(f"TTS error: {e}")
        # Fallback to gTTS if Google Cloud TTS fails
        return text_to_speech_gtts(text, filename)

def text_to_speech_google_cloud(text, filename):
    """Convert text to speech using Google Cloud Text-to-Speech"""
    try:
        # Initialize the client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",  # High-quality neural voice
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        
        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal speed
            pitch=0.0,  # Normal pitch
            volume_gain_db=0.0,  # Normal volume
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Save the audio file
        audio_path = os.path.join(AUDIO_FOLDER, f"{filename}.mp3")
        with open(audio_path, "wb") as out:
            out.write(response.audio_content)
            print(f"✅ Google Cloud TTS: Audio content written to {audio_path}")
        
        return audio_path
        
    except Exception as e:
        print(f"❌ Google Cloud TTS error: {e}")
        raise e

def text_to_speech_gtts(text, filename):
    """Convert text to speech using gTTS (fallback)"""
    try:
        tts = gTTS(text=text, lang='en')
        audio_path = os.path.join(AUDIO_FOLDER, f"{filename}.mp3")
        tts.save(audio_path)
        print(f"✅ gTTS: Audio content written to {audio_path}")
        return audio_path
    except Exception as e:
        print(f"❌ gTTS error: {e}")
        return None

def simulate_shutter_sound():
    """Simulate camera shutter sound (console beep)"""
    try:
        # Print a visual indicator for shutter sound
        print("📸 *shutter sound*")
        # You could also add actual audio feedback here if desired
    except:
        pass

def get_image_info(image_path):
    """Get detailed information about a captured image"""
    try:
        if not os.path.exists(image_path):
            return None
        
        # Get file stats
        stat = os.stat(image_path)
        file_size = stat.st_size
        
        # Get image dimensions and properties
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        # Calculate image statistics
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        return {
            'dimensions': f"{width}x{height}",
            'channels': channels,
            'file_size': file_size,
            'file_size_kb': round(file_size / 1024, 2),
            'brightness': {
                'mean': round(mean_brightness, 2),
                'std': round(std_brightness, 2)
            },
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        return None

@app.route('/')
def index():
    """Main page with camera interface"""
    return render_template('index.html')

@app.route('/api/camera/start', methods=['POST'])
def start_camera_api():
    """Start the camera"""
    try:
        success = start_camera()
        if success:
            # Verify camera is actually working
            if camera and camera.isOpened():
                ret, test_frame = camera.read()
                if ret and test_frame is not None:
                    return jsonify({
                        'success': True,
                        'message': 'Camera started successfully',
                        'resolution': f"{test_frame.shape[1]}x{test_frame.shape[0]}"
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Camera opened but cannot read frames'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'message': 'Camera failed to open'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start camera'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Camera startup error: {str(e)}'
        }), 500

@app.route('/api/camera/troubleshoot', methods=['POST'])
def troubleshoot_camera():
    """Troubleshoot camera issues with comprehensive diagnostics"""
    try:
        print("🔧 Starting comprehensive camera troubleshooting...")
        
        # Check system camera status
        check_system_camera_status()
        
        # Check system camera availability
        system_cameras = find_available_cameras()
        
        # Check current camera status
        current_status = {
            'camera_active': camera_active,
            'camera_opened': camera.isOpened() if camera else False,
            'available_devices': system_cameras
        }
        
        # Check permissions
        permissions_status = check_camera_permissions()
        current_status['permissions'] = permissions_status
        
        # Try to start camera with fallback
        if not camera_active:
            print("🔧 Troubleshooting: Attempting camera startup...")
            success = start_camera()
            current_status['startup_attempted'] = True
            current_status['startup_successful'] = success
        else:
            current_status['startup_attempted'] = False
            current_status['startup_successful'] = True
        
        # Generate comprehensive troubleshooting recommendations
        recommendations = []
        
        if not system_cameras:
            recommendations.append("❌ No camera devices detected. Check hardware connections.")
            recommendations.append("❌ Ensure camera is properly connected and powered.")
            recommendations.append("❌ Check if camera is physically working in other apps.")
        
        if permissions_status == 'denied_or_unknown':
            recommendations.append("🔐 Camera permissions may be denied.")
            recommendations.append("🔐 Check camera permissions in your browser settings")
            recommendations.append("🔐 Ensure you're accessing via HTTPS for camera access")
        
        if not current_status['camera_opened'] and system_cameras:
            recommendations.append("⚠️ Camera devices found but cannot be opened.")
            recommendations.append("⚠️ Check if another application is using the camera.")
            recommendations.append("⚠️ Try closing other camera apps.")
        
        if not current_status['startup_successful']:
            recommendations.append("❌ Camera startup failed after multiple attempts.")
            recommendations.append("❌ Try restarting your computer to reset camera state.")
            recommendations.append("❌ Check camera permissions in your browser.")
            recommendations.append("❌ Ensure you're using HTTPS for camera access.")
        
        # Add mobile-specific recommendations
        recommendations.append("📱 Mobile access: Use your phone's camera through the web interface")
        recommendations.append("📱 Mobile access: Grant camera permissions when prompted by your browser")
        recommendations.append("📱 Mobile access: Ensure you're accessing via HTTPS for camera access")
        
        return jsonify({
            'success': True,
            'current_status': current_status,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera_api():
    """Stop the camera"""
    stop_camera()
    return jsonify({
        'success': True,
        'message': 'Camera stopped'
    })

@app.route('/api/camera/diagnostics')
def camera_diagnostics():
    """Get comprehensive camera diagnostics for troubleshooting"""
    try:
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': os.uname().sysname if hasattr(os, 'uname') else 'Unknown',
                'opencv_version': cv2.__version__,
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            },
            'camera_status': {
                'active': camera_active,
                'opened': camera.isOpened() if camera else False,
                'camera_object': str(camera) if camera else None
            },
            'device_scan': {
                'available_devices': find_available_cameras(),
                'device_details': []
            },
            'permissions_check': {
                'camera_access': check_camera_permissions(),
                'file_access': check_file_permissions()
            },
            'recommendations': []
        }
        
        # Add device details
        for device_id in diagnostics['device_scan']['available_devices']:
            try:
                test_cam = cv2.VideoCapture(device_id)
                if test_cam.isOpened():
                    width = int(test_cam.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(test_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = test_cam.get(cv2.CAP_PROP_FPS)
                    
                    diagnostics['device_scan']['device_details'].append({
                        'device_id': device_id,
                        'resolution': f"{width}x{height}",
                        'fps': fps,
                        'status': 'working'
                    })
                    
                    # Test frame capture
                    ret, frame = test_cam.read()
                    if ret and frame is not None:
                        diagnostics['device_scan']['device_details'][-1]['frame_capture'] = 'success'
                    else:
                        diagnostics['device_scan']['device_details'][-1]['frame_capture'] = 'failed'
                    
                    test_cam.release()
            except Exception as e:
                diagnostics['device_scan']['device_details'].append({
                    'device_id': device_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate recommendations
        if not diagnostics['device_scan']['available_devices']:
            diagnostics['recommendations'].append("No camera devices detected. Check hardware connections.")
        
        if not diagnostics['camera_status']['opened']:
            diagnostics['recommendations'].append("Camera not opened. Check permissions and device availability.")
        
        if diagnostics['permissions_check']['camera_access'] == 'unknown':
            diagnostics['recommendations'].append("Camera permissions unclear. Check System Preferences > Security & Privacy > Camera.")
        
        return jsonify(diagnostics)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/camera/test-frame')
def test_camera_frame():
    """Test endpoint to capture a single frame and return its properties"""
    try:
        if not camera or not camera.isOpened():
            return jsonify({
                'success': False,
                'error': 'Camera not available'
            }), 400
        
        # Capture a test frame
        ret, frame = camera.read()
        if not ret or frame is None:
            return jsonify({
                'success': False,
                'error': 'Failed to capture frame'
            }), 400
        
        # Analyze frame properties
        height, width = frame.shape[:2]
        channels = frame.shape[2] if len(frame.shape) == 3 else 1
        
        # Check brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        frame_info = {
            'success': True,
            'frame_properties': {
                'dimensions': f"{width}x{height}",
                'channels': channels,
                'total_pixels': width * height,
                'brightness': {
                    'mean': round(mean_brightness, 2),
                    'std': round(std_brightness, 2),
                    'status': 'normal' if 20 <= mean_brightness <= 240 else 'extreme'
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(frame_info)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def check_camera_permissions():
    """Check camera permissions for mobile web access"""
    try:
        print("🔐 Checking camera permissions for mobile web access...")
        
        # Try to open camera directly
        try:
            test_cam = cv2.VideoCapture(0)
            if test_cam.isOpened():
                test_cam.release()
                print("✅ Camera access appears to be granted")
                return 'granted'
            else:
                print("⚠️ Camera could not be opened - may be permission issue")
                return 'denied_or_unknown'
        except Exception as e:
            print(f"❌ Camera access test failed: {e}")
            return 'denied_or_unknown'
    except Exception:
        return 'unknown'

def check_system_camera_status():
    """Check system-level camera status for mobile web access"""
    try:
        print("🔍 Checking camera system status for mobile web access...")
        
        # Simple camera hardware check
        try:
            test_cam = cv2.VideoCapture(0)
            if test_cam.isOpened():
                print("✅ Camera hardware detected and accessible")
                test_cam.release()
            else:
                print("⚠️ Camera hardware not accessible")
        except Exception as e:
            print(f"⚠️ Could not check camera hardware: {e}")
            
    except Exception as e:
        print(f"❌ Error checking system camera status: {e}")

def check_file_permissions():
    """Check if we can write to the images directory"""
    try:
        test_file = os.path.join(UPLOAD_FOLDER, 'test_permission.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return 'writable'
    except Exception:
        return 'not_writable'

@app.route('/api/camera/status')
def camera_status():
    """Get detailed camera status and information"""
    try:
        # Get basic status
        status_data = {
            'active': camera_active,
            'opened': camera.isOpened() if camera else False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add camera information if available
        if camera and camera.isOpened():
            camera_info = get_camera_info()
            if camera_info:
                status_data['camera_info'] = camera_info
            
            # Test frame capture
            try:
                ret, test_frame = camera.read()
                status_data['frame_test'] = {
                    'success': ret and test_frame is not None,
                    'frame_shape': test_frame.shape if test_frame is not None else None,
                    'frame_size': test_frame.size if test_frame is not None else 0
                }
            except Exception as e:
                status_data['frame_test'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Add available devices information
        available_devices = find_available_cameras()
        status_data['available_devices'] = available_devices
        
        # Add system information
        status_data['system_info'] = {
            'platform': 'Mobile Web Access',
            'opencv_version': cv2.__version__,
            'camera_detection': len(available_devices) > 0
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({
            'active': False,
            'opened': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/capture', methods=['POST'])
def capture_api():
    """Capture an image via API with enhanced response"""
    try:
        filename, message = capture_image()
        
        if filename:
            # Simulate shutter sound
            simulate_shutter_sound()
            
            # Get detailed image information
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_info = get_image_info(image_path)
            
            response_data = {
                'success': True,
                'filename': filename,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'image_info': image_info
            }
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Capture error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/upload/mobile', methods=['POST'])
def upload_mobile_image():
    """Upload and process image from mobile camera"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only JPG, JPEG, PNG allowed.'
            }), 400
        
        # Generate filename for mobile capture
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mobile_{timestamp}_p001.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file
        file.save(filepath)
        
        # Verify file was saved
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return jsonify({
                'success': False,
                'message': 'Failed to save mobile image'
            }), 500
        
        # Get image information
        image_info = get_image_info(filepath)
        
        # Simulate shutter sound
        simulate_shutter_sound()
        
        response_data = {
            'success': True,
            'filename': filename,
            'message': 'Mobile image uploaded successfully',
            'timestamp': datetime.now().isoformat(),
            'file_size': os.path.getsize(filepath),
            'image_info': image_info
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Mobile upload error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/ocr/<filename>', methods=['POST'])
def ocr_api(filename):
    """Perform OCR on captured image with enhanced processing and metadata"""
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    # Start timing
    start_time = time.time()
    
    try:
        # Determine OCR method
        if GOOGLE_CLOUD_VISION_ENABLED and GOOGLE_CLOUD_CREDENTIALS_PATH:
            try:
                text = perform_google_cloud_ocr(image_path)
                ocr_method = 'google_cloud_vision'
            except Exception as e:
                print(f"Google Cloud Vision failed: {e}")
                text = f"OCR Error: Google Cloud Vision unavailable - {str(e)}"
                ocr_method = 'failed'
        else:
            text = "OCR Error: Google Cloud Vision not configured"
            ocr_method = 'not_configured'
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save text to file
        text_filename = filename.replace('.jpg', '.txt')
        text_path = os.path.join(TEXT_FOLDER, text_filename)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save metadata
        metadata_path = save_ocr_metadata(image_path, text, ocr_method, processing_time)
        
        # Prepare response
        response_data = {
            'success': True,
            'text': text,
            'text_file': text_filename,
            'ocr_method': ocr_method,
            'processing_time': round(processing_time, 3),
            'confidence_score': 'high' if ocr_method == 'google_cloud_vision' else 'medium',
            'metadata_file': os.path.basename(metadata_path) if metadata_path else None
        }
        
        # Add text statistics
        if text and text != "No text detected in image":
            response_data.update({
                'text_length': len(text),
                'word_count': len(text.split()),
                'line_count': len(text.splitlines()),
                'text_preview': text[:200] + '...' if len(text) > 200 else text
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_response = {
            'success': False,
            'error': str(e),
            'processing_time': round(processing_time, 3),
            'ocr_method': 'failed'
        }
        return jsonify(error_response), 500

@app.route('/api/tts/text', methods=['POST'])
def tts_text_api():
    """Convert text input to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Generate a unique filename for this text
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"text_tts_{timestamp}.mp3"
        
        # Convert to speech
        audio_path = text_to_speech(text, f"text_tts_{timestamp}")
        
        if audio_path:
            return jsonify({
                'success': True,
                'audio_file': os.path.basename(audio_path),
                'message': 'Text converted to speech successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to convert text to speech'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing text: {str(e)}'
        }), 500

@app.route('/api/tts/<filename>', methods=['POST'])
def tts_api(filename):
    """Convert text to speech"""
    # First perform OCR if text doesn't exist
    text_filename = filename.replace('.jpg', '.txt')
    text_path = os.path.join(TEXT_FOLDER, text_filename)
    
    if not os.path.exists(text_path):
        # Perform OCR first
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        text = perform_ocr(image_path)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # Convert to speech
    audio_path = text_to_speech(text, filename.replace('.jpg', ''))
    
    if audio_path:
        return jsonify({
            'success': True,
            'audio_file': os.path.basename(audio_path),
            'message': 'Text converted to speech successfully'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to convert text to speech'
        }), 500

@app.route('/api/files')
def list_files():
    """List all captured files"""
    files = []
    
    # List images
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.jpg'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            stat = os.stat(filepath)
            files.append({
                'filename': filename,
                'type': 'image',
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'has_text': os.path.exists(os.path.join(TEXT_FOLDER, filename.replace('.jpg', '.txt'))),
                'has_audio': os.path.exists(os.path.join(AUDIO_FOLDER, filename.replace('.jpg', '.mp3')))
            })
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({'files': files})

@app.route('/api/files/<filename>')
def get_file(filename):
    """Get a specific file"""
    # Check if it's an image
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    
    # Check if it's a text file
    text_path = os.path.join(TEXT_FOLDER, filename)
    if os.path.exists(text_path):
        return send_file(text_path, mimetype='text/plain')
    
    # Check if it's an audio file
    audio_path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/files/<filename>/info')
def get_file_info(filename):
    """Get detailed information about a specific file"""
    # Check if it's an image
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(image_path):
        image_info = get_image_info(image_path)
        if image_info:
            return jsonify({
                'success': True,
                'file_type': 'image',
                'filename': filename,
                'info': image_info
            })
        else:
            return jsonify({'error': 'Failed to get image information'}), 500
    
    # Check if it's a text file
    text_path = os.path.join(TEXT_FOLDER, filename)
    if os.path.exists(text_path):
        try:
            stat = os.stat(text_path)
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_info = {
                    'file_size': stat.st_size,
                    'file_size_kb': round(stat.st_size / 1024, 2),
                    'line_count': len(content.splitlines()),
                    'word_count': len(content.split()),
                    'character_count': len(content),
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                return jsonify({
                    'success': True,
                    'file_type': 'text',
                    'filename': filename,
                    'info': text_info
                })
        except Exception as e:
            return jsonify({'error': f'Failed to read text file: {str(e)}'}), 500
    
    # Check if it's an audio file
    audio_path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(audio_path):
        try:
            stat = os.stat(audio_path)
            audio_info = {
                'file_size': stat.st_size,
                'file_size_kb': round(stat.st_size / 1024, 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            return jsonify({
                'success': True,
                'file_type': 'audio',
                'filename': filename,
                'info': audio_info
            })
        except Exception as e:
            return jsonify({'error': f'Failed to read audio file: {str(e)}'}), 500
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/capture/stats')
def get_capture_stats():
    """Get capture statistics and performance metrics"""
    # Calculate success rate
    success_rate = 0
    if capture_stats['total_captures'] > 0:
        success_rate = (capture_stats['successful_captures'] / capture_stats['total_captures']) * 100
    
    # Get recent errors (last 10)
    recent_errors = capture_stats['capture_errors'][-10:] if capture_stats['capture_errors'] else []
    
    stats_data = {
        'success': True,
        'statistics': {
            'total_captures': capture_stats['total_captures'],
            'successful_captures': capture_stats['successful_captures'],
            'failed_captures': capture_stats['failed_captures'],
            'success_rate_percent': round(success_rate, 2),
            'total_capture_time': round(capture_stats['total_capture_time'], 3),
            'average_capture_time': round(capture_stats['average_capture_time'], 3),
            'last_capture_timestamp': capture_stats['last_capture_timestamp'],
            'recent_errors': recent_errors
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(stats_data)

@app.route('/api/capture/stats/reset', methods=['POST'])
def reset_capture_stats():
    """Reset capture statistics"""
    global capture_stats
    
    capture_stats = {
        'total_captures': 0,
        'successful_captures': 0,
        'failed_captures': 0,
        'total_capture_time': 0.0,
        'average_capture_time': 0.0,
        'last_capture_timestamp': None,
        'capture_errors': []
    }
    
    return jsonify({
        'success': True,
        'message': 'Capture statistics reset successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ocr/info')
def get_ocr_info():
    """Get OCR system information and configuration"""
    try:
        # Check Google Cloud Vision availability
        google_vision_available = False
        google_vision_error = None
        
        if GOOGLE_CLOUD_VISION_ENABLED:
            if GOOGLE_CLOUD_CREDENTIALS_PATH:
                if os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
                    try:
                        # Test Google Cloud Vision client initialization
                        client = vision.ImageAnnotatorClient()
                        google_vision_available = True
                    except Exception as e:
                        google_vision_error = str(e)
                else:
                    google_vision_error = "Credentials file not found"
            else:
                google_vision_error = "No credentials path configured"
        
        # Check Google Cloud TTS availability
        google_tts_available = False
        google_tts_error = None
        
        if GOOGLE_CLOUD_TTS_ENABLED:
            if GOOGLE_CLOUD_CREDENTIALS_PATH:
                if os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
                    try:
                        # Test Google Cloud TTS client initialization
                        client = texttospeech.TextToSpeechClient()
                        google_tts_available = True
                    except Exception as e:
                        google_tts_error = str(e)
                else:
                    google_tts_error = "Credentials file not found"
            else:
                google_tts_error = "No credentials path configured"

        ocr_info = {
            'success': True,
            'ocr_systems': {
                'google_cloud_vision': {
                    'enabled': GOOGLE_CLOUD_VISION_ENABLED,
                    'available': google_vision_available,
                    'credentials_path': GOOGLE_CLOUD_CREDENTIALS_PATH,
                    'error': google_vision_error,
                    'priority': 'primary' if google_vision_available else 'unavailable'
                }
            },
            'tts_systems': {
                'google_cloud_tts': {
                    'enabled': GOOGLE_CLOUD_TTS_ENABLED,
                    'available': google_tts_available,
                    'credentials_path': GOOGLE_CLOUD_CREDENTIALS_PATH,
                    'error': google_tts_error,
                    'priority': 'primary' if google_tts_available else 'fallback_to_gtts'
                },
                'gtts': {
                    'enabled': True,
                    'available': True,
                    'priority': 'fallback'
                }
            },
            'recommended_method': 'google_cloud_vision' if google_vision_available else 'none',
            'recommended_tts': 'google_cloud_tts' if google_tts_available else 'gtts',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(ocr_info)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file and its associated files"""
    deleted_files = []
    
    # Delete image
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(image_path):
        os.remove(image_path)
        deleted_files.append(filename)
    
    # Delete associated text file
    text_filename = filename.replace('.jpg', '.txt')
    text_path = os.path.join(TEXT_FOLDER, text_filename)
    if os.path.exists(text_path):
        os.remove(text_path)
        deleted_files.append(text_filename)
    
    # Delete associated audio file
    audio_filename = filename.replace('.jpg', '.mp3')
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
    if os.path.exists(audio_path):
        os.remove(audio_path)
        deleted_files.append(audio_filename)
    
    return jsonify({
        'success': True,
        'deleted_files': deleted_files,
        'message': f'Deleted {len(deleted_files)} files'
    })

@app.route('/api/stream')
def video_stream():
    """Stream camera feed with enhanced error handling"""
    def generate():
        global camera
        frame_count = 0
        error_count = 0
        max_errors = 10  # Increased error tolerance
        
        # Warm up the camera with a few initial reads
        for _ in range(5):  # Increased warm-up frames
            try:
                if camera and camera.isOpened():
                    camera.read()
                time.sleep(0.2)  # Increased delay
            except:
                pass
        
        while camera_active and camera and camera.isOpened():
            try:
                ret, frame = camera.read()
                if ret and frame is not None:
                    # Convert frame to JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        frame_count += 1
                        error_count = 0  # Reset error count on successful frame
                        
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        error_count += 1
                        print(f"⚠️ Frame encoding failed (error {error_count}/{max_errors})")
                else:
                    error_count += 1
                    print(f"⚠️ Frame capture failed (error {error_count}/{max_errors})")
                
                # Stop if too many consecutive errors
                if error_count >= max_errors:
                    print("❌ Too many consecutive errors, stopping video stream")
                    break
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                error_count += 1
                print(f"❌ Video stream error: {e} (error {error_count}/{max_errors})")
                
                if error_count >= max_errors:
                    print("❌ Too many errors, stopping video stream")
                    break
                
                time.sleep(0.1)
        
        print(f"📹 Video stream ended. Total frames: {frame_count}, Errors: {error_count}")
    
    return app.response_class(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Check if SSL certificates exist for HTTPS
    ssl_cert = 'cert.pem'
    ssl_key = 'key.pem'
    
    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        print("🔒 Starting with HTTPS support...")
        print("📱 Mobile camera access: https://YOUR_IP:5001")
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False, 
                ssl_context=(ssl_cert, ssl_key))
    else:
        print("🌐 Starting with HTTP (local development)...")
        print("📱 Mobile camera access: http://localhost:5001 or http://YOUR_IP:5001")
        print("⚠️  Note: Some browsers may require HTTPS for camera access")
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
