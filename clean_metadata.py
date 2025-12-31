#!/usr/bin/env python3
"""
Script to clean non-words from metadata.json extractedText field.
Uses a dictionary-based approach to filter out OCR errors.
"""

import json
import re

# Known valid English words that should be kept (including positive vocabulary words)
VALID_WORDS = {
    # Common positive vocabulary words
    'abundance', 'abundant', 'achieve', 'achieved', 'affirmations', 'alive', 'all',
    'and', 'appreciate', 'appreciation', 'areas', 'aspire', 'am', 'are',
    'beaming', 'belief', 'best', 'blissful', 'bloom', 'blossom', 'blow', 'bright',
    'can', 'change', 'content', 'create',
    'deep', 'dynamic',
    'eager', 'empowered', 'energetic', 'evolve',
    'feel', 'flourish', 'for', 'fresh',
    'genuine', 'gifted', 'glow', 'goal', 'grace', 'grateful', 'great', 'grow', 'growth',
    'happiness', 'happy', 'have',
    'in', 'inspire', 'is',
    'jubilant',
    'learn', 'life', 'lively',
    'magnificent', 'myself',
    'noble',
    'of',
    'positive', 'positivity', 'prosper', 'prosperous', 'prowess',
    'self', 'serene', 'spark', 'sparkle', 'spirited', 'stellar', 'strength', 'strong', 'success',
    'the', 'thrive', 'to', 'today', 'true',
    'upbeat', 'uplifting',
    'valor', 'vital', 'vitality',
    'with',
    'yes',
    'zeal', 'zenith', 'zest',
    # Additional common words
    'a', 'i', 'be', 'focus', 'soar', 'goals', 'adaptable'
}

# Words to remove (identified as non-words/OCR errors)
NON_WORDS = {
    'nnspreb', 'aivtmioe', 'erd', 'reat', 'ghflodtto', 'epbeat', 'erous',
    'succes', 'dewarry', 'honered', 'rlnef', 'mowjand', 'evelq', 'frcenced',
    'mcrance', 'nbotnis', 'ajioance', 'perow', 'wiroho6y', 'adature', 'matance',
    'prosences', 'evolled', 'advgance', 'ercnonace', 'mrise', 'rinsh', 'mocs',
    'sfcrrb', 'beoss', 'bukcenen', 'inticudeed', 'burgud', 'fsrsayc', 'tty',
    'extived', 'frl', 'suret', 'prosrcn', 'amomon', 'menice', 'oitei', 'medleys',
    'prosperd', 'slxgend', 'megass', 'ebrifoncteais', 'rass', 'domerce', 'tfiuisb',
    'achievedi', 'mmjihlsisa', 'vesi', 'yesi', 'sstvong', 'vitauty', 'zea',
    'utality', 'gified', 'lnspire', 'browess', 'appreciaton', 'freshht', 'arightt',
    'aaptable', 'energtic', 'vitabillity', 'blisiful', 'apprecation', 'lam', 'tor',
    'sparre', 'cdjio', 'ccidd', 'cozic', 'dne', 'ttoto', 'joar', 'rue', 'inobl',
    'zenih', 'mionda', 'ocus', 'pmstc', 'positivevocab', 'exp', 'pic', 'ne',
    # Single characters and numbers
    't', 'w', 'n', 'jl'
}

def is_valid_word(word):
    """Check if a word is valid (real English word)."""
    # Clean the word
    clean_word = word.lower().strip()
    
    # Skip empty strings
    if not clean_word:
        return False
    
    # Skip single characters (except 'a', 'i')
    if len(clean_word) == 1 and clean_word not in {'a', 'i'}:
        return False
    
    # Skip if it's in the non-words list
    if clean_word in NON_WORDS:
        return False
    
    # Skip words with numbers
    if any(c.isdigit() for c in clean_word):
        return False
    
    # Skip words that are too short to be meaningful (less than 2 chars)
    if len(clean_word) < 2:
        return False
    
    # Check if in valid words list
    if clean_word in VALID_WORDS:
        return True
    
    # For words not in our lists, use a heuristic:
    # Keep words that look like proper English (reasonable consonant-vowel patterns)
    # Skip words with more than 3 consecutive consonants (likely OCR errors)
    consonants = 'bcdfghjklmnpqrstvwxyz'
    consecutive_consonants = 0
    max_consecutive = 0
    for char in clean_word.lower():
        if char in consonants:
            consecutive_consonants += 1
            max_consecutive = max(max_consecutive, consecutive_consonants)
        else:
            consecutive_consonants = 0
    
    if max_consecutive > 4:
        return False
    
    # If the word looks reasonable, keep it
    return True

def clean_extracted_text(text):
    """Clean the extractedText field by removing non-words."""
    if not text:
        return ""
    
    # Split into words (keeping hashtags separate)
    words = re.findall(r'#?\w+', text)
    
    # Filter valid words
    valid_words = []
    for word in words:
        # Handle hashtags
        if word.startswith('#'):
            word_without_hash = word[1:]
            if is_valid_word(word_without_hash):
                valid_words.append(word)
        elif is_valid_word(word):
            valid_words.append(word)
    
    return ' '.join(valid_words)

def clean_words_array(words):
    """Clean the words array by removing non-words."""
    if not words:
        return []
    
    return [word for word in words if is_valid_word(word)]

def main():
    # Load the metadata
    with open('metadata.json', 'r') as f:
        data = json.load(f)
    
    # Track changes
    changes = []
    
    # Process each file entry
    for file_entry in data.get('files', []):
        original_text = file_entry.get('extractedText', '')
        original_words = file_entry.get('words', [])
        
        # Clean the extracted text and words
        cleaned_text = clean_extracted_text(original_text)
        cleaned_words = clean_words_array(original_words)
        
        # Check if there were changes
        if original_text != cleaned_text or original_words != cleaned_words:
            changes.append({
                'filename': file_entry.get('filename'),
                'original_text': original_text,
                'cleaned_text': cleaned_text,
                'original_words': original_words,
                'cleaned_words': cleaned_words
            })
        
        # Update the entry
        file_entry['extractedText'] = cleaned_text
        file_entry['words'] = cleaned_words
    
    # Save the cleaned metadata
    with open('metadata.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    # Print summary
    print(f"Processed {len(data.get('files', []))} files")
    print(f"Made changes to {len(changes)} files")
    print("\nChanges made:")
    for change in changes:
        print(f"\n{change['filename']}:")
        print(f"  Original: {change['original_text'][:80]}..." if len(change['original_text']) > 80 else f"  Original: {change['original_text']}")
        print(f"  Cleaned:  {change['cleaned_text'][:80]}..." if len(change['cleaned_text']) > 80 else f"  Cleaned:  {change['cleaned_text']}")

if __name__ == '__main__':
    main()
