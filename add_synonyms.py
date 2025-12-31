#!/usr/bin/env python3
"""
Script to add synonyms to metadata.json for positive vocabulary words.
"""

import json

# Synonym dictionary for all unique positive vocabulary words
SYNONYMS = {
    "ABUNDANCE": ["plenty", "wealth", "prosperity", "richness", "profusion", "excess"],
    "ABUNDANT": ["plentiful", "ample", "copious", "rich", "lavish", "bountiful"],
    "ACE": ["expert", "champion", "master", "star", "winner", "top"],
    "ACHIEVE": ["accomplish", "attain", "reach", "complete", "succeed", "fulfill"],
    "AFFIRMATIONS": ["declarations", "assertions", "statements", "confirmations", "mantras"],
    "ALIVE": ["living", "vibrant", "animated", "lively", "energetic", "vital"],
    "APPRECIATION": ["gratitude", "thankfulness", "recognition", "acknowledgment", "admiration"],
    "ASPIRE": ["aim", "strive", "hope", "dream", "desire", "pursue"],
    "BEAMING": ["radiant", "glowing", "shining", "bright", "smiling", "happy"],
    "BELIEF": ["faith", "trust", "confidence", "conviction", "assurance", "hope"],
    "BLISSFUL": ["happy", "joyful", "ecstatic", "delighted", "euphoric", "serene"],
    "BLOSSOM": ["bloom", "flourish", "flower", "develop", "grow", "thrive"],
    "BOLD": ["brave", "courageous", "daring", "fearless", "confident", "audacious"],
    "BOOST": ["increase", "enhance", "elevate", "uplift", "improve", "strengthen"],
    "BOUNTIFUL": ["abundant", "plentiful", "generous", "ample", "copious", "rich"],
    "BRAVE": ["courageous", "bold", "fearless", "valiant", "heroic", "daring"],
    "BRIGHT": ["brilliant", "radiant", "luminous", "shining", "glowing", "vivid"],
    "CHEERFUL": ["happy", "joyful", "merry", "upbeat", "jolly", "lighthearted"],
    "CLEAR": ["transparent", "lucid", "obvious", "distinct", "pure", "clean"],
    "CREATIVE": ["imaginative", "innovative", "inventive", "artistic", "original", "inspired"],
    "DREAM": ["vision", "aspiration", "goal", "ambition", "fantasy", "hope"],
    "DYNAMIC": ["energetic", "active", "lively", "vibrant", "powerful", "forceful"],
    "EAGER": ["enthusiastic", "keen", "excited", "willing", "anxious", "ready"],
    "EMPOWERED": ["enabled", "strengthened", "authorized", "confident", "capable", "liberated"],
    "ENERGETIC": ["lively", "active", "dynamic", "vigorous", "spirited", "vibrant"],
    "ENTHUSIASM": ["excitement", "eagerness", "passion", "zeal", "fervor", "keenness"],
    "ENTHUSIASTIC": ["eager", "excited", "passionate", "keen", "zealous", "fervent"],
    "EPIC": ["legendary", "grand", "heroic", "monumental", "impressive", "magnificent"],
    "FLAIR": ["style", "talent", "panache", "elegance", "skill", "aptitude"],
    "FLOURISH": ["thrive", "prosper", "bloom", "succeed", "grow", "blossom"],
    "FLOW": ["stream", "movement", "current", "glide", "rhythm", "ease"],
    "FOCUS": ["concentrate", "attention", "clarity", "determination", "direction", "aim"],
    "FORTUNATE": ["lucky", "blessed", "favored", "successful", "privileged", "prosperous"],
    "FREE": ["liberated", "independent", "unrestricted", "open", "unbound", "liberated"],
    "FRESH": ["new", "crisp", "clean", "renewed", "invigorating", "revitalized"],
    "GEM": ["treasure", "jewel", "prize", "wonder", "pearl", "beauty"],
    "GENUINE": ["authentic", "real", "sincere", "true", "honest", "original"],
    "GIFTED": ["talented", "skilled", "blessed", "exceptional", "brilliant", "capable"],
    "GLORY": ["honor", "fame", "triumph", "splendor", "magnificence", "greatness"],
    "GLOW": ["shine", "radiance", "warmth", "light", "luminescence", "brilliance"],
    "GOLDEN": ["precious", "valuable", "excellent", "perfect", "ideal", "brilliant"],
    "GRACE": ["elegance", "poise", "beauty", "charm", "refinement", "dignity"],
    "GRAND": ["magnificent", "impressive", "majestic", "splendid", "great", "glorious"],
    "GRATEFUL": ["thankful", "appreciative", "blessed", "indebted", "obliged", "content"],
    "GRIT": ["determination", "perseverance", "resilience", "courage", "tenacity", "resolve"],
    "GROWTH": ["development", "progress", "expansion", "improvement", "evolution", "advancement"],
    "HARMONY": ["balance", "peace", "unity", "accord", "serenity", "coherence"],
    "HEARTENING": ["encouraging", "uplifting", "inspiring", "comforting", "reassuring", "hopeful"],
    "HOPE": ["optimism", "faith", "expectation", "aspiration", "belief", "confidence"],
    "IGNITE": ["spark", "kindle", "inspire", "fire", "activate", "energize"],
    "INSPIRE": ["motivate", "encourage", "uplift", "stimulate", "move", "influence"],
    "INSPIRED": ["motivated", "encouraged", "moved", "uplifted", "stimulated", "creative"],
    "JOY": ["happiness", "delight", "bliss", "pleasure", "elation", "gladness"],
    "JOYFUL": ["happy", "delighted", "elated", "cheerful", "merry", "jubilant"],
    "JUBILANT": ["joyful", "triumphant", "elated", "exultant", "ecstatic", "overjoyed"],
    "KIND": ["caring", "compassionate", "gentle", "thoughtful", "considerate", "generous"],
    "LIVELY": ["energetic", "animated", "vivacious", "spirited", "active", "vibrant"],
    "LUMINOUS": ["bright", "glowing", "radiant", "shining", "brilliant", "gleaming"],
    "MAGIC": ["wonder", "enchantment", "miracle", "marvel", "sorcery", "mystical"],
    "MAGNIFICENT": ["splendid", "grand", "majestic", "glorious", "superb", "impressive"],
    "MIGHTY": ["powerful", "strong", "forceful", "potent", "great", "formidable"],
    "NOBLE": ["honorable", "dignified", "worthy", "virtuous", "admirable", "respectable"],
    "OPTIMISTIC": ["hopeful", "positive", "confident", "upbeat", "cheerful", "sanguine"],
    "PEAK": ["summit", "top", "pinnacle", "apex", "zenith", "height"],
    "PLEASED": ["happy", "satisfied", "content", "delighted", "glad", "gratified"],
    "POISE": ["composure", "grace", "balance", "elegance", "confidence", "self-assurance"],
    "PRIME": ["best", "top", "excellent", "peak", "optimal", "superior"],
    "PROSPEROUS": ["successful", "thriving", "flourishing", "wealthy", "affluent", "booming"],
    "PROWESS": ["skill", "expertise", "ability", "talent", "mastery", "competence"],
    "PURE": ["clean", "genuine", "authentic", "untainted", "pristine", "innocent"],
    "QUEST": ["journey", "pursuit", "search", "adventure", "mission", "expedition"],
    "RADIANT": ["glowing", "bright", "shining", "luminous", "brilliant", "beaming"],
    "REJUVENATE": ["refresh", "revitalize", "renew", "restore", "revive", "regenerate"],
    "RELENTLESS": ["persistent", "determined", "unstoppable", "tireless", "unyielding", "tenacious"],
    "RESILIENT": ["strong", "tough", "flexible", "adaptable", "hardy", "durable"],
    "SERENE": ["calm", "peaceful", "tranquil", "placid", "composed", "relaxed"],
    "SHARP": ["keen", "acute", "smart", "clever", "quick", "astute"],
    "SHINE": ["glow", "sparkle", "radiate", "gleam", "glitter", "beam"],
    "SMOOTH": ["sleek", "polished", "even", "effortless", "flowing", "seamless"],
    "SOAR": ["fly", "rise", "ascend", "climb", "elevate", "surge"],
    "SOLID": ["strong", "firm", "stable", "reliable", "dependable", "sturdy"],
    "SPARK": ["ignite", "inspire", "trigger", "kindle", "flash", "glimmer"],
    "SPARKLE": ["shine", "glitter", "twinkle", "gleam", "shimmer", "glisten"],
    "SPIRITED": ["lively", "energetic", "animated", "vibrant", "enthusiastic", "vivacious"],
    "STELLAR": ["outstanding", "exceptional", "excellent", "superb", "brilliant", "remarkable"],
    "SUCCESS": ["achievement", "victory", "accomplishment", "triumph", "prosperity", "win"],
    "SUPPORTIVE": ["helpful", "encouraging", "caring", "nurturing", "understanding", "compassionate"],
    "THRIVE": ["flourish", "prosper", "bloom", "succeed", "grow", "blossom"],
    "TRUE": ["genuine", "authentic", "real", "honest", "sincere", "faithful"],
    "UPBEAT": ["positive", "cheerful", "optimistic", "lively", "buoyant", "happy"],
    "UPLIFTING": ["inspiring", "encouraging", "heartening", "elevating", "moving", "motivating"],
    "VALOR": ["bravery", "courage", "heroism", "fearlessness", "gallantry", "boldness"],
    "VERVE": ["energy", "enthusiasm", "vigor", "vitality", "spirit", "zest"],
    "VIBRANT": ["lively", "vivid", "dynamic", "energetic", "colorful", "bright"],
    "VITAL": ["essential", "crucial", "important", "necessary", "energetic", "lively"],
    "VITALITY": ["energy", "vigor", "liveliness", "strength", "vivacity", "dynamism"],
    "VIVID": ["bright", "vibrant", "colorful", "intense", "striking", "lively"],
    "WILD": ["free", "untamed", "adventurous", "spirited", "unrestrained", "natural"],
    "WONDER": ["amazement", "awe", "marvel", "miracle", "fascination", "astonishment"],
    "ZEAL": ["enthusiasm", "passion", "fervor", "eagerness", "dedication", "ardor"],
    "ZENITH": ["peak", "pinnacle", "apex", "summit", "height", "climax"],
    "ZEST": ["enthusiasm", "energy", "vigor", "passion", "gusto", "excitement"],
    # Handle typos/variations found in metadata
    "HEARTNEING": ["heartening", "encouraging", "uplifting", "inspiring"],
    "RESILENCY": ["resilience", "strength", "toughness", "adaptability"]
}

def add_synonyms_to_metadata():
    # Read the existing metadata
    with open('metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Add synonyms to each file entry
    for file_entry in metadata['files']:
        synonyms_list = []
        for word in file_entry.get('words', []):
            word_upper = word.upper()
            if word_upper in SYNONYMS:
                synonyms_list.extend(SYNONYMS[word_upper])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_synonyms = []
        for syn in synonyms_list:
            if syn.lower() not in seen:
                seen.add(syn.lower())
                unique_synonyms.append(syn)
        
        file_entry['synonyms'] = unique_synonyms
    
    # Write the updated metadata back
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Added synonyms to {len(metadata['files'])} files")

if __name__ == '__main__':
    add_synonyms_to_metadata()
