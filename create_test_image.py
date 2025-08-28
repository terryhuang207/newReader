#!/usr/bin/env python3
"""
Create a test image with text for OCR testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """Create a test image with sample text"""
    
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            # Fallback to default font
            font = ImageFont.load_default()
        except:
            # Use basic font
            font = ImageFont.load_default()
    
    # Sample text for OCR testing
    text_lines = [
        "Story Reader OCR Test",
        "",
        "This is a sample text document",
        "created for testing OCR functionality.",
        "",
        "The text includes:",
        "• Multiple lines",
        "• Different formatting",
        "• Numbers: 123, 456, 789",
        "• Punctuation marks!",
        "",
        "This demonstrates the enhanced",
        "OCR capabilities with smart",
        "text formatting and processing.",
        "",
        "End of test document."
    ]
    
    # Draw text on image
    y_position = 50
    for line in text_lines:
        if line.strip():  # Skip empty lines
            # Center the text
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (width - text_width) // 2
            
            # Draw text with black color
            draw.text((x_position, y_position), line, fill='black', font=font)
        
        y_position += 35
    
    # Save the image
    test_image_path = "test_ocr_document.jpg"
    image.save(test_image_path, "JPEG", quality=95)
    
    print(f"✅ Test image created: {test_image_path}")
    print(f"📏 Dimensions: {width}x{height}")
    print(f"📝 Contains {len([l for l in text_lines if l.strip()])} text lines")
    
    return test_image_path

if __name__ == "__main__":
    create_test_image()
