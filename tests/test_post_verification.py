"""
Unit Tests for Two-Stage Post-Generation Verification Guard.
Tests:
- Dosage & prescription statement interception
- Miracle cure and guaranteed claim calibration
- Emergency referral injection when red flags are present
- Disclaimer enforcement
- Citation domain whitelisting and invalid domain scrubbing
- Safety confidence score calculation
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from safety.post_verification import (
    Stage1ClinicalRuleValidator,
    Stage2FactConsistencyVerifier,
    TwoStageVerificationGuard,
    verify_and_filter_response
)

class TestTwoStageVerification(unittest.TestCase):

    def setUp(self):
        self.guard = TwoStageVerificationGuard()

    def test_dosage_interception(self):
        raw_text = "You should take 500mg paracetamol every 6 hours and take 2 pills of ibuprofen."
        sanitized, mods = Stage1ClinicalRuleValidator.sanitize_prescriptive_dosages(raw_text)
        self.assertIn("prescriptive_dosage_intercepted", mods)
        self.assertNotIn("500mg", sanitized)
        self.assertNotIn("2 pills", sanitized)
        self.assertIn("consult your doctor or pharmacist", sanitized)

    def test_unscientific_certainty_calibration(self):
        raw_text = "Drinking this herbal mixture is a guaranteed cure that will 100% cure your migraine permanently."
        calibrated, mods = Stage1ClinicalRuleValidator.calibrate_unscientific_certainty(raw_text)
        self.assertIn("unscientific_certainty_calibrated", mods)
        self.assertNotIn("100% cure", calibrated)
        self.assertNotIn("guaranteed cure", calibrated)

    def test_emergency_safety_injection(self):
        user_q = "My father has crushing chest pain and shortness of breath"
        raw_text = "Chest pain can be caused by acid reflux or anxiety. Try taking a warm bath."
        validated, mods = Stage1ClinicalRuleValidator.validate_emergency_safety(raw_text, user_q, region="US")
        self.assertIn("emergency_warning_injected", mods)
        self.assertIn("URGENT MEDICAL NOTICE", validated)
        self.assertIn("911", validated)

    def test_disclaimer_enforcement(self):
        raw_text = "Headaches can be triggered by dehydration. Drink plenty of water."
        enforced, mods = Stage1ClinicalRuleValidator.enforce_clinical_disclaimer(raw_text)
        self.assertIn("clinical_disclaimer_appended", mods)
        self.assertIn("consult a qualified healthcare professional", enforced.lower())

    def test_citation_domain_whitelisting(self):
        raw_citations = [
            {"name": "World Health Organization", "url": "https://www.who.int/news-room/fact-sheets/detail/migraine"},
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/diseases-conditions/headaches"},
            {"name": "Spam Scam Drug Store", "url": "https://buy-cheap-drugs-online.xyz/pills"},
            {"name": "Unverified Blog", "url": "http://miracle-cures-daily.fake/remedy"}
        ]
        verified_citations, mods = Stage2FactConsistencyVerifier.sanitize_citations(raw_citations)
        self.assertEqual(len(verified_citations), 2)
        self.assertEqual(verified_citations[0]["name"], "World Health Organization")
        self.assertEqual(verified_citations[1]["name"], "Mayo Clinic")
        self.assertTrue(any("unwhitelisted_citation_scrubbed" in m for m in mods))

    def test_full_pipeline_verification(self):
        user_query = "What is the best way to handle migraine?"
        raw_reply = "Migraine can cause throbbing pain. Rest in a dark quiet room and stay hydrated. Consult your doctor for tailored care."
        rag_context = "Migraine is a neurological condition causing throbbing headache, nausea, and light sensitivity."
        citations = [
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/migraine"},
            {"name": "Fake Site", "url": "https://phishing-site.xyz"}
        ]

        result = verify_and_filter_response(
            raw_reply=raw_reply,
            user_query=user_query,
            rag_context=rag_context,
            citations=citations,
            region="US"
        )

        self.assertTrue(result["is_verified"])
        self.assertGreaterEqual(result["safety_score"], 0.85)
        self.assertEqual(len(result["citations"]), 1)
        self.assertEqual(result["citations"][0]["name"], "Mayo Clinic")
        self.assertIn("stage_1_clinical_rules", result["stages_passed"])
        self.assertIn("stage_2_fact_consistency", result["stages_passed"])

if __name__ == "__main__":
    unittest.main()
