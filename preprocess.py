#!/usr/bin/env python3
"""
Positive Vocabulary Image Preprocessor

This script scans the positivevocab folder, extracts text from images using OCR,
and generates a metadata.json file for the web gallery.

Uses EasyOCR - a pure Python OCR library that works better with stylized text.

Requirements:
    pip install easyocr Pillow

Usage:
    python preprocess.py           # Process all files
    python preprocess.py --force   # Force re-process even if metadata exists
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow not installed. Install with: pip install Pillow")

try:
    import easyocr
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: EasyOCR not installed.")
    print("Install with: pip install easyocr")
    print("Note: First run will download OCR models (~100MB)")
    print("Proceeding without OCR - text extraction will be skipped.")

# Configuration
MEDIA_FOLDER = "positivevocab"
OUTPUT_FILE = "metadata.json"

# Supported file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}

# Global OCR reader (lazy initialization)
_ocr_reader = None


def get_ocr_reader():
    """Get or create the EasyOCR reader (lazy initialization)."""
    global _ocr_reader
    if _ocr_reader is None and HAS_OCR:
        print("  Initializing OCR engine (first run may take a moment)...")
        _ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _ocr_reader


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    return filepath.stat().st_size


def get_modification_time(filepath: Path) -> str:
    """Get file modification time as ISO format string."""
    timestamp = filepath.stat().st_mtime
    return datetime.fromtimestamp(timestamp).isoformat()


def get_image_dimensions(filepath: Path) -> tuple:
    """Get image dimensions (width, height)."""
    if not HAS_PIL:
        return (0, 0)
    try:
        with Image.open(filepath) as img:
            return img.size
    except Exception as e:
        print(f"    Warning: Could not get dimensions for {filepath.name}: {e}")
        return (0, 0)


def extract_text_from_image(filepath: Path) -> str:
    """Extract text from image using EasyOCR."""
    if not HAS_OCR:
        return ""
    
    try:
        reader = get_ocr_reader()
        if reader is None:
            return ""
        
        # EasyOCR reads the image and returns list of (bbox, text, confidence)
        results = reader.readtext(str(filepath), detail=1, paragraph=False)
        
        # Filter by confidence and extract text
        texts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Only include text with reasonable confidence
                texts.append(text)
        
        # Join all detected text
        full_text = ' '.join(texts)
        
        # Clean up the text
        full_text = full_text.strip()
        full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
        
        return full_text
    except Exception as e:
        print(f"    Warning: OCR failed for {filepath.name}: {e}")
        return ""


def extract_words(text: str) -> list:
    """Extract meaningful words from OCR text."""
    if not text:
        return []
    
    # Extract words (alphabetic only, min 3 chars)
    words = re.findall(r'\b[A-Za-z]{3,}\b', text)
    
    # Convert to lowercase and remove duplicates while preserving order
    seen = set()
    unique_words = []
    for word in words:
        word_lower = word.lower()
        if word_lower not in seen:
            seen.add(word_lower)
            # Keep original case for display
            unique_words.append(word)
    
    return unique_words


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def process_file(filepath: Path, use_ocr: bool = True) -> dict:
    """Process a single file and extract metadata."""
    ext = filepath.suffix.lower()
    is_image = ext in IMAGE_EXTENSIONS
    is_video = ext in VIDEO_EXTENSIONS
    
    if not (is_image or is_video):
        return None
    
    print(f"  Processing: {filepath.name}")
    
    metadata = {
        "filename": filepath.name,
        "type": "image" if is_image else "video",
        "format": ext.lstrip('.'),
        "fileSize": get_file_size(filepath),
        "fileSizeFormatted": format_file_size(get_file_size(filepath)),
        "timestamp": get_modification_time(filepath),
    }
    
    # For images, get dimensions and extract text
    if is_image:
        width, height = get_image_dimensions(filepath)
        metadata["dimensions"] = {
            "width": width,
            "height": height
        }
        
        # Extract text using OCR (skip for GIFs as they might be animated)
        if use_ocr and ext != '.gif':
            extracted_text = extract_text_from_image(filepath)
            metadata["extractedText"] = extracted_text
            metadata["words"] = extract_words(extracted_text)
            if metadata["words"]:
                print(f"    Found words: {', '.join(metadata['words'][:5])}")
        else:
            metadata["extractedText"] = ""
            metadata["words"] = []
    else:
        # Video - no OCR
        metadata["extractedText"] = ""
        metadata["words"] = []
        metadata["dimensions"] = {"width": 0, "height": 0}
    
    return metadata


def main():
    """Main function to process all files in the media folder."""
    # Check for --force flag
    force_reprocess = '--force' in sys.argv
    
    media_path = Path(MEDIA_FOLDER)
    output_path = Path(OUTPUT_FILE)
    
    if not media_path.exists():
        print(f"Error: Folder '{MEDIA_FOLDER}' not found!")
        return 1
    
    # Check if metadata already exists (unless --force)
    if output_path.exists() and not force_reprocess:
        print(f"Metadata file '{OUTPUT_FILE}' already exists.")
        print("Use --force to regenerate, or delete the file manually.")
        return 0
    
    # Get all files in the folder
    files = sorted(media_path.iterdir())
    
    print("=" * 60)
    print("Positive Vocabulary Image Preprocessor")
    print("=" * 60)
    print(f"Media folder: {media_path.absolute()}")
    print(f"Found {len(files)} files")
    print(f"OCR enabled: {HAS_OCR}")
    if HAS_OCR:
        print("Using EasyOCR (pure Python, better for stylized text)")
    print("-" * 60)
    
    # Process all files
    metadata_list = []
    image_count = 0
    video_count = 0
    words_found = 0
    
    for filepath in files:
        if filepath.is_file():
            result = process_file(filepath, use_ocr=HAS_OCR)
            if result:
                metadata_list.append(result)
                if result["type"] == "image":
                    image_count += 1
                    words_found += len(result.get("words", []))
                else:
                    video_count += 1
    
    # Create output structure
    output = {
        "generated": datetime.now().isoformat(),
        "totalFiles": len(metadata_list),
        "imageCount": image_count,
        "videoCount": video_count,
        "mediaFolder": MEDIA_FOLDER,
        "files": metadata_list
    }
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("-" * 60)
    print("Processing complete!")
    print(f"  Images processed: {image_count}")
    print(f"  Videos processed: {video_count}")
    print(f"  Total words extracted: {words_found}")
    print(f"  Output saved to: {output_path.absolute()}")
    print("=" * 60)
    
    # Print sample of extracted words
    if metadata_list:
        print("\nSample extracted words:")
        word_sample = []
        for item in metadata_list[:20]:
            if item.get("words"):
                word_sample.extend(item["words"][:3])
        if word_sample:
            print(f"  {', '.join(word_sample[:20])}")
        else:
            print("  (No words extracted)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
