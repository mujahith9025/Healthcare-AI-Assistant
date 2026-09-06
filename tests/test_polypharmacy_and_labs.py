"""
Unit and integration tests for Multi-Drug Polypharmacy Matrix and Medical Lab Test Interpreter.
"""

import unittest
import json
from app import app
from safety.polypharmacy_matrix import (
    check_polypharmacy_interactions,
    scan_text_for_polypharmacy,
    DRUG_INTERACTIONS_DB
)
from safety.lab_interpreter import (
    interpret_lab_result,
    detect_and_interpret_vitals_in_query,
    LAB_TESTS_CATALOG
)


class TestPolypharmacyAndLabs(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # -------------------------------------------------------------------------
    # Polypharmacy Matrix Tests
    # -------------------------------------------------------------------------
    def test_warfarin_nsaid_major_interaction(self):
        result = check_polypharmacy_interactions(["Warfarin", "Ibuprofen"])
        self.assertEqual(result["total_interactions"], 1)
        self.assertEqual(result["severity_summary"], "MAJOR")
        self.assertIn("bleeding", result["interactions"][0]["effects"].lower())

    def test_ace_inhibitor_potassium_interaction(self):
        result = check_polypharmacy_interactions(["Lisinopril", "Potassium"])
        self.assertEqual(result["total_interactions"], 1)
        self.assertEqual(result["severity_summary"], "MAJOR")
        self.assertIn("hyperkalemia", result["interactions"][0]["effects"].lower())

    def test_ssri_tramadol_serotonin_syndrome(self):
        result = check_polypharmacy_interactions(["Sertraline", "Tramadol"])
        self.assertEqual(result["total_interactions"], 1)
        self.assertEqual(result["severity_summary"], "MAJOR")
        self.assertIn("serotonin syndrome", result["interactions"][0]["title"].lower())

    def test_beta_blocker_asthma_contraindication(self):
        result = check_polypharmacy_interactions(["Propranolol", "Asthma"])
        self.assertEqual(result["total_interactions"], 1)
        self.assertEqual(result["severity_summary"], "MAJOR")
        self.assertIn("asthma", result["interactions"][0]["effects"].lower())

    def test_safe_drug_combination(self):
        result = check_polypharmacy_interactions(["Acetaminophen", "Amoxicillin"])
        self.assertEqual(result["total_interactions"], 0)
        self.assertEqual(result["severity_summary"], "NONE")

    def test_text_scanning_for_polypharmacy(self):
        query = "I am currently taking Warfarin and my doctor recommended Ibuprofen for pain."
        detected = scan_text_for_polypharmacy(query)
        self.assertIsNotNone(detected)
        self.assertEqual(detected["severity_summary"], "MAJOR")
        self.assertTrue(len(detected["interactions"]) > 0)

    # -------------------------------------------------------------------------
    # Lab Biomarker Interpreter Tests
    # -------------------------------------------------------------------------
    def test_glucose_interpretation_ranges(self):
        # Low
        res_low = interpret_lab_result("fasting_glucose", 60)
        self.assertEqual(res_low["tier"], "LOW")

        # Optimal
        res_opt = interpret_lab_result("fasting_glucose", 88)
        self.assertEqual(res_opt["tier"], "OPTIMAL")

        # Borderline / Pre-diabetes
        res_bord = interpret_lab_result("fasting_glucose", 112)
        self.assertEqual(res_bord["tier"], "BORDERLINE")

        # High / Diabetes range
        res_high = interpret_lab_result("fasting_glucose", 165)
        self.assertEqual(res_high["tier"], "HIGH")

    def test_blood_pressure_interpretation(self):
        # Normal
        bp_norm = interpret_lab_result("blood_pressure", 116, 76)
        self.assertEqual(bp_norm["tier"], "OPTIMAL")

        # Stage 1
        bp_s1 = interpret_lab_result("blood_pressure", 134, 86)
        self.assertEqual(bp_s1["tier"], "STAGE_1")

        # Stage 2
        bp_s2 = interpret_lab_result("blood_pressure", 152, 94)
        self.assertEqual(bp_s2["tier"], "STAGE_2")

        # Crisis
        bp_crit = interpret_lab_result("blood_pressure", 185, 125)
        self.assertEqual(bp_crit["tier"], "CRITICAL_HIGH")
        self.assertIn("Crisis", bp_crit["tier_label"])

    def test_detect_vitals_in_query(self):
        query = "My blood pressure reading came back as 145/92 mmHg today."
        vitals = detect_and_interpret_vitals_in_query(query)
        self.assertIsNotNone(vitals)
        self.assertEqual(vitals["test_id"], "blood_pressure")
        self.assertEqual(vitals["tier"], "STAGE_2")

    # -------------------------------------------------------------------------
    # Flask Endpoints Integration Tests
    # -------------------------------------------------------------------------
    def test_api_check_interactions_endpoint(self):
        response = self.app.post(
            '/api/check-interactions',
            data=json.dumps({"drugs": ["Warfarin", "Aspirin"]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["interaction_count"], 0)

    def test_api_lab_tests_endpoint(self):
        response = self.app.get('/api/lab-tests')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("metabolic", data["panels"])
        self.assertIn("lipids", data["panels"])

    def test_api_interpret_lab_endpoint(self):
        response = self.app.post(
            '/api/interpret-lab',
            data=json.dumps({
                "test_key": "hba1c",
                "value": 7.4
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "high")
        self.assertIn("Diabetes", data["status_label"])


if __name__ == '__main__':
    unittest.main()
