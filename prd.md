Goal

A lightweight Flask-based web app (runs locally and on LAN) that:

Captures book pages via camera.

Capture:

Three input methods (spacebar, click video, capture button).

Unified display for both live camera and captured images.

Shutter sound + debounce delay.

Saves image to /images.

Data Model

File structure:

/story_reader
  /images
  /text
  /audio
  app.py


Naming: YYYYMMDD_HHMMSS_pXXX (e.g., 20250824_102455_p001.jpg).

REST API endpoints for save, OCR, TTS, file list, retrieval, and deletion.
