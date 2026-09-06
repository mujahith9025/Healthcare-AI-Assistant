import unittest
import json
from app import app
from safety.mental_health_toolkit import (
    evaluate_phq9,
    evaluate_gad7,
    evaluate_pc_ptsd5,
    evaluate_isi,
    evaluate_pss4,
    evaluate_cage_aid,
    generate_stanley_brown_safety_plan,
    get_mental_health_catalog,
    evaluate_mental_health_assessment,
    detect_mental_health_intent,
    SOMATIC_PROTOCOLS
)

class TestMentalHealthToolkit(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # 1. PHQ-9 Depression Tests & Suicide Gate
    def test_phq9_minimal_score(self):
        result = evaluate_phq9([0, 1, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["tier"], "MINIMAL")
        self.assertFalse(result["has_suicide_flag"])

    def test_phq9_severe_score_with_suicide_flag(self):
        # Q9 = 3 (thoughts of death or self harm)
        result = evaluate_phq9([3, 3, 3, 2, 2, 2, 3, 1, 3])
        self.assertEqual(result["score"], 22)
        self.assertEqual(result["tier"], "SEVERE")
        self.assertTrue(result["has_suicide_flag"])
        self.assertIn("CRITICAL CRISIS ALERT", result["safety_alert"])
        self.assertIn("988", result["safety_alert"])

    # 2. GAD-7 Anxiety Tests
    def test_gad7_scoring(self):
        result = evaluate_gad7([2, 3, 2, 2, 2, 1, 1])
        self.assertEqual(result["score"], 13)
        self.assertEqual(result["tier"], "MODERATE")
        self.assertIn("Generalized Anxiety", result["clinical_action"])

    # 3. PC-PTSD-5 Screen Tests
    def test_pc_ptsd5_positive_cutoff(self):
        result = evaluate_pc_ptsd5([True, True, True, False, False])
        self.assertEqual(result["score"], 3)
        self.assertTrue(result["is_positive"])
        self.assertEqual(result["tier"], "POSITIVE_SCREEN")

    def test_pc_ptsd5_negative_cutoff(self):
        result = evaluate_pc_ptsd5([True, False, False, False, False])
        self.assertEqual(result["score"], 1)
        self.assertFalse(result["is_positive"])
        self.assertEqual(result["tier"], "NEGATIVE_SCREEN")

    # 4. ISI Insomnia Tests
    def test_isi_insomnia_scoring(self):
        result = evaluate_isi([3, 3, 2, 3, 2, 3, 2])
        self.assertEqual(result["score"], 18)
        self.assertEqual(result["tier"], "MODERATE")
        self.assertIn("CBT-I", result["clinical_action"])

    # 5. PSS-4 Perceived Stress Tests (Reverse-scoring check)
    def test_pss4_reverse_scoring(self):
        # Q0=3, Q1=0 (reverse -> 4), Q2=0 (reverse -> 4), Q3=3 -> Total = 3 + 4 + 4 + 3 = 14
        result = evaluate_pss4([3, 0, 0, 3])
        self.assertEqual(result["score"], 14)
        self.assertEqual(result["tier"], "HIGH")

    # 6. CAGE-AID Substance Tests
    def test_cage_aid_positive(self):
        result = evaluate_cage_aid([True, True, False, False])
        self.assertEqual(result["score"], 2)
        self.assertTrue(result["is_positive"])
        self.assertEqual(result["tier"], "POSITIVE_SCREEN")
        self.assertIn("SAMHSA", result["clinical_action"])

    # 7. Somatic Protocols Catalog Verification
    def test_somatic_protocols_structure(self):
        self.assertIn("box_breathing", SOMATIC_PROTOCOLS)
        self.assertIn("relaxing_478", SOMATIC_PROTOCOLS)
        self.assertIn("physiological_sigh", SOMATIC_PROTOCOLS)
        self.assertIn("grounding_54321", SOMATIC_PROTOCOLS)
        self.assertIn("pmr_jacobson", SOMATIC_PROTOCOLS)

        # Verify Box Breathing 4-4-4-4 phases
        box = SOMATIC_PROTOCOLS["box_breathing"]
        self.assertEqual(len(box["phases"]), 4)
        for phase in box["phases"]:
            self.assertEqual(phase["duration"], 4)

        # Verify 5-4-3-2-1 Sensory Grounding steps
        g54321 = SOMATIC_PROTOCOLS["grounding_54321"]
        self.assertEqual(len(g54321["steps"]), 5)
        self.assertEqual(g54321["steps"][0]["count"], 5)

        # Verify PMR Jacobson 8 muscle zones
        pmr = SOMATIC_PROTOCOLS["pmr_jacobson"]
        self.assertEqual(len(pmr["muscle_zones"]), 8)

    # 8. Stanley-Brown Safety Plan Generator
    def test_generate_stanley_brown_safety_plan(self):
        payload = {
            "warning_signs": ["Insomnia", "Racing heartbeat"],
            "coping_strategies": ["Box Breathing", "Walking in park"],
            "social_distractions": ["Library", "Coffee shop"],
            "trusted_contacts": ["Mom (555-0192)"],
            "professionals": ["Dr. Smith (555-0188)"],
            "environment_safety": ["Medications safely stored"]
        }
        res = generate_stanley_brown_safety_plan(payload)
        self.assertTrue(res["success"])
        self.assertTrue(res["is_complete"])
        self.assertIn("step1_warning_signs", res["plan"])
        self.assertIn("step5_emergency_hotlines", res["plan"])

    # 9. Intent Detection Engine Tests
    def test_detect_mental_health_intent(self):
        self.assertEqual(detect_mental_health_intent("Can I do a box breathing exercise?")["protocol_id"], "box_breathing")
        self.assertEqual(detect_mental_health_intent("start 4-7-8 breathing")["protocol_id"], "relaxing_478")
        self.assertEqual(detect_mental_health_intent("how to do a physiological sigh")["protocol_id"], "physiological_sigh")
        self.assertEqual(detect_mental_health_intent("help me with 5-4-3-2-1 grounding")["protocol_id"], "grounding_54321")
        self.assertEqual(detect_mental_health_intent("progressive muscle relaxation guide")["protocol_id"], "pmr_jacobson")
        self.assertEqual(detect_mental_health_intent("take PHQ-9 depression scale")["scale_id"], "phq9")
        self.assertEqual(detect_mental_health_intent("take GAD-7 anxiety test")["scale_id"], "gad7")
        self.assertEqual(detect_mental_health_intent("create a stanley brown safety plan")["type"], "safety_plan")

    # 10. Universal Dispatcher Tests & Somatic Cross-Recommendations
    def test_evaluate_mental_health_assessment_cross_recs(self):
        res = evaluate_mental_health_assessment("gad7", [2, 2, 2, 2, 2, 2, 2])
        self.assertTrue(res["success"])
        self.assertEqual(res["score"], 14)
        self.assertIn("recommended_somatic_protocols", res)
        self.assertGreater(len(res["recommended_somatic_protocols"]), 0)

    # 11. REST API Endpoints Tests
    def test_api_get_mental_health_tools(self):
        response = self.app.get('/api/mental-health/tools')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("success"))
        self.assertIn("scales", data)
        self.assertIn("somatic_protocols", data)

    def test_api_assess_endpoint_success(self):
        payload = {
            "scale_id": "phq9",
            "answers": [1, 1, 1, 1, 0, 0, 0, 0, 0]
        }
        response = self.app.post('/api/mental-health/assess',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 4)
        self.assertEqual(data["tier"], "MINIMAL")

    def test_api_safety_plan_endpoint(self):
        payload = {
            "warning_signs": ["Negative thoughts"],
            "coping_strategies": ["Breathing"],
            "trusted_contacts": ["Sister"]
        }
        response = self.app.post('/api/mental-health/safety-plan',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertTrue(data["is_complete"])

    # 12. Chat Endpoint Intent Detection Test
    def test_chat_mental_health_intent(self):
        payload = {"message": "How do I do box breathing for panic?"}
        response = self.app.post('/chat',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("is_mental_health_intent"))
        self.assertEqual(data.get("protocol_id"), "box_breathing")

if __name__ == '__main__':
    unittest.main()
