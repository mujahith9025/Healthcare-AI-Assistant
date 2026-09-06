"""
Unit and integration tests for Medical Nutrition Therapy (MNT & Diet-Disease Prescriptor).
Covers 12+ condition protocols, multi-condition conflict resolution, food-drug interaction checks,
dietary preferences, and Flask API endpoints.
"""

import unittest
import json
from app import app
from safety.nutrition_therapy import (
    NUTRITION_PROTOCOLS,
    get_all_nutrition_protocols,
    reconcile_dietary_conflicts,
    check_food_drug_interactions,
    evaluate_nutrition_therapy
)


class TestNutritionTherapy(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        self.app = app.test_client()

    # -------------------------------------------------------------------------
    # 1. Protocol Catalog & Database Completeness
    # -------------------------------------------------------------------------
    def test_protocol_catalog_completeness(self):
        protocols = get_all_nutrition_protocols()
        self.assertTrue(protocols["success"])
        self.assertGreaterEqual(len(protocols["protocols"]), 12)
        
        required_keys = ["hypertension", "diabetes", "ckd", "gout", "gerd", "ibs", 
                         "nafld", "hyperlipidemia", "celiac", "anemia", "osteoporosis", "migraine"]
        for rk in required_keys:
            self.assertIn(rk, protocols["protocols"])
            p = protocols["protocols"][rk]
            self.assertIn("name", p)
            self.assertIn("principles", p)
            self.assertIn("macro_targets", p)
            self.assertIn("prioritize_foods", p)
            self.assertIn("avoid_foods", p)
            self.assertIn("sample_meal_plan", p)
            self.assertIn("guideline_sources", p)

    # -------------------------------------------------------------------------
    # 2. Single Condition Nutrition Evaluation
    # -------------------------------------------------------------------------
    def test_hypertension_dash_evaluation(self):
        res = evaluate_nutrition_therapy(conditions=["hypertension"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["evaluated_protocols"]), 1)
        self.assertEqual(res["evaluated_protocols"][0]["id"], "hypertension")
        self.assertFalse(res["has_conflicts"])
        # Check DASH targets
        self.assertIn("sodium", res["macro_targets"])
        # Check foods
        self.assertTrue(any("Leafy green" in f or "Berries" in f for f in res["prioritize_foods"]))
        self.assertTrue(any("Cured" in f or "sodium" in f.lower() for f in res["avoid_foods"]))

    def test_diabetes_low_gi_evaluation(self):
        res = evaluate_nutrition_therapy(conditions=["diabetes"])
        self.assertTrue(res["success"])
        self.assertEqual(res["evaluated_protocols"][0]["id"], "diabetes")
        self.assertIn("carbohydrate", res["macro_targets"])
        self.assertTrue(any("Cruciferous" in f or "Legumes" in f or "Berries" in f for f in res["prioritize_foods"]))

    def test_ckd_renal_evaluation(self):
        res = evaluate_nutrition_therapy(conditions=["ckd"])
        self.assertTrue(res["success"])
        self.assertIn("potassium", res["macro_targets"])
        self.assertIn("2,000", res["macro_targets"]["potassium"])
        self.assertTrue(any("Leached" in f or "Low-potassium" in f or "potassium" in f.lower() for f in res["prioritize_foods"]))

    def test_gout_purine_evaluation(self):
        res = evaluate_nutrition_therapy(conditions=["gout"])
        self.assertTrue(res["success"])
        self.assertTrue(any("cherries" in f.lower() or "tart cherry" in f.lower() for f in res["prioritize_foods"]))
        self.assertTrue(any("organ meats" in f.lower() or "purine" in f.lower() or "beer" in f.lower() for f in res["avoid_foods"]))

    def test_celiac_gluten_free_evaluation(self):
        res = evaluate_nutrition_therapy(conditions=["celiac"])
        self.assertTrue(res["success"])
        self.assertTrue(any("gluten-free" in f.lower() or "quinoa" in f.lower() for f in res["prioritize_foods"]))
        self.assertTrue(any("wheat" in f.lower() or "barley" in f.lower() or "rye" in f.lower() for f in res["avoid_foods"]))

    # -------------------------------------------------------------------------
    # 3. Multi-Condition Conflict Resolution Engine
    # -------------------------------------------------------------------------
    def test_dash_vs_ckd_potassium_conflict_resolution(self):
        """DASH normally encourages 4,700mg potassium, but CKD requires strict <2,000mg."""
        conflicts = reconcile_dietary_conflicts(["hypertension", "ckd"])
        self.assertGreaterEqual(len(conflicts), 1)
        k_conflict = next((c for c in conflicts if "potassium" in c["conflict"].lower()), None)
        self.assertIsNotNone(k_conflict)
        self.assertEqual(k_conflict["primary_priority"], "Renal Organ Protection (CKD)")
        self.assertIn("2,000 mg/day", k_conflict["resolution"])

        # Integrated evaluation check
        eval_res = evaluate_nutrition_therapy(conditions=["hypertension", "ckd"])
        self.assertTrue(eval_res["has_conflicts"])
        self.assertIn("2,000 mg/day", eval_res["macro_targets"]["potassium"])

    def test_gout_vs_diabetes_protein_conflict_resolution(self):
        """Diabetes emphasizes lean meats & legumes, Gout restricts red meat, seafood, and high-purine lentils."""
        conflicts = reconcile_dietary_conflicts(["gout", "diabetes"])
        self.assertGreaterEqual(len(conflicts), 1)
        g_conflict = next((c for c in conflicts if "purine" in c["conflict"].lower() or "protein" in c["conflict"].lower()), None)
        self.assertIsNotNone(g_conflict)
        self.assertIn("low-purine plant proteins", g_conflict["resolution"].lower())

    def test_gerd_vs_nafld_fat_conflict_resolution(self):
        """GERD requires low fat to prevent LES relaxation, NAFLD emphasizes monounsaturated/omega-3 fats."""
        conflicts = reconcile_dietary_conflicts(["gerd", "nafld"])
        self.assertGreaterEqual(len(conflicts), 1)
        f_conflict = next((c for c in conflicts if "fat" in c["conflict"].lower()), None)
        self.assertIsNotNone(f_conflict)
        self.assertIn("unsaturated fats", f_conflict["resolution"].lower())

    # -------------------------------------------------------------------------
    # 4. Food-Drug Interaction Cross-Checks
    # -------------------------------------------------------------------------
    def test_warfarin_vitamin_k_interaction(self):
        warnings = check_food_drug_interactions(["Warfarin"])
        self.assertGreaterEqual(len(warnings), 1)
        w_warn = next((w for w in warnings if "vitamin k" in w["food_nutrient"].lower()), None)
        self.assertIsNotNone(w_warn)
        self.assertEqual(w_warn["severity"], "HIGH")
        self.assertIn("consistent daily intake", w_warn["action"].lower())

    def test_statin_grapefruit_interaction(self):
        warnings = check_food_drug_interactions(["Atorvastatin"])
        self.assertGreaterEqual(len(warnings), 1)
        s_warn = next((w for w in warnings if "grapefruit" in w["food_nutrient"].lower()), None)
        self.assertIsNotNone(s_warn)
        self.assertEqual(s_warn["severity"], "HIGH")
        self.assertIn("cyp3a4", s_warn["warning"].lower())

    def test_levothyroxine_calcium_iron_timing_interaction(self):
        warnings = check_food_drug_interactions(["Levothyroxine"])
        self.assertGreaterEqual(len(warnings), 1)
        t_warn = next((w for w in warnings if "calcium" in w["food_nutrient"].lower()), None)
        self.assertIsNotNone(t_warn)
        self.assertIn("4 hours", t_warn["action"].lower())

    def test_maoi_tyramine_interaction(self):
        warnings = check_food_drug_interactions(["Phenelzine"])
        self.assertGreaterEqual(len(warnings), 1)
        m_warn = next((w for w in warnings if "tyramine" in w["food_nutrient"].lower()), None)
        self.assertIsNotNone(m_warn)
        self.assertEqual(m_warn["severity"], "CRITICAL")
        self.assertIn("hypertensive crisis", m_warn["warning"].lower())

    # -------------------------------------------------------------------------
    # 5. Dietary Preferences Filtering
    # -------------------------------------------------------------------------
    def test_vegetarian_preference_filtering(self):
        res = evaluate_nutrition_therapy(
            conditions=["hypertension"],
            dietary_preferences=["vegetarian"]
        )
        self.assertTrue(res["success"])
        # Should not include salmon or meat in prioritized list
        for food in res["prioritize_foods"]:
            self.assertNotIn("salmon", food.lower())
            self.assertNotIn("chicken", food.lower())

    # -------------------------------------------------------------------------
    # 6. Flask API Endpoints
    # -------------------------------------------------------------------------
    def test_api_get_nutrition_protocols(self):
        resp = self.app.get('/api/nutrition-protocols')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertIn("protocols", data)
        self.assertIn("conditions", data)
        self.assertIn("dietary_preferences", data)

    def test_api_post_nutrition_recommendation(self):
        payload = {
            "conditions": ["hypertension", "diabetes"],
            "dietary_preferences": ["low_sodium"],
            "active_medications": ["Warfarin", "Lisinopril"]
        }
        resp = self.app.post('/api/nutrition-recommendation',
                             data=json.dumps(payload),
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["evaluated_protocols"]), 2)
        self.assertTrue(data["has_drug_interactions"])
        self.assertGreaterEqual(len(data["food_drug_interactions"]), 1)

    def test_chat_nutrition_intent(self):
        payload = {"message": "What is the medical diet plan for hypertension and diabetes?"}
        resp = self.app.post('/chat',
                             data=json.dumps(payload),
                             content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("reply", data)
        self.assertTrue(data.get("is_nutrition_intent") or "DASH" in data["reply"] or "Medical Nutrition" in data["reply"])


if __name__ == '__main__':
    unittest.main()
