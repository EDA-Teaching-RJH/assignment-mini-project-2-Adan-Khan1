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


# ==========================================
# BLOCK 2: The Object Oriented Brain
# ==========================================
# FEATURE 2: Using the extractors from Block 1 to populate these objects and then apply clinical trial rules to the extracted data

class PatientRecord: 
    """
    Handles universal patient data not specific to a single disease
    """
    def __init__(self, patient_id, raw_text): # This base class establishes universal traits every patient has
        self.patient_id = patient_id 
        self.age = extract_age(raw_text)
        self.prostate_volume = extract_volume(raw_text)
        self.status = "Pending"
        self.reason = "Awaiting Evaluation"

class UrologyPatient(PatientRecord): 
    """
    This subclass will inherit universal traits, adds prostate-specific metrics and NICE logic
    """
    def __init__(self, patient_id, raw_text): 
        super().__init__(patient_id, raw_text) #  This pulls in the ID, age and volume from the Parent class
        self.gleason = extract_gleason(raw_text)
        self.psa = extract_psa(raw_text)
        self.t_stage = extract_t_stage(raw_text)

    def evaluate_eligibility(self): 
        """
        This is the rule engine, it applies NICE NG131 CPG criteria using relaxed clinical 'OR' Logic
        """
        # 1. Edge Case Handling: Filter out non-urology noise immediately
        if self.gleason is None and self.psa is None and self.t_stage is None:   
            self.status = "Ineligible - No Data"
            self.reason = "ExcludedL No prostate oncology metrics detected. Irrelevant record"
            return
        
        # 2. Safety Insurance: Age Constraint for theoretical trial bounds 
        if self.age is None or self.age > 80: 
            self.status = "Ineligible"
            self.reason = "Excluded: patient exceeds age limits for trial for trial safety"
            return 
        
        # 3. Data Safety: Convert 'None' types to 0 locally so Python math operators like (>, <, ==) don't crash when evaluating missing metrics
        safe_gleason = self.gleason if self.gleason is not None else 0 
        safe_psa = self.psa if self.psa is not None else 0 
        safe_t_stage = self.t_stage if self.t_stage is not None else "Unknown"

        # 4. The NICE NG131 Logic Gates 
        high_risk_count = 0 
        if safe_gleason == 8: high_risk_count += 1
        if safe_psa > 20: high_risk_count += 1
        if "T3" in safe_t_stage: high_risk_count += 1 

        # Cascading OR: Extreme severity in a single metric forces trial inclusion, bypassing the need for perfect data 
        if safe_gleason >= 9 or "T4" in safe_t_stage or high_risk_count >= 2: 
            self.status = "Eligible - CPG 5"
            self.reason = "Included: high Risk (CPG 5) clinically identified"
        elif high_risk_count == 1: 
            self.status = "Eligible - CPG 4"
            self.reason = "Included: High Risk (CPG 4) clinically identified"

        #Missing data is risky for lower tiers, required human clinician review 
        elif self.gleason is None or self.psa is None:
            self.status = "Manual Review"
            self.reason = "Incomplete metric. Cannot safely confirm low/intermediate risk."
        
        elif safe_gleason == 7 and safe_psa <= 20: 
            self.status = "Eligible - CPG 2/3"
            self.reason = "Included: Intermediate Risk identified."

        elif safe_gleason <= 6 and safe_psa < 10: 
            self.status = "Ineligible - CPG 1"
            self.reason = "Excluded: Disease state too low (CPG 1)."
        
        else: 
            self.status = "Manual Review"
            self.reason = "Metrics present but boundary condition unclear"
        
    


