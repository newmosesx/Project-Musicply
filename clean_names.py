import os
import re

def clean_song_name(filename):
    """
    Cleans a single song filename using a series of regular expressions and cleanup steps.
    """
    # Don't touch the extension yet
    name, extension = os.path.splitext(filename)

    # --- Step 1: Define all the junk patterns to remove ---
    # This list is now more comprehensive.
    junk_patterns = [
        # --- Website names and download sources ---
        r'SIMP3\.(COM|BIZ)', r'FELIZMP3\.COM', r'ytmp3s', r'genteflow\.icu', 
        r'y2mate\.com', r'ni2ni3',
        
        # --- Common channel names and upload tags ---
        r'GRM Daily', r'WSHH Exclusive', r'Pressplay', r'MixtapeMadness',
        r'TheUk Lyrics', r'AdloMusic', 'Ultra Music', 'OnASpaceship',
        
        # --- Generic video/audio descriptions (more robust) ---
        # This now catches Video, Audio, Lyrics, Visualizer, etc., in many forms
        r'\[\s*(Official|Music|Lyric|Audio|Dance|HD|Video|Visualizer|Videoclip)\s*.*?\]',
        r'\(\s*(Official|Music|Lyric|Audio|Dance|HD|Video|Visualizer|Videoclip)\s*.*?[\)\]]',
        r'\(Letra[u\/0-9-]*Lyrics\)', # Catches (Letra/Lyrics), (Letra-Lyrics)
        r'Video\s*Oficial', # Catches "Video Oficial" even without brackets
        r'Shot\s*by\s*\w+', # Catches "Shot by Ballve"
        
        # --- Producer tags and other metadata ---
        r'\[\s*Prod\s*\.?\s*by.*?\]', # Catches [Prod. by ...]
        r'\(\s*Prod\s*\.?\s*by.*?[\)\]]', # Catches (Prod. by ...)
        r'Prod\s*\.?\s*by\s*[\w\s&]+', # Catches "Prod by" without brackets
        
        # --- Rap battle / Parody / Other specific junk ---
        r'COMBATES\s*MORTALES\s*DE\s*RAP.*',
        r'Record of Ragnarok.*',
        r'(Parodia.*)',
        
        # --- Other common junk ---
        r'\_?\s*from\s*.*?soundtrack', # Catches 'from _Black Panther...'
        r'\(Funk Explode\)',
        r'by\s*joker502',
        r'Un\s*Verano\s*Sin\s*Ti',
        
        # --- Numbered duplicates like (1), (2), etc. ---
        r'\(\d+\)',
    ]

    # Combine all patterns into a single regex, separated by '|' (OR)
    combined_pattern = re.compile('|'.join(junk_patterns), re.IGNORECASE)
    clean_name = re.sub(combined_pattern, '', name)

    # --- Step 2: Character and Emoji Cleanup ---
    
    # Remove hashtags but keep the content (e.g., #53 -> 53)
    clean_name = clean_name.replace('#', '')

    # Remove HTML entity for '&'
    clean_name = clean_name.replace('&', '&')
    
    # Remove common emojis and symbols
    # This regex covers a wide range of pictorial symbols.
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\u2600-\u26FF"          # miscellaneous symbols
        u"\u2700-\u27BF"          # dingbats
        u"\u2B50"                # star
        u"\uFE0F"                # variation selector
        u"🕯"                     # candle
        u"║"                     # box drawing
        u"❌"                     # cross mark
        "]+",
        flags=re.UNICODE,
    )
    clean_name = emoji_pattern.sub('', clean_name)


    # --- Step 3: Final Whitespace and Artifact Cleanup ---
    
    # Replace various separators with a standard space
    clean_name = re.sub(r'[_\-—|]+', ' ', clean_name) # a longer dash
    
    # Remove empty parentheses or brackets, e.g., () or []
    clean_name = re.sub(r'\(\s*\)', '', clean_name)
    clean_name = re.sub(r'\[\s*\]', '', clean_name)
    
    # Standardize all whitespace to single spaces. This is very powerful.
    # It fixes issues like "Artist  -  Title" -> "Artist - Title"
    clean_name = ' '.join(clean_name.split())
    
    # Remove any leading/trailing spaces, hyphens, or dots that might be left
    clean_name = clean_name.strip(' .-_')

    # Put the filename back together
    return f"{clean_name}{extension}"