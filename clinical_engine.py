import re 

# ==========================================
# BLOCK 1: Deterministic Extraction (REGEX)
# ==========================================
# FEATURE 1: Building a language parser first. These functions use pattern matching to find specific medical data inside messy and variable patient records 

def extract_gleason(text): 
    """
    Extracts the total Gleason Score. Looks for patterns like 'Gealson 4+3=7', 'Gleason score of 7', or 'Gleason 8'
    """
    match = re.search(r"Gleason\s*(?:score|grade)?\s*(?:of)?\s*(?:(?:\d\s*\+\s*\d\s*=\s*)?(\d+))", str(text), re.IGNORECASE) # Using (?:  ) allows it to just look for those words but not save them. (\d+) however is the actual capture command that extracts the final integer score 
    if match: 
        return int(match.group(1))
    return None 