import unittest
from clinical_engine import UrologyPatient, extract_psa, extract_gleason, extract_volume, extract_t_stage, extract_age

class TestClinicalEngine(unittest.TestCase):


    # ==========================================
    # BLOCK 1: REGEX COMPONENT TESTS
    # ==========================================
    # First test the deterministic extractors to ensure they pullthe correct data types (integers, floats, strings) and handle missing data.

    def test_regex_psa_and_gleason(self):
        """Tests if Regex correctly parses core oncology metrics."""
        dummy_text = "PSA is 14.2. Gleason score 4+3=7."
        self.assertEqual(extract_psa(dummy_text), 14.2)
        self.assertEqual(extract_gleason(dummy_text), 7)

    def test_regex_volume(self):
        """Tests extraction of prostate volume in various units."""
        dummy_text = "The prostate volume of 45.5 cc was noted."
        self.assertEqual(extract_volume(dummy_text), 45.5)

    def test_regex_t_stage(self):
        """Tests extraction of alphanumeric clinical staging."""
        dummy_text = "Clinical staging is T2b."
        self.assertEqual(extract_t_stage(dummy_text), "T2B")

    def test_regex_age(self):
        """Tests extraction of patient age from standard shorthand."""
        dummy_text = "This 65-year-old male presents today."
        self.assertEqual(extract_age(dummy_text), 65)

    def test_regex_missing_data(self):
        """Tests edge case: Does the regex handle missing data gracefully?"""
        dummy_text = "Patient is here for a follow up. No labs available."
        self.assertIsNone(extract_psa(dummy_text))
        self.assertIsNone(extract_gleason(dummy_text))
        self.assertIsNone(extract_volume(dummy_text))


    # ==========================================
    # BLOCK 2: OOP RULE ENGINE TESTS
    # ==========================================
    # Now testing the logic to ensure the NICE NG131 rules are applied correctly and that the Cascading OR logic functions safely 

    def test_oop_cpg_logic_high_risk(self):
        """Tests if the Rule Engine correctly identifies a CPG 5 patient."""
        dummy_text = "70 yo male. Gleason 9. PSA level 25. T4."
        patient = UrologyPatient(patient_id="TEST_01", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Eligible - CPG 5")

    def test_oop_cpg_logic_cpg4(self):
        """Tests if the Rule Engine correctly identifies a CPG 4 patient (1 high risk marker)."""
        dummy_text = "55 yo male. Gleason 8. PSA 12. T2c."
        patient = UrologyPatient(patient_id="TEST_01b", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Eligible - CPG 4")

    def test_oop_cpg_logic_intermediate(self):
        """Tests if the Rule Engine correctly identifies a CPG 2/3 intermediate patient."""
        dummy_text = "62 yo male. Gleason 7. PSA 15. T2a."
        patient = UrologyPatient(patient_id="TEST_01c", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Eligible - CPG 2/3")

    def test_oop_cpg_logic_low_risk(self):
        """Tests if the Rule Engine excludes low risk (CPG 1) patients."""
        dummy_text = "50 yo male. Gleason 6. PSA 5. T1c."
        patient = UrologyPatient(patient_id="TEST_01d", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Ineligible - CPG 1")

    def test_oop_manual_review_trigger(self):
        """Tests if missing vital metrics properly triggers a Manual Review state."""
        dummy_text = "70 yo patient. Gleason 7, but PSA is pending."
        patient = UrologyPatient(patient_id="TEST_02", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Manual Review")

    def test_oop_age_exclusion(self):
        """Tests the Safety Interlock: Patients over 80 should be strictly excluded."""
        dummy_text = "85 yo male. Gleason 9. PSA level 25. T4."
        patient = UrologyPatient(patient_id="TEST_03", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Ineligible")
        self.assertTrue("age limits" in patient.reason.lower())

    def test_oop_completely_empty_data(self):
        """Tests extreme edge case: A completely empty or irrelevant medical note."""
        dummy_text = "Patient arrived for a broken arm. X-rays negative."
        patient = UrologyPatient(patient_id="TEST_04", raw_text=dummy_text)
        patient.evaluate_eligibility()
        self.assertEqual(patient.status, "Ineligible - No Data")
        self.assertTrue("no prostate oncology metrics" in patient.reason.lower())

if __name__ == '__main__':
    unittest.main()
