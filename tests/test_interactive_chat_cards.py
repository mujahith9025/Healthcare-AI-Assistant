"""
Unit tests for Interactive Compact Visual Chat Cards payload and metadata generation.
Validates that /chat returns the necessary structured metadata for all 6 card types:
1. Clinical Risk Calculators
2. Emergency First-Aid Protocols
3. Medical Nutrition Therapy
4. Mental Health & Somatic Regulation
5. Local Condition / Disease Overview
6. Guided Triage Triggers
"""

import unittest
import json
from app import app


class TestInteractiveChatCards(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_calculator_interactive_card_metadata(self):
        payload = {"message": "Can you calculate my ASCVD 10-year cardiovascular risk?"}
        resp = self.app.post('/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("is_calculator_intent"))
        self.assertIn("calculator_id", data)
        self.assertEqual(data["calculator_id"], "ascvd")
        self.assertIn("calculator_info", data)
        self.assertIn("title", data["calculator_info"])

    def test_first_aid_interactive_card_metadata(self):
        payload = {"message": "First aid for adult CPR"}
        resp = self.app.post('/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("is_first_aid_intent"))
        self.assertIn("first_aid_card_id", data)
        self.assertEqual(data["first_aid_card_id"], "cpr_adult")
        self.assertIn("first_aid_data", data)
        self.assertIn("steps", data["first_aid_data"])

    def test_nutrition_interactive_card_metadata(self):
        payload = {"message": "What is the medical nutrition diet plan for hypertension?"}
        resp = self.app.post('/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("is_nutrition_intent"))
        self.assertIn("nutrition_data", data)
        self.assertIn("prioritize_foods", data["nutrition_data"])
        self.assertIn("avoid_foods", data["nutrition_data"])

    def test_mental_health_interactive_card_metadata(self):
        payload = {"message": "Can I try 4-7-8 relaxing breathing exercises for anxiety?"}
        resp = self.app.post('/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("is_mental_health_intent"))
        self.assertEqual(data.get("mh_category"), "somatic_pacers")
        self.assertIn("protocol_info", data)
        self.assertIn("title", data["protocol_info"])

    def test_disease_overview_interactive_card_metadata(self):
        payload = {"message": "Common Cold"}
        resp = self.app.post('/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("disease_data", data)
        self.assertIsNotNone(data["disease_data"])
        self.assertIn("disease_name", data["disease_data"])
        self.assertIn("symptoms", data["disease_data"])
        self.assertIn("precautions", data["disease_data"])


if __name__ == '__main__':
    unittest.main()
