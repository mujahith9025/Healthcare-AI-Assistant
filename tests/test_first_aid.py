"""
Unit and Integration Tests for Interactive First-Aid & Emergency Action Flashcards Module.
Tests catalog integrity, category grouping, search ranking, critical DO NOT rules,
CPR 110 BPM metronome parameters, and Flask REST endpoints.
"""

import unittest
from app import app
from safety.first_aid_cards import (
    FIRST_AID_CARDS_CATALOG,
    get_all_first_aid_cards,
    get_first_aid_card,
    search_first_aid_cards
)


class TestFirstAidCards(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_catalog_size_and_categories(self):
        """Ensure catalog has at least 14 evidence-based emergency protocols across all 4 categories."""
        self.assertGreaterEqual(len(FIRST_AID_CARDS_CATALOG), 14)
        
        categories = set(c["category"] for c in FIRST_AID_CARDS_CATALOG.values())
        expected_cats = {"life_threatening", "trauma", "medical_crisis", "everyday_injuries"}
        self.assertEqual(categories, expected_cats)

    def test_card_structure_and_mandatory_fields(self):
        """Ensure all 14 protocols have required clinical fields and valid step sequences."""
        for cid, card in FIRST_AID_CARDS_CATALOG.items():
            self.assertEqual(card["id"], cid)
            self.assertTrue(card.get("title"), f"Card {cid} missing title")
            self.assertTrue(card.get("icon"), f"Card {cid} missing icon")
            self.assertIn(card.get("priority"), ["CRITICAL", "URGENT", "STANDARD"], f"Card {cid} invalid priority")
            self.assertTrue(card.get("summary"), f"Card {cid} missing summary")
            self.assertIsInstance(card.get("critical_donots"), list, f"Card {cid} donots not a list")
            self.assertGreaterEqual(len(card["critical_donots"]), 2, f"Card {cid} should have at least 2 DO NOTs")
            
            # Check prohibited wording in DO NOTs
            for donot in card["critical_donots"]:
                self.assertTrue(
                    donot.startswith("DO NOT") or donot.startswith("NEVER") or "DO NOT" in donot,
                    f"Warning in {cid} does not contain prohibited phrasing: {donot}"
                )

            # Check sequential action steps
            steps = card.get("steps", [])
            self.assertGreaterEqual(len(steps), 3, f"Card {cid} has fewer than 3 steps")
            for idx, step in enumerate(steps, start=1):
                self.assertEqual(step["step_num"], idx, f"Card {cid} step sequence mismatch at {idx}")
                self.assertTrue(step.get("title"), f"Card {cid} step {idx} missing title")
                self.assertTrue(step.get("action"), f"Card {cid} step {idx} missing action")
                self.assertTrue(step.get("visual_hint"), f"Card {cid} step {idx} missing visual hint")

    def test_cpr_metronome_parameters(self):
        """Verify CPR protocols are calibrated to exactly 110 BPM (AHA standard)."""
        adult_cpr = FIRST_AID_CARDS_CATALOG.get("cpr_adult")
        infant_cpr = FIRST_AID_CARDS_CATALOG.get("cpr_infant")
        
        self.assertIsNotNone(adult_cpr)
        self.assertIsNotNone(infant_cpr)
        self.assertEqual(adult_cpr.get("metronome_bpm"), 110)
        self.assertEqual(infant_cpr.get("metronome_bpm"), 110)
        self.assertTrue(adult_cpr.get("call_emergency_first"))

    def test_get_all_first_aid_cards_helper(self):
        """Test get_all_first_aid_cards helper returns structured categories and cards."""
        data = get_all_first_aid_cards()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["total_cards"], 14)
        self.assertIn("categories", data)
        self.assertIn("life_threatening", data["categories"])
        self.assertGreaterEqual(len(data["categories"]["life_threatening"]["cards"]), 2)

    def test_get_first_aid_card_helper(self):
        """Test get_first_aid_card helper for exact and partial match."""
        res_exact = get_first_aid_card("choking_adult")
        self.assertIsNotNone(res_exact)
        self.assertTrue(res_exact["success"])
        self.assertEqual(res_exact["card"]["id"], "choking_adult")

        # Partial search match
        res_partial = get_first_aid_card("anaphylaxis")
        self.assertIsNotNone(res_partial)
        self.assertEqual(res_partial["card"]["id"], "anaphylaxis")

        # Non existent
        res_none = get_first_aid_card("unknown_mythical_card_123")
        self.assertIsNone(res_none)

    def test_search_first_aid_cards_helper(self):
        """Test search_first_aid_cards keyword and synonym ranking."""
        cpr_results = search_first_aid_cards("cpr compressions")
        self.assertGreater(len(cpr_results), 0)
        self.assertEqual(cpr_results[0]["id"], "cpr_adult")

        burn_results = search_first_aid_cards("burns cold water")
        self.assertGreater(len(burn_results), 0)
        self.assertEqual(burn_results[0]["id"], "burns_scalds")

        empty_results = search_first_aid_cards("")
        self.assertEqual(len(empty_results), 0)

    # -------------------------------------------------------------------------
    # REST API Endpoint Tests
    # -------------------------------------------------------------------------

    def test_api_get_all_cards(self):
        """Test GET /api/first-aid-cards."""
        response = self.app.get('/api/first-aid-cards')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["total_cards"], 14)

    def test_api_category_filter(self):
        """Test GET /api/first-aid-cards?category=trauma."""
        response = self.app.get('/api/first-aid-cards?category=trauma')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["category"], "trauma")
        for card in data["cards"]:
            self.assertEqual(card["category"], "trauma")

    def test_api_search_query(self):
        """Test GET /api/first-aid-cards?q=stroke."""
        response = self.app.get('/api/first-aid-cards?q=stroke')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["results"]), 0)
        self.assertEqual(data["results"][0]["id"], "stroke_fast")

    def test_api_card_detail(self):
        """Test GET /api/first-aid-cards/<card_id>."""
        response = self.app.get('/api/first-aid-cards/stroke_fast')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["card"]["id"], "stroke_fast")
        self.assertIn("FAST", data["card"]["title"])
        self.assertGreaterEqual(len(data["card"]["steps"]), 4)

    def test_api_card_detail_not_found(self):
        """Test GET /api/first-aid-cards/invalid_card_404 returns 404."""
        response = self.app.get('/api/first-aid-cards/invalid_card_404')
        self.assertEqual(response.status_code, 404)

    def test_chat_first_aid_intent(self):
        """Test /chat triggers first-aid protocol when user asks for emergency guidance."""
        response = self.app.post(
            '/chat',
            headers={'X-Benchmark-Test': 'true'},
            json={'message': 'How to do CPR instructions for an adult?'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get("is_first_aid_intent"))
        self.assertEqual(data.get("first_aid_card_id"), "cpr_adult")
        self.assertIn("110 BPM", data.get("reply", ""))
        self.assertIn("CRITICAL DO NOTS", data.get("reply", ""))


if __name__ == '__main__':
    unittest.main()
