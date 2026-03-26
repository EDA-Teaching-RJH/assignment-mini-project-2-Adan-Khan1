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
