import unittest
import json
from app import app
from safety.clinical_calculators import (
    calculate_ascvd,
    calculate_chads_vasc,
    calculate_egfr_ckdepi,
    calculate_fib4,
    calculate_curb65,
    calculate_wells_dvt,
    calculate_qsofa,
    calculate_findrisc,
    calculate_phq9,
    calculate_gad7,
    calculate_anthropometrics,
    evaluate_clinical_calculator,
    detect_calculator_in_text,
    get_all_calculators_catalog,
    CALCULATORS_CATALOG
)

class TestClinicalCalculators(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # 1. ASCVD 10-Year Risk Tests
    def test_ascvd_calculation_male_white(self):
        result = calculate_ascvd(
            age=55,
            sex="male",
            race="white_other",
            systolic_bp=140,
            total_cholesterol=210,
            hdl_cholesterol=50,
            is_diabetic=False,
            is_smoker=True,
            on_hypertension_treatment=True
        )
        self.assertIn("score", result)
        self.assertGreater(result["score"], 0)
        self.assertIn("tier", result)
        self.assertIn("statin_recommendation", result)
        self.assertIn("citations", result)

    def test_ascvd_calculation_female_aa(self):
        result = calculate_ascvd(
            age=62,
            sex="female",
            race="african_american",
            systolic_bp=150,
            total_cholesterol=230,
            hdl_cholesterol=45,
            is_diabetic=True,
            is_smoker=False,
            on_hypertension_treatment=True
        )
        self.assertIn("score", result)
        self.assertIn(result["tier"], ["LOW", "BORDERLINE", "INTERMEDIATE", "HIGH"])

    # 2. CHA2DS2-VASc Stroke Risk Tests
    def test_cha2ds2_vasc_scoring(self):
        # Age 76 (+2), Female (+1), Hypertension (+1), Diabetes (+1) = Score 5
        result = calculate_chads_vasc(
            age=76,
            is_female=True,
            congestive_heart_failure=False,
            hypertension=True,
            diabetes=True,
            stroke_or_tia=False,
            vascular_disease=False
        )
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["tier"], "HIGH")
        self.assertIn("anticoagulation_recommendation", result)

    # 3. eGFR CKD-EPI 2021 Race-Free Tests
    def test_egfr_ckd_epi_normal(self):
        result = calculate_egfr_ckdepi(
            serum_creatinine=0.9,
            age=35,
            is_female=False
        )
        self.assertGreater(result["score"], 90)
        self.assertEqual(result["stage"], "G1")

    def test_egfr_ckd_epi_impaired(self):
        result = calculate_egfr_ckdepi(
            serum_creatinine=2.4,
            age=68,
            is_female=True
        )
        self.assertLess(result["score"], 30)
        self.assertEqual(result["stage"], "G4")

    # 4. FIB-4 Liver Fibrosis Tests
    def test_fib4_index(self):
        result = calculate_fib4(
            age=52,
            ast=65,
            alt=42,
            platelets=140
        )
        self.assertIn("score", result)
        self.assertIn("tier", result)
        self.assertGreater(result["score"], 2.0)

    # 5. CURB-65 Pneumonia Severity Tests
    def test_curb65_pneumonia(self):
        result = calculate_curb65(
            confusion=True,
            bun_mg_dl=25,
            respiratory_rate=32,
            systolic_bp=85,
            diastolic_bp=55,
            age=70
        )
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["tier"], "HIGH")

    # 6. Wells Criteria DVT Tests
    def test_wells_dvt(self):
        result = calculate_wells_dvt(
            active_cancer=True,
            paralysis_or_plaster=False,
            bedridden_or_major_surgery=True,
            localized_tenderness=True,
            entire_leg_swollen=True,
            calf_swelling_over_3cm=True,
            pitting_edema=True,
            collateral_superficial_veins=False,
            previous_dvt=False,
            alternative_diagnosis_likely=False
        )
        self.assertGreaterEqual(result["score"], 3)
        self.assertEqual(result["tier"], "HIGH")

    # 7. qSOFA Sepsis Screener Tests
    def test_qsofa_sepsis_positive(self):
        result = calculate_qsofa(
            respiratory_rate=24,
            altered_mentation=True,
            systolic_bp=92
        )
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["tier"], "CRITICAL")

    # 8. FINDRISC Diabetes Risk Tests
    def test_findrisc_diabetes(self):
        result = calculate_findrisc(
            age=58,
            bmi=32,
            waist_cm=105,
            is_female=False,
            physical_activity_daily=False,
            vegetables_daily=False,
            on_bp_medication=True,
            history_high_blood_glucose=True,
            family_history_diabetes="first_degree"
        )
        self.assertGreaterEqual(result["score"], 15)
        self.assertIn(result["tier"], ["HIGH", "VERY_HIGH"])

    # 9. PHQ-9 Depression & Suicide Safety Tests
    def test_phq9_depression_with_suicide_flag(self):
        result = calculate_phq9([2, 3, 2, 2, 2, 2, 2, 1, 2])
        self.assertEqual(result["score"], 18)
        self.assertEqual(result["tier"], "MODERATELY_SEVERE")
        self.assertTrue(result["has_suicide_flag"])
        self.assertIn("CRITICAL SAFETY ALERT", result["safety_warning"])

    def test_phq9_depression_without_suicide_flag(self):
        result = calculate_phq9([1, 1, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["tier"], "MINIMAL")
        self.assertFalse(result["has_suicide_flag"])

    # 10. GAD-7 Anxiety Tests
    def test_gad7_anxiety(self):
        result = calculate_gad7([2, 2, 2, 1, 2, 1, 1])
        self.assertEqual(result["score"], 11)
        self.assertEqual(result["tier"], "MODERATE")

    # 11. Anthropometric & Metabolic Vitals Suite Tests
    def test_anthropometrics_suite(self):
        result = calculate_anthropometrics(
            weight_kg=75,
            height_cm=178,
            age=30,
            is_female=False,
            activity_level="moderate"
        )
        self.assertIn("bmi", result)
        self.assertIn("ideal_body_weight_kg", result)
        self.assertIn("body_surface_area_m2", result)
        self.assertIn("bmr_kcal_day", result)
        self.assertIn("tdee_kcal_day", result)
        self.assertEqual(result["bmi_tier"], "NORMAL")

    # Universal Dispatcher Test
    def test_evaluate_clinical_calculator_dispatch(self):
        res = evaluate_clinical_calculator("chads_vasc", {
            "age": 66, "is_female": False, "congestive_heart_failure": False,
            "hypertension": True, "diabetes": False, "stroke_or_tia": False, "vascular_disease": False
        })
        self.assertTrue(res["success"])
        self.assertEqual(res["calculator_id"], "chads_vasc")
        self.assertEqual(res["data"]["score"], 2) # Age 66 (+1) + HTN (+1) = 2

    # Intent Detection Regex Tests
    def test_detect_calculator_in_text(self):
        self.assertEqual(detect_calculator_in_text("What is my 10-year ASCVD risk score?")["calculator_id"], "ascvd")
        self.assertEqual(detect_calculator_in_text("calculate cha2ds2 score for afib")["calculator_id"], "chads_vasc")
        self.assertEqual(detect_calculator_in_text("calculate egfr for kidney function")["calculator_id"], "egfr")
        self.assertEqual(detect_calculator_in_text("fib-4 index score for liver")["calculator_id"], "fib4")
        self.assertEqual(detect_calculator_in_text("pneumonia curb-65 severity")["calculator_id"], "curb65")
        self.assertEqual(detect_calculator_in_text("wells criteria score for dvt")["calculator_id"], "wells_dvt")
        self.assertEqual(detect_calculator_in_text("qsofa score sepsis")["calculator_id"], "qsofa")
        self.assertEqual(detect_calculator_in_text("diabetes risk findrisc")["calculator_id"], "findrisc")
        self.assertEqual(detect_calculator_in_text("take phq-9 depression test")["calculator_id"], "phq9")
        self.assertEqual(detect_calculator_in_text("gad-7 anxiety test")["calculator_id"], "gad7")
        self.assertEqual(detect_calculator_in_text("calculate my bmi and ideal body weight")["calculator_id"], "anthropometrics")

    # Catalog and REST API Endpoint Tests
    def test_api_get_calculators_catalog(self):
        response = self.app.get('/api/calculators')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["total_calculators"], 11)
        self.assertIn("categories", data)

    def test_api_calculate_endpoint_success(self):
        payload = {
            "calculator_id": "curb65",
            "inputs": {
                "confusion": False,
                "bun_mg_dl": 14,
                "respiratory_rate": 20,
                "systolic_bp": 120,
                "diastolic_bp": 75,
                "age": 45
            }
        }
        response = self.app.post('/api/calculators/calculate',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["score"], 0)
        self.assertEqual(data["data"]["tier"], "LOW")

    def test_api_calculate_endpoint_invalid_id(self):
        payload = {
            "calculator_id": "non_existent_calc",
            "inputs": {}
        }
        response = self.app.post('/api/calculators/calculate',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])

if __name__ == '__main__':
    unittest.main()
