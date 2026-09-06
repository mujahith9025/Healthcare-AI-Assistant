"""
Unit Tests for Multimodal Medical Document & Vision OCR Module.
Validates magic byte signatures, lab synonym fuzzy matching, offline fallback heuristics,
and the /api/vision/scan endpoint.
"""

import unittest
import io
import json
import base64
from app import app
from safety.vision_ocr import (
    validate_image_bytes,
    match_lab_test_key,
    generate_heuristic_ocr_fallback,
    process_medical_document_image
)

class TestVisionOCR(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Minimal valid image byte headers
        self.valid_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        self.valid_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00' + b'\x00' * 50
        self.valid_webp = b'RIFF\x24\x00\x00\x00WEBPVP8 \x18\x00\x00\x00' + b'\x00' * 30
        self.invalid_text = b'This is a fake text file and not a valid medical image.'

    def test_magic_byte_validation_valid_types(self):
        """Verify that legitimate JPEG, PNG, and WEBP headers are validated."""
        valid, mime, err = validate_image_bytes(self.valid_png)
        self.assertTrue(valid)
        self.assertEqual(mime, 'image/png')
        self.assertEqual(err, "")

        valid, mime, err = validate_image_bytes(self.valid_jpeg)
        self.assertTrue(valid)
        self.assertEqual(mime, 'image/jpeg')
        self.assertEqual(err, "")

        valid, mime, err = validate_image_bytes(self.valid_webp)
        self.assertTrue(valid)
        self.assertEqual(mime, 'image/webp')
        self.assertEqual(err, "")

    def test_magic_byte_validation_invalid_types(self):
        """Verify that plain text, corrupted data, and empty bytes are rejected."""
        valid, mime, err = validate_image_bytes(self.invalid_text)
        self.assertFalse(valid)
        self.assertEqual(mime, '')
        self.assertTrue(len(err) > 0)

        valid, mime, err = validate_image_bytes(b'')
        self.assertFalse(valid)

        valid, mime, err = validate_image_bytes(b'MZ\x90\x00\x03\x00\x00\x00') # Windows PE
        self.assertFalse(valid)

    def test_match_lab_test_key_synonyms(self):
        """Verify fuzzy synonym resolution against standard 26-test catalog."""
        self.assertEqual(match_lab_test_key("Fasting Blood Sugar (FBS)"), "fasting_glucose")
        self.assertEqual(match_lab_test_key("Hemoglobin A1c (Glycated)"), "hba1c")
        self.assertEqual(match_lab_test_key("Total Serum Cholesterol"), "total_cholesterol")
        self.assertEqual(match_lab_test_key("Blood Pressure (BP Systolic/Diastolic)"), "blood_pressure")
        self.assertEqual(match_lab_test_key("Serum Creatinine"), "serum_creatinine")
        self.assertEqual(match_lab_test_key("eGFR Kidney Clearance"), "egfr")
        self.assertEqual(match_lab_test_key("Thyroid Stimulating Hormone (TSH)"), "tsh")
        self.assertEqual(match_lab_test_key("Serum Potassium K+"), "serum_potassium")
        self.assertIsNone(match_lab_test_key("Unrelated Random Label XYZ"))

    def test_heuristic_ocr_fallback_lab_report(self):
        """Verify offline heuristic fallback generates clinical 3-tier structure for lab reports."""
        res = generate_heuristic_ocr_fallback("lab_report")
        self.assertTrue(res["success"])
        self.assertEqual(res["doc_type"], "lab_report")
        self.assertTrue(len(res["extracted_labs"]) > 0)
        self.assertIn("plain_language_summary", res)
        self.assertIn("key_takeaways", res)
        self.assertIn("doctor_questions", res)

    def test_heuristic_ocr_fallback_prescription(self):
        """Verify offline heuristic fallback generates extracted medications and polypharmacy check."""
        res = generate_heuristic_ocr_fallback("prescription")
        self.assertTrue(res["success"])
        self.assertEqual(res["doc_type"], "prescription")
        self.assertTrue(len(res["extracted_medications"]) > 0)
        self.assertIn("polypharmacy_interaction_check", res)

    def test_heuristic_ocr_fallback_radiology_report(self):
        """Verify offline heuristic fallback generates 3-tier structure for diagnostic radiology (Chest X-Ray)."""
        res = generate_heuristic_ocr_fallback("radiology")
        self.assertTrue(res["success"])
        self.assertEqual(res["doc_type"], "radiology_report")
        self.assertEqual(res["modality"], "Chest X-Ray")
        self.assertEqual(res["body_map_region"], "chest")
        self.assertIn("radiologist_impression", res)
        self.assertTrue(len(res["findings_breakdown"]) >= 4)
        self.assertTrue(len(res["jargon_glossary"]) >= 4)
        self.assertIn("plain_language_summary", res)
        self.assertTrue(len(res["key_takeaways"]) > 0)
        self.assertTrue(len(res["doctor_questions"]) > 0)

        # Check finding structure
        finding = res["findings_breakdown"][0]
        self.assertIn("organ_structure", finding)
        self.assertIn("radiologist_finding", finding)
        self.assertIn("plain_english_meaning", finding)
        self.assertIn("status_tier", finding)

        # Check jargon glossary structure
        glossary_item = res["jargon_glossary"][0]
        self.assertIn("term", glossary_item)
        self.assertIn("definition", glossary_item)

    def test_heuristic_ocr_fallback_radiology_mri_spine(self):
        """Verify heuristic fallback handles Lumbar Spine MRI modality."""
        res = generate_heuristic_ocr_fallback("mri")
        self.assertTrue(res["success"])
        self.assertEqual(res["doc_type"], "radiology_report")
        self.assertIn(res["body_map_region"], ["chest", "spine"])
        self.assertIn("radiologist_impression", res)
        self.assertTrue(len(res["findings_breakdown"]) > 0)

    def test_api_vision_scan_no_payload_400(self):
        """Verify /api/vision/scan returns 400 when no image is provided."""
        res = self.app.post('/api/vision/scan', json={})
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data["success"])

    def test_api_vision_scan_corrupted_image_400(self):
        """Verify /api/vision/scan rejects fake or non-image payloads."""
        res = self.app.post('/api/vision/scan', data={
            'file': (io.BytesIO(b'NOT AN IMAGE'), 'test.txt')
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data["success"])
        self.assertIn("corrupted", data["error"].lower())

    def test_api_vision_scan_multipart_png_success(self):
        """Verify /api/vision/scan handles multipart image upload and returns 3-tier ELI5 results."""
        res = self.app.post('/api/vision/scan', data={
            'file': (io.BytesIO(self.valid_png), 'lab_slip.png'),
            'doc_hint': 'lab_report'
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn(data["doc_type"], ["lab_report", "prescription", "vital_signs", "radiology_report", "general_medical_document"])
        self.assertIn("plain_language_summary", data)

    def test_api_vision_scan_radiology_multipart_success(self):
        """Verify /api/vision/scan handles radiology mode and returns findings breakdown and jargon glossary."""
        res = self.app.post('/api/vision/scan', data={
            'file': (io.BytesIO(self.valid_png), 'chest_xray.png'),
            'doc_hint': 'radiology'
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["doc_type"], "radiology_report")
        self.assertIn("radiologist_impression", data)
        self.assertIn("findings_breakdown", data)
        self.assertIn("jargon_glossary", data)
        self.assertEqual(data["body_map_region"], "chest")

    def test_api_vision_scan_base64_json_success(self):
        """Verify /api/vision/scan handles Base64 JSON payloads."""
        b64_str = f"data:image/png;base64,{base64.b64encode(self.valid_png).decode('utf-8')}"
        res = self.app.post('/api/vision/scan', json={
            'image_base64': b64_str,
            'doc_hint': 'radiology'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["doc_type"], "radiology_report")
        self.assertIn("plain_language_summary", data)
        self.assertTrue(len(data.get("findings_breakdown", [])) > 0)

if __name__ == '__main__':
    unittest.main()

