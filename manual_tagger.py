#!/usr/bin/env python3
"""
Manual Word Tagger for Positive Vocabulary Gallery

This interactive tool displays each image and lets you type the words/text
you see in the image. The words are saved directly to metadata.json.

Usage:
    python manual_tagger.py              # Tag images not yet reviewed
    python manual_tagger.py --all        # Tag all images (re-do everything)
    python manual_tagger.py --resume     # Resume from where you left off
    
Controls:
    - Type words separated by commas (e.g., "joy, happiness, love")
    - Type 'null' or 'n' to mark as "no text" (won't be asked again)
    - Type 'skip' or 's' to skip without marking (will be asked again)
    - Type 'quit' or 'q' to save and exit
    - Type 'back' or 'b' to go back to previous image
"""

import json
import os
import sys
import subprocess
import platform
from pathlib import Path

# Configuration
METADATA_FILE = "metadata.json"
MEDIA_FOLDER = "positivevocab"
PROGRESS_FILE = ".tagger_progress.json"


def load_metadata():
    """Load the metadata.json file."""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_metadata(metadata):
    """Save the metadata.json file."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def save_progress(index):
    """Save the current progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"last_index": index}, f)


def load_progress():
    """Load the saved progress."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f).get("last_index", 0)
    return 0


def clear_progress():
    """Clear the progress file."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


def open_image(filepath):
    """Open an image using the default system viewer."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", filepath], check=True)
        elif system == "Windows":
            os.startfile(filepath)
        else:  # Linux
            subprocess.run(["xdg-open", filepath], check=True)
        return True
    except Exception as e:
        print(f"  Warning: Could not open image: {e}")
        print(f"  Please manually open: {filepath}")
        return False


def close_preview_app():
    """Close the Preview app on macOS to avoid cluttering."""
    if platform.system() == "Darwin":
        try:
            subprocess.run(["osascript", "-e", 'tell application "Preview" to close every window'], 
                         capture_output=True, timeout=2)
        except:
            pass


def parse_words(input_text):
    """Parse comma-separated words into a clean list."""
    if not input_text.strip():
        return []
    
    # Split by comma, strip whitespace, filter empty
    words = [w.strip() for w in input_text.split(',')]
    words = [w for w in words if w]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_words = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    
    return unique_words


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("📝 Manual Word Tagger for Positive Vocabulary Gallery")
    print("=" * 60)
    print("\nInstructions:")
    print("  • Type words separated by commas (e.g., 'joy, happiness')")
    print("  • Type 'null' or 'n' to mark as 'no text' (won't ask again)")
    print("  • Type 'skip' or 's' to skip (will ask again next time)")
    print("  • Type 'quit' or 'q' to save and exit")
    print("  • Type 'back' or 'b' to go back to previous image")
    print("-" * 60)


def main():
    # Parse arguments
    tag_all = '--all' in sys.argv
    resume = '--resume' in sys.argv
    
    # Load metadata
    if not os.path.exists(METADATA_FILE):
        print(f"Error: {METADATA_FILE} not found!")
        print("Please run preprocess.py first to generate metadata.")
        return 1
    
    metadata = load_metadata()
    files = metadata.get("files", [])
    
    if not files:
        print("No files found in metadata!")
        return 1
    
    # Filter files to tag
    if tag_all:
        files_to_tag = [(i, f) for i, f in enumerate(files)]
        print(f"\nTagging ALL {len(files_to_tag)} images...")
    else:
        # Only show images that haven't been reviewed yet
        files_to_tag = [(i, f) for i, f in enumerate(files) 
                        if not f.get("reviewed", False)]
        print(f"\nFound {len(files_to_tag)} images not yet reviewed (out of {len(files)} total)")
    
    if not files_to_tag:
        print("All images already have words! Use --all to re-tag.")
        return 0
    
    # Resume from last position if requested
    start_idx = 0
    if resume:
        saved_progress = load_progress()
        # Find position in files_to_tag list
        for i, (orig_idx, _) in enumerate(files_to_tag):
            if orig_idx >= saved_progress:
                start_idx = i
                break
        print(f"Resuming from image #{start_idx + 1}")
    
    print_header()
    
    # Process each image
    current = start_idx
    modified = False
    
    while current < len(files_to_tag):
        orig_idx, file_info = files_to_tag[current]
        filename = file_info["filename"]
        filepath = os.path.join(MEDIA_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"\n⚠️  File not found: {filepath}")
            current += 1
            continue
        
        # Display current progress
        print(f"\n[{current + 1}/{len(files_to_tag)}] 📷 {filename}")
        
        # Show existing words if any
        existing_words = file_info.get("words", [])
        if existing_words:
            print(f"  Current words: {', '.join(existing_words)}")
        
        # Open the image
        open_image(filepath)
        
        # Get user input
        try:
            user_input = input("  Enter words (comma separated): ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nInterrupted! Saving progress...")
            save_progress(orig_idx)
            if modified:
                save_metadata(metadata)
                print("✅ Metadata saved!")
            return 0
        
        # Handle special commands
        if user_input.lower() in ('quit', 'q', 'exit'):
            print("\nSaving and exiting...")
            save_progress(orig_idx)
            if modified:
                save_metadata(metadata)
                print("✅ Metadata saved!")
            close_preview_app()
            return 0
        
        if user_input.lower() in ('back', 'b'):
            if current > 0:
                current -= 1
                close_preview_app()
            else:
                print("  Already at the first image!")
            continue
        
        # Handle null - mark as reviewed with no words
        if user_input.lower() in ('null', 'n'):
            metadata["files"][orig_idx]["words"] = []
            metadata["files"][orig_idx]["extractedText"] = ""
            metadata["files"][orig_idx]["reviewed"] = True
            modified = True
            print("  ✅ Marked as 'no text' (won't ask again)")
            close_preview_app()
            current += 1
            continue
        
        # Handle skip - don't mark, will ask again
        if user_input.lower() in ('skip', 's') or user_input == '':
            print("  ⏭️  Skipped (will ask again next time)")
            close_preview_app()
            current += 1
            continue
        
        # Parse and save words
        words = parse_words(user_input)
        if words:
            # Update metadata
            metadata["files"][orig_idx]["words"] = words
            metadata["files"][orig_idx]["extractedText"] = ' '.join(words)
            metadata["files"][orig_idx]["reviewed"] = True
            modified = True
            print(f"  ✅ Saved: {', '.join(words)}")
        else:
            print("  ⏭️  Skipped (no valid words)")
        
        # Close preview to avoid clutter
        close_preview_app()
        
        # Move to next image
        current += 1
        
        # Auto-save every 10 images
        if modified and current % 10 == 0:
            save_metadata(metadata)
            save_progress(orig_idx)
            print("  💾 Auto-saved progress...")
    
    # Final save
    if modified:
        save_metadata(metadata)
        print("\n✅ All changes saved to metadata.json!")
    
    clear_progress()
    close_preview_app()
    
    # Print summary
    total_with_words = sum(1 for f in metadata["files"] if f.get("words"))
    print(f"\n📊 Summary: {total_with_words}/{len(files)} images now have words")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
