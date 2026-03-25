import re

# ====================
# BLOCK 1: Deterministic Extraction (REGEX)
# FEATURE 1: Building the language parser first. This will use pattern matching to find the specific medical information inside the patient transcripts

def extract_gleason(text): 
    """
    Extracts the total Gleason Score. Looks for patterns like 'Gleason 4+3=7', or 'Gleason 8'.
    """
    match = re.search(r"Gleason\s*(?:score|grade)?\s*(?:of)?\s*(?:(?:\d\s*\+\s*\d\s*=\s*)?(\d+))", str(text), re.IGNORECASE) # The (?:  ) looks for the words but does not save them. The (\d+) is the actual capture group that extracts the final integer score
    if match: 
        return int(match.group(1))
    return None

def extract_psa(text): 
    """
    Extracts the PSA level as a float. Accounts for decimals and shorthand like 'PSA is 14.2'. 
    """ 
    match = re.search(r"PSA\s*(?:of|is|level)?\s*[:\-]?\s*(\d+\.?\d*)", str(text), re.IGNORECASE) # \.?\d* means we capture floating point decimals, not just whole numbers
    if match: 
        return int(match.group(1))
    return None

def extract_volume(text): 
    """
    Extracts Prostate volume in cc or grams.
    """
    match = re.search(r"(?:prostate)?\s*volume\s*(?:of)?\s*(\d+\.?\d*)\s*(?:cc|ml|grams|g)", str(text), re.IGNORECASE)
    if match: 
        return float(match.group(1))
    return None 