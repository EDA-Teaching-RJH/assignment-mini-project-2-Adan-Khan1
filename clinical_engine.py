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

def extract_psa(text): 
    """
    Extracts the PSA level as a float. Accounts for decimals and shorthand like 'PSA is 14.2' 
    """
    match = re.search(r"PSA\s*(?:of|is|level)?\s*[:\-]?\s*(\d+\.?\d*)", str(text), re.IGNORECASE) # (\.?\d*) enables that we capture floating point decimals, not just whole numbers
    if match: 
        return float(match.group(1))
    return None    

def extract_t_stage(text): 
    """
    Extracts the clinical T-Stage (ie T1c, T2a or T3 etc)
    """
    match = re.search(r"(T[1-4][a-c]?)", str(text), re.IGNORECASE) # T stages are alphanumerical characters with [1-4] limitng the number to valid staging tiers and [a-c]? allows for optional sub-staging if present
    if match: 
        return match.group(1).upper()
    return None 

def extract_volume(text): 
    """
    Extracts prostate volume in cc or grams
    """
    match = re.search(r"(?:prostate)?\s*volume\s*(?:of)?\s*(\d+\.?\d*)\s*(?:cc|ml|grams|g)", str(text), re.IGNORECASE)
    if match: 
        return float(match.group(1))
    return None

def extract_age(text): 
    """
    Extracts patient age from the patient transcripts
    """
    match = re.search(r"(\d{2})\s*(?:-|year old|yo|y\.o\.)", str(text), re.IGNORECASE)
    if match: 
        return int(match.group(1))
    return None
