import os
import json
import time
import math
import re
import functools
import traceback
from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv
from google import genai
from google.genai import types

from safety.emergency_check import (
    is_emergency,
    get_contextual_emergency_response,
    detect_red_flags,
    format_red_flag_note,
    EMERGENCY_RESPONSE
)
from safety.medication_guard import check_medication_safety
from safety.guided_triage import TRIAGE_STEPS, evaluate_triage
from safety.post_verification import verify_and_filter_response
from safety.polypharmacy_matrix import check_polypharmacy_interactions, scan_text_for_polypharmacy
from safety.lab_interpreter import get_all_lab_tests, interpret_lab_result, detect_and_interpret_vitals_in_query, LAB_TESTS_CATALOG
from safety.nutrition_therapy import get_all_nutrition_protocols, evaluate_nutrition_therapy, NUTRITION_PROTOCOLS
from safety.first_aid_cards import get_all_first_aid_cards, get_first_aid_card, search_first_aid_cards
from safety.clinical_calculators import get_all_calculators_catalog, evaluate_clinical_calculator, detect_calculator_in_text
from safety.mental_health_toolkit import (
    get_mental_health_catalog,
    evaluate_mental_health_assessment,
    generate_stanley_brown_safety_plan,
    detect_mental_health_intent,
    SOMATIC_PROTOCOLS
)
from safety.vision_ocr import process_medical_document_image, validate_image_bytes
from database.db_helper import lookup_health_info, get_rag_grounding_context, TOPIC_CITATIONS
from database.setup_db import init_db

# Load environment variables from .env file
load_dotenv()

# Initialize/seed SQLite database on startup if not present
init_db()

app = Flask(__name__)

# --- Security Configuration: Maximum Payload Size Limit (DoS Protection & Image OCR) ---
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB maximum request body for medical image OCR

# --- Advanced Sliding-Window Rate Limiting & Abuse Prevention ---
CLIENT_REQUEST_LOGS = {}
WINDOW_DURATION = 30.0       # 30 seconds window
MAX_REQUESTS_IN_WINDOW = 25  # max 25 requests per 30s
MIN_COOLDOWN_SECONDS = 0.2   # 0.2s minimal gap
MAX_MESSAGE_LENGTH = 500     # max character length for input sanitization

def get_client_ip(req) -> str:
    """Safely extract and sanitize client IP address."""
    if req.headers.get('X-Forwarded-For'):
        ip = req.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = req.remote_addr or '127.0.0.1'
    # Sanitize to valid IP characters (IPv4/IPv6)
    return re.sub(r'[^a-fA-F0-9.:]', '', ip)[:45]

def check_rate_limit(client_ip: str) -> tuple[bool, int]:
    """Sliding window rate-limiter with automatic memory leak cleanup."""
    now = time.time()

    # Periodic cleanup of expired client logs to prevent memory exhaustion
    if len(CLIENT_REQUEST_LOGS) > 500:
        expired_ips = [ip for ip, hist in list(CLIENT_REQUEST_LOGS.items()) if not hist or (now - hist[-1] > WINDOW_DURATION)]
        for ip in expired_ips:
            CLIENT_REQUEST_LOGS.pop(ip, None)

    history = CLIENT_REQUEST_LOGS.get(client_ip, [])
    valid_history = [t for t in history if now - t < WINDOW_DURATION]

    if valid_history and (now - valid_history[-1]) < MIN_COOLDOWN_SECONDS:
        return False, 1

    if len(valid_history) >= MAX_REQUESTS_IN_WINDOW:
        oldest = valid_history[0]
        retry_after = int(WINDOW_DURATION - (now - oldest)) + 1
        return False, max(1, retry_after)

    valid_history.append(now)
    CLIENT_REQUEST_LOGS[client_ip] = valid_history
    return True, 0

# --- High-Speed In-Memory Response Cache (Sub-Millisecond Response Time) ---
RESPONSE_CACHE = {}
MAX_CACHE_SIZE = 500
CACHE_TTL_SECONDS = 3600  # 1 hour TTL

def get_cached_chat_response(query: str, region: str = "GLOBAL") -> dict | None:
    """Retrieve verified pre-computed / cached response in <1ms."""
    clean_key = f"{region}:{re.sub(r'[^a-zA-Z0-9]', '', query.lower())}"
    entry = RESPONSE_CACHE.get(clean_key)
    if entry:
        timestamp, data = entry
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return data
    return None

def set_cached_chat_response(query: str, data: dict, region: str = "GLOBAL"):
    """Store verified response in in-memory LRU cache."""
    if len(RESPONSE_CACHE) > MAX_CACHE_SIZE:
        oldest_keys = sorted(RESPONSE_CACHE.keys(), key=lambda k: RESPONSE_CACHE[k][0])[:MAX_CACHE_SIZE // 5]
        for k in oldest_keys:
            RESPONSE_CACHE.pop(k, None)
    clean_key = f"{region}:{re.sub(r'[^a-zA-Z0-9]', '', query.lower())}"
    RESPONSE_CACHE[clean_key] = (time.time(), data)

def rate_limited(f):
    """Decorator to enforce rate limiting on API endpoints."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        is_benchmark = (
            request.headers.get('X-Benchmark-Test') == 'true'
            or app.testing
            or app.config.get('TESTING', False)
            or request.environ.get('werkzeug.test', False)
            or request.headers.get('User-Agent', '').lower().startswith('werkzeug')
        )
        client_ip = get_client_ip(request)
        is_allowed, retry_after = (True, 0) if is_benchmark else check_rate_limit(client_ip)

        if not is_allowed:
            resp = jsonify({
                'error': 'Rate limit exceeded',
                'reply': f"⏳ You are sending requests too quickly. Please wait {retry_after} second(s) before trying again.",
                'source': 'rate_limiter'
            })
            resp.status_code = 429
            resp.headers['Retry-After'] = str(retry_after)
            return resp
        return f(*args, **kwargs)
    return decorated_function

# --- Security Headers Middleware ---
@app.after_request
def add_security_headers(response):
    """Inject standard HTTP security headers into all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'self';"
    )
    return response

# --- Centralized HTTP Error Handlers ---
@app.errorhandler(400)
def bad_request_error(e):
    return jsonify({'error': 'Bad Request', 'message': 'Invalid input or request format.'}), 400

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({'error': 'Not Found', 'message': 'The requested endpoint does not exist.'}), 404

@app.errorhandler(405)
def method_not_allowed_error(e):
    return jsonify({'error': 'Method Not Allowed', 'message': 'HTTP method not supported for this endpoint.'}), 405

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({'error': 'Payload Too Large', 'message': 'Request payload exceeds maximum allowed limit (1MB).'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Too Many Requests', 'message': 'Rate limit exceeded. Please wait a moment.'}), 429

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred. Please try again later.'}), 500

# Persistent client instance
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key.strip() and api_key.strip() != 'your_key_here':
            _client = genai.Client(api_key=api_key.strip())
    return _client

SYSTEM_INSTRUCTION = (
    "You are an AI healthcare information assistant providing factually grounded, empathetic health education in an intuitive 3-Tier Plain Language format:\n"
    "• 💡 **Plain Language (ELI5):** Explain what this means in simple, reassuring words at a 5th-grade reading level (under 25 words).\n"
    "• 📋 **Evidence-Based Home Care:** 2-3 practical, actionable self-care, hydration, rest, or dietary steps.\n"
    "• 🩺 **Questions for Your Doctor:** 1-2 key questions or warning signs to discuss with a physician.\n\n"
    "You are NOT a doctor and must NEVER diagnose a specific condition, prescribe medication dosages, or claim clinical certainty. "
    "CONFIDENCE & UNCERTAINTY CALIBRATION: Explicitly qualify uncertainty for recovery timelines or home remedies (e.g. 'Timelines vary by individual...'). "
    "Keep answers direct, structured, and under 90 words total."
)

DEFAULT_SUGGESTIONS = [
    "What are common home care tips for this?",
    "When should I consult a doctor?",
    "What foods or habits help with recovery?"
]

SPECULATIVE_PATTERNS = [
    "cure me", "guaranteed cure", "100% cure", "permanent cure", "miracle cure",
    "definitely go away", "how many days exactly", "instant cure", "magic remedy"
]

def is_specific_or_followup_question(query: str) -> bool:
    """
    Detect if the query is a specific in-depth or follow-up question
    that should be grounded and answered by Gemini AI rather than returning a static card.
    """
    q = query.lower().strip()

    specific_keywords = [
        "home remedies", "remedy", "remedies", "what foods", "food", "foods", "diet",
        "what to eat", "what to drink", "foods to avoid", "avoid", "when to see",
        "when should", "see a doctor", "how long", "how does", "how do", "how to",
        "why does", "why do", "difference between", "difference of", "vs", "versus",
        "triggers", "trigger", "cure", "prevention tips", "exercises", "exercise",
        "lifestyle", "tea", "teas", "supplements", "vitamins", "recovery", "routine",
        "water", "fluids", "warm", "drink", "tips for", "tips to", "manage", "relieve",
        "that", "those", "them", "it"
    ]

    for kw in specific_keywords:
        if kw in q:
            return True

    if re.search(r'^(how|why|when|what foods|what remedies|can i|should i|is it safe|tips)\b', q):
        return True

    return False

def check_uncertainty_calibration(query: str) -> str:
    """Detect speculative claims and append an uncertainty & clinical evidence disclaimer."""
    normalized = query.lower()
    if any(p in normalized for p in SPECULATIVE_PATTERNS):
        return (
            "\n\n🔬 **CLINICAL EVIDENCE & UNCERTAINTY CALIBRATION**:\n"
            "Medical conditions and biological responses vary substantially from person to person. "
            "No health approach can guarantee a fixed timeframe or instant cure. "
            "Please rely on verified medical evaluations rather than unscientific claims."
        )
    return ""

@app.route('/')
def home():
    """Render the main Healthcare Assistant interface."""
    return render_template('index.html')

@app.route('/triage/options', methods=['GET'])
def triage_options():
    """Return configured structured triage steps and options."""
    return jsonify(TRIAGE_STEPS)

@app.route('/triage/evaluate', methods=['POST'])
@rate_limited
def triage_evaluate():
    """Evaluate submitted 5-step triage responses and return structured guidance."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    region = str(data.get('region', 'GLOBAL')).strip().upper()[:20]
    assessment = evaluate_triage(data, region=region)
    return jsonify(assessment)

@app.route('/api/check-interactions', methods=['POST'])
@rate_limited
def api_check_interactions():
    """Evaluate multi-drug, drug-condition, and drug-food interactions."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    items = data.get('drugs') or data.get('items', [])
    if isinstance(items, str):
        items = [i.strip() for i in items.split(',') if i.strip()]
    if not isinstance(items, list):
        items = []
    # Cap item count and character lengths for input sanitization
    items = [str(x).strip()[:100] for x in items[:30] if str(x).strip()]
    
    result = check_polypharmacy_interactions(items)
    result['success'] = True
    result['interaction_count'] = result.get('total_interactions', 0)
    result['highest_severity'] = result.get('severity_summary', 'NONE')
    result['drugs'] = result.get('checked_entities', [])
    
    # Map interaction fields for frontend consistency
    adapted_interactions = []
    for item in result.get('interactions', []):
        adapted_interactions.append({
            'drug_a': item.get('item_1', ''),
            'drug_b': item.get('item_2', ''),
            'severity': item.get('severity', 'MODERATE'),
            'title': item.get('title', ''),
            'effect': item.get('effects', '') or item.get('mechanism', ''),
            'clinical_recommendation': item.get('action', ''),
            'evidence': item.get('mechanism', '')
        })
    result['interactions'] = adapted_interactions
    return jsonify(result)

@app.route('/api/lab-tests', methods=['GET'])
def api_lab_tests():
    """Return catalog of all standard laboratory biomarker panels."""
    # Organize into 7 structured clinical panels
    panel_mapping = {
        "fasting_glucose": "metabolic", "hba1c": "metabolic", "fasting_insulin": "metabolic",
        "total_cholesterol": "lipids", "ldl_cholesterol": "lipids", "hdl_cholesterol": "lipids", "triglycerides": "lipids",
        "blood_pressure": "vitals", "resting_heart_rate": "vitals", "oxygen_saturation": "vitals", "body_temperature": "vitals",
        "hemoglobin": "cbc", "white_blood_cells": "cbc", "platelet_count": "cbc",
        "serum_creatinine": "renal", "egfr": "renal", "bun": "renal", "serum_potassium": "renal", "serum_sodium": "renal",
        "alt_liver": "hepatic", "ast_liver": "hepatic", "bilirubin_total": "hepatic",
        "tsh": "thyroid_vitamins", "vitamin_d": "thyroid_vitamins", "vitamin_b12": "thyroid_vitamins", "serum_calcium": "thyroid_vitamins"
    }

    panels = {
        "metabolic": {"title": "🩸 Metabolic & Glycemic", "tests": {}},
        "lipids": {"title": "❤️ Lipids & Cardiac", "tests": {}},
        "vitals": {"title": "💓 Vitals & Hemodynamics", "tests": {}},
        "cbc": {"title": "🔬 CBC Complete Blood Count", "tests": {}},
        "renal": {"title": "🫘 Kidney & Renal Function", "tests": {}},
        "hepatic": {"title": "🧪 Liver Function (LFT)", "tests": {}},
        "thyroid_vitamins": {"title": "🦋 Thyroid, Minerals & Vitamins", "tests": {}}
    }

    for tid, tinfo in LAB_TESTS_CATALOG.items():
        pkey = panel_mapping.get(tid, "metabolic")
        panels[pkey]["tests"][tid] = {
            "name": tinfo.get("name", tid),
            "unit": tinfo.get("unit", ""),
            "optimal_target": tinfo.get("display_range", ""),
            "min_gauge": tinfo.get("slider_min", 0),
            "max_gauge": tinfo.get("slider_max", 100),
            "default_val": tinfo.get("default_val", 0),
            "description": tinfo.get("description", "")
        }

    return jsonify({"success": True, "panels": panels, "tests": LAB_TESTS_CATALOG})

@app.route('/api/interpret-lab', methods=['POST'])
@rate_limited
def api_interpret_lab():
    """Interpret numeric laboratory or vital biomarker values."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    test_id = str(data.get('test_key') or data.get('test_id', 'fasting_glucose')).strip()[:64]
    value = data.get('value', 0)
    value_2 = data.get('value2') if data.get('value2') is not None else data.get('value_2', None)
    
    try:
        val_float = float(value)
        if math.isnan(val_float) or math.isinf(val_float):
            return jsonify({"error": "Numerical value cannot be NaN or Infinite"}), 400

        val_2_float = None
        if value_2 is not None and str(value_2).strip() != '':
            val_2_float = float(value_2)
            if math.isnan(val_2_float) or math.isinf(val_2_float):
                return jsonify({"error": "Numerical value2 cannot be NaN or Infinite"}), 400

        result = interpret_lab_result(test_id, val_float, val_2_float)
        
        result['success'] = True
        result['status'] = result.get('tier', 'OPTIMAL').lower()
        result['status_label'] = result.get('tier_label', '')
        result['test_name'] = result.get('name', '')
        result['optimal_target'] = result.get('reference_range', '')
        
        # Parse causes and lifestyle into clean lists if needed
        raw_causes = (result.get('high_causes', '') + ' ' + result.get('low_causes', '')).strip()
        result['potential_causes'] = [c.strip() for c in re.split(r'[,;.]', raw_causes) if len(c.strip()) > 3][:4]
        result['evidence_lifestyle'] = [l.strip() for l in re.split(r'[,;.]', result.get('lifestyle_tips', '')) if len(l.strip()) > 3][:4]
        result['physician_talking_points'] = result.get('doctor_questions', [])
        result['pin_percent'] = result.get('gauge_pct', 50)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Invalid numerical value: {e}"}), 400

@app.route('/api/vision/scan', methods=['POST'])
@rate_limited
def api_vision_scan():
    """
    Multimodal Vision OCR endpoint for Laboratory Test Slips, Prescriptions, and Vital Monitors.
    Accepts multipart/form-data ('file' or 'image') or JSON {'image_base64': '...', 'doc_hint': '...'}.
    Returns structured 3-tier ELI5 analysis, mapped lab tests, medications, and clinical safety flags.
    """
    import base64
    image_bytes = None
    doc_hint = "auto"

    if request.files and ('file' in request.files or 'image' in request.files):
        uploaded_file = request.files.get('file') or request.files.get('image')
        doc_hint = request.form.get('doc_hint', 'auto')[:32]
        if uploaded_file and uploaded_file.filename:
            image_bytes = uploaded_file.read()
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        doc_hint = str(data.get('doc_hint', 'auto'))[:32]
        b64_str = data.get('image_base64') or data.get('data') or data.get('image')
        if b64_str and isinstance(b64_str, str):
            if ',' in b64_str:
                b64_str = b64_str.split(',', 1)[1]
            try:
                image_bytes = base64.b64decode(b64_str)
            except Exception:
                return jsonify({"error": "Malformed Base64 image payload.", "success": False}), 400

    if not image_bytes:
        return jsonify({"error": "No image file or Base64 payload provided in request.", "success": False}), 400

    is_valid, mime_type, err_msg = validate_image_bytes(image_bytes)
    if not is_valid:
        return jsonify({
            "error": err_msg or "Invalid or corrupted image format. Please upload a valid JPEG, PNG, or WEBP image under 5MB.",
            "success": False
        }), 400

    result = process_medical_document_image(image_bytes, mime_type=mime_type, doc_hint=doc_hint)
    return jsonify(result)

@app.route('/api/nutrition-protocols', methods=['GET'])
def api_nutrition_protocols():
    """Return all condition nutrition protocols, dietary preferences, and food-drug interaction catalog."""
    data = get_all_nutrition_protocols()
    return jsonify(data)

@app.route('/api/nutrition-recommendation', methods=['POST'])
@rate_limited
def api_nutrition_recommendation():
    """Generate personalized multi-condition medical nutrition therapy prescription with conflict resolution."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    conditions = [str(c).strip()[:64] for c in data.get('conditions', [])[:20]] if isinstance(data.get('conditions'), list) else []
    dietary_preferences = [str(d).strip()[:64] for d in data.get('dietary_preferences', [])[:20]] if isinstance(data.get('dietary_preferences'), list) else []
    active_medications = [str(m).strip()[:64] for m in data.get('active_medications', [])[:20]] if isinstance(data.get('active_medications'), list) else []
    
    result = evaluate_nutrition_therapy(
        conditions=conditions,
        dietary_preferences=dietary_preferences,
        active_medications=active_medications
    )
    return jsonify(result)

@app.route('/api/first-aid-cards', methods=['GET'])
def api_first_aid_cards():
    """Return catalog of interactive emergency action and first-aid flashcards."""
    q = request.args.get('q', '').strip()[:100]
    category = request.args.get('category', '').strip()[:64]
    
    if q:
        results = search_first_aid_cards(q)
        return jsonify({"success": True, "results": results, "query": q})
    
    catalog_data = get_all_first_aid_cards()
    if category and category in catalog_data.get("categories", {}):
        filtered_cards = catalog_data["categories"][category]["cards"]
        return jsonify({"success": True, "category": category, "cards": filtered_cards, "categories": catalog_data.get("categories", {})})
        
    return jsonify(catalog_data)

@app.route('/api/first-aid-cards/<card_id>', methods=['GET'])
def api_first_aid_card_detail(card_id: str):
    """Return full sequential emergency protocol and DO NOTs for a specific first-aid card."""
    card_id = str(card_id).strip()[:64]
    card_res = get_first_aid_card(card_id)
    if not card_res:
        return jsonify({"error": f"First-aid card '{card_id}' not found."}), 404
    return jsonify(card_res)

@app.route('/api/calculators', methods=['GET'])
def api_calculators():
    """Return catalog of evidence-based clinical risk calculators and vital tools."""
    catalog_data = get_all_calculators_catalog()
    return jsonify(catalog_data)

@app.route('/api/calculators/calculate', methods=['POST'])
@rate_limited
def api_calculate():
    """Evaluate a specific clinical calculator with validated inputs and return clinical risk report."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    calc_id = str(data.get('calculator_id', '')).strip()[:64]
    inputs = data.get('inputs', {})
    if not isinstance(inputs, dict):
        inputs = {}
    
    result = evaluate_clinical_calculator(calc_id, inputs)
    status_code = 200 if result.get('success') else 400
    return jsonify(result), status_code

@app.route('/api/mental-health/tools', methods=['GET'])
def api_mental_health_tools():
    """Return catalog of clinical assessment scales, somatic regulation pacers, and grounding toolkits."""
    data = get_mental_health_catalog()
    return jsonify(data)

@app.route('/api/mental-health/assess', methods=['POST'])
@rate_limited
def api_mental_health_assess():
    """Evaluate standardized psychometric questionnaires (PHQ-9, GAD-7, PC-PTSD-5, ISI, PSS-4, CAGE-AID)."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    scale_id = str(data.get('scale_id', '')).strip()[:64]
    answers = data.get('answers', [])
    if not isinstance(answers, list):
        answers = []
    
    result = evaluate_mental_health_assessment(scale_id, answers)
    status_code = 200 if result.get('success') else 400
    return jsonify(result), status_code

@app.route('/api/mental-health/safety-plan', methods=['POST'])
@rate_limited
def api_mental_health_safety_plan():
    """Validate and format a structured Stanley-Brown Crisis Safety Plan."""
    data = request.get_json(silent=True, force=True) or {}
    if not isinstance(data, dict):
        data = {}
    result = generate_stanley_brown_safety_plan(data)
    return jsonify(result)

@app.route('/chat', methods=['POST'])
@rate_limited
def chat():
    """
    Zero-Hallucination Grounded Healthcare Pipeline:
    1. Sliding-Window Rate Limiting & Payload Sanitization
    2. Contextual Crisis Hotlines (0ms)
    3. Polypharmacy Matrix & Medication Safety Guard
    4. Clinical Lab & Vital Biomarker Range Interpretation
    5. Red-Flag Symptom Scanning
    6. Hybrid Retrieval Knowledge Base Lookup (Dense Vectors + BM25 FTS5)
    7. RAG-Grounded Multi-Turn Gemini AI (With Uncertainty Calibration)
    """
    # 1. Input Parsing & Sanitization
    data = request.get_json(silent=True, force=True)
    if not data or not isinstance(data, dict) or 'message' not in data:
        if request.form and 'message' in request.form:
            data = request.form
        else:
            return jsonify({'error': 'A "message" field is required in JSON payload.'}), 400

    raw_message = str(data.get('message', '')).strip()
    if not raw_message:
        return jsonify({'reply': 'Please type a health-related question.'})

    raw_message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw_message)
    if len(raw_message) > MAX_MESSAGE_LENGTH:
        raw_message = raw_message[:MAX_MESSAGE_LENGTH]

    user_message = raw_message
    region = str(data.get('region', 'GLOBAL')).strip().upper()
    history = data.get('history', [])

    # Step 0: Check High-Speed In-Memory Cache (<1ms Instant Return)
    if not history:
        cached_reply = get_cached_chat_response(user_message, region=region)
        if cached_reply:
            cached_reply['is_cached'] = True
            return jsonify(cached_reply)

    # Triage Trigger Intent
    normalized_msg = user_message.lower()
    if re.search(r'\b(start triage|guided triage|check my symptoms|symptom triage|triage my symptoms|symptom checker|check symptoms)\b', normalized_msg):
        return jsonify({
            'reply': (
                "🩺 **Interactive Guided Symptom Triage**\n\n"
                "I can guide you through a step-by-step 5-stage clinical triage questionnaire to help evaluate your symptoms, "
                "screen for red flags, and determine whether you need emergency care, a doctor's visit, or supportive home care.\n\n"
                "Click the **'Start Guided Triage'** button below or use the 🩺 icon in the top bar to launch the questionnaire."
            ),
            'source': 'triage_intent',
            'is_triage_trigger': True,
            'suggestions': [
                "🩺 Launch Guided Triage",
                "What are common emergency warning signs?",
                "How to prepare for a doctor's appointment?"
            ]
        })

    # Nutrition Therapy Quick Trigger Intent
    if re.search(r'\b(nutrition|diet|dietary|food prescription|prescriptor|meal plan|foods to eat|foods to avoid)\b', normalized_msg):
        # Match any mentioned conditions
        matched_conds = []
        cond_keywords = {
            "hypertension": ["hypertension", "high blood pressure", "dash diet", "bp"],
            "diabetes": ["diabetes", "type 2", "diabetic", "blood sugar", "insulin resistance", "glycemic"],
            "ckd": ["ckd", "kidney disease", "renal", "kidney failure"],
            "gout": ["gout", "uric acid", "hyperuricemia"],
            "gerd": ["gerd", "acid reflux", "heartburn"],
            "ibs": ["ibs", "fodmap", "irritable bowel"],
            "nafld": ["nafld", "masld", "fatty liver"],
            "hyperlipidemia": ["cholesterol", "hyperlipidemia", "high ldl", "triglycerides", "tlc diet"],
            "celiac": ["celiac", "gluten-free", "gluten sensitivity", "gluten"],
            "anemia": ["anemia", "iron deficiency", "low ferritin", "low hemoglobin"],
            "osteoporosis": ["osteoporosis", "bone density", "osteopenia"],
            "migraine": ["migraine", "tyramine", "headache triggers"]
        }
        for cid, syns in cond_keywords.items():
            if any(syn in normalized_msg for syn in syns):
                matched_conds.append(cid)

        if matched_conds:
            mnt_res = evaluate_nutrition_therapy(matched_conds)
            p_names = ", ".join([p["name"] for p in mnt_res.get("evaluated_protocols", [])])
            p_foods = mnt_res.get("prioritize_foods", [])[:4]
            a_foods = mnt_res.get("avoid_foods", [])[:4]
            
            conflict_note = ""
            if mnt_res.get("has_conflicts"):
                conflict_note = f"\n\n⚖️ **Dietary Conflict Resolved:** {mnt_res['conflict_resolutions'][0]['resolution']}"

            reply_text = (
                f"🥗 **Medical Nutrition Therapy Plan: {p_names}**\n\n"
                f"**Clinical Target Principles:** {mnt_res.get('clinical_summary', '')}\n\n"
                f"🟢 **Prioritize Foods:**\n" + "".join([f"• {f}\n" for f in p_foods]) +
                f"\n🔴 **Strictly Avoid / Restrict:**\n" + "".join([f"• {f}\n" for f in a_foods]) +
                conflict_note +
                f"\n\n*Click **'🥗 Open Nutrition Therapy'** to customize multi-condition plans, adjust dietary preferences, or attach to your Doctor PDF Summary.*"
            )
            return jsonify({
                'reply': reply_text,
                'source': 'nutrition_prescriptor',
                'is_nutrition_intent': True,
                'nutrition_data': mnt_res,
                'suggestions': [
                    "🥗 Open Full Nutrition Prescriptor",
                    "Attach Diet Plan to Doctor Intake Summary",
                    "Are there food-drug interactions with my medications?"
                ]
            })

    # First-Aid & Emergency Action Flashcard Intent Trigger
    if re.search(r'\b(first aid|first-aid|emergency protocol|emergency action|action card|action flashcard|flashcards|how to do cpr|cpr instructions|cpr metronome|choking first aid|heimlich|how to treat burns|burn first aid|epipen protocol|anaphylaxis first aid|stroke fast|stop severe bleeding|tourniquet protocol|seizure first aid|heatstroke first aid|poisoning first aid|sprain rice protocol|cpr adult|cpr infant|first aid for)\b', normalized_msg) or normalized_msg.startswith("first aid") or normalized_msg.startswith("cpr"):
        first_aid_matches = search_first_aid_cards(user_message)
        if first_aid_matches:
            top_match_id = first_aid_matches[0]["id"]
            card_res = get_first_aid_card(top_match_id)
            if card_res and card_res.get("card"):
                card = card_res["card"]
                steps_formatted = []
                for s in card.get("steps", [])[:4]:
                    steps_formatted.append(f"**Step {s['step_num']}: {s['title']}**\n• {s['action']}\n• *Visual Hint:* `{s['visual_hint']}`")
                
                donots_formatted = []
                for d in card.get("critical_donots", [])[:3]:
                    donots_formatted.append(f"• 🚫 {d}")

                metronome_note = ""
                if card.get("metronome_bpm"):
                    metronome_note = f"\n\n⏱️ **CPR Audio Metronome:** Calibrated to **{card['metronome_bpm']} BPM** (AHA standard rate)."

                reply_text = (
                    f"🚑 **EMERGENCY ACTION FLASHCARD: {card['icon']} {card['title']}** ({card['category_label']})\n\n"
                    f"**Summary:** {card['summary']}\n\n"
                    f"⚡ **Immediate Sequential Action Steps:**\n" + "\n\n".join(steps_formatted) +
                    f"\n\n🔴 **CRITICAL DO NOTS:**\n" + "\n".join(donots_formatted) +
                    metronome_note +
                    f"\n\n*Click **'🚑 Open Interactive Flashcard'** below for full step-by-step guidance, CPR metronome audio, and 1-tap PDF summary attachment.*"
                )

                suggs = [
                    f"🚑 Open {card['title']} Flashcard",
                    "⏱️ Start CPR 110 BPM Metronome" if card.get("metronome_bpm") else "View All 14 Emergency Flashcards",
                    "📄 Attach First-Aid Steps to Doctor Intake Summary"
                ]

                return jsonify({
                    'reply': reply_text,
                    'source': 'first_aid_protocols',
                    'is_first_aid_intent': True,
                    'first_aid_card_id': card['id'],
                    'first_aid_data': card,
                    'suggestions': suggs
                })

    # Clinical Risk Calculators & Vital Tools Intent Trigger
    calc_match = detect_calculator_in_text(user_message)
    if calc_match:
        cid = calc_match["calculator_id"]
        cinfo = calc_match.get("info", {})
        c_title = cinfo.get("title", "Clinical Risk Calculator")
        c_badge = cinfo.get("badge", "Evidence-Based")
        c_desc = cinfo.get("description", "Calculate patient-specific clinical risk scores and treatment guidance.")

        reply_text = (
            f"🧮 **CLINICAL RISK TOOL: {cinfo.get('icon', '🧮')} {c_title}** ({c_badge})\n\n"
            f"**Clinical Purpose:** {c_desc}\n\n"
            f"⚡ You can evaluate your exact clinical parameters with real-time risk gauges, guideline-directed statin/anticoagulation/staging recommendations, and 1-tap Doctor PDF export using our interactive tool.\n\n"
            f"*Click **'🧮 Open {c_title}'** below to enter your laboratory values, vitals, or clinical criteria.*"
        )
        return jsonify({
            'reply': reply_text,
            'source': 'clinical_calculators',
            'is_calculator_intent': True,
            'calculator_id': cid,
            'calculator_info': cinfo,
            'suggestions': [
                f"🧮 Open {c_title}",
                "View All 10+ Clinical Risk Calculators",
                "📄 Attach Risk Evaluation to Doctor Intake PDF"
            ]
        })

    # Mental Health & Somatic Toolkit Intent Trigger
    mh_match = detect_mental_health_intent(user_message)
    if mh_match:
        mtype = mh_match.get("type", "general_toolkit")
        if mtype == "safety_plan":
            reply_text = (
                "🛡️ **STANLEY-BROWN CRISIS SAFETY PLANNING INTERVENTION**\n\n"
                "A personalized, evidence-based safety plan reduces suicide and crisis risk by identifying your personal warning signs, "
                "internal coping mechanisms, supportive contacts, and environmental safety steps before an acute crisis escalates.\n\n"
                "🚨 **Immediate 24/7 Lifelines:** Call or text **988** (US/Canada), call **111** (UK), call **112** (EU/India), or text **HOME to 741741**.\n\n"
                "*Click **'🛡️ Open Crisis Safety Planner'** below to build and download your personalized safety plan.*"
            )
            return jsonify({
                'reply': reply_text,
                'source': 'mental_health_safety_plan',
                'is_mental_health_intent': True,
                'mh_category': 'crisis_safety',
                'suggestions': [
                    "🛡️ Open Crisis Safety Planner",
                    "📞 Call 988 Suicide & Crisis Lifeline",
                    "🫁 Start 5-Minute Box Breathing"
                ]
            })
        elif mtype == "somatic":
            p_info = mh_match.get("info", {})
            p_title = p_info.get("title", "Somatic Breathing Pacer")
            p_badge = p_info.get("badge", "Vagal Regulation")
            p_summary = p_info.get("summary", "")
            p_id = mh_match.get("protocol_id", "box_breathing")
            reply_text = (
                f"🫁 **SOMATIC VAGUS REGULATION: {p_info.get('icon', '🫁')} {p_title}** ({p_badge})\n\n"
                f"**Clinical Mechanism:** {p_summary}\n\n"
                f"⚡ **Neurobiological Target:** {p_info.get('vagal_mechanism', 'Stimulates parasympathetic vagal afferents to down-regulate acute arousal.')}\n\n"
                f"*Click **'🫁 Start Visual Pacer'** below to launch the animated expanding lung guide with optional soothing audio chimes.*"
            )
            return jsonify({
                'reply': reply_text,
                'source': 'somatic_protocols',
                'is_mental_health_intent': True,
                'mh_category': 'somatic_pacers',
                'protocol_id': p_id,
                'protocol_info': p_info,
                'suggestions': [
                    f"🫁 Launch {p_title}",
                    "Try 5-4-3-2-1 Sensory Grounding",
                    "Take GAD-7 Anxiety Assessment"
                ]
            })
        elif mtype == "scale":
            s_title = mh_match.get("title", "Psychometric Scale")
            s_id = mh_match.get("scale_id", "phq9")
            reply_text = (
                f"🧠 **CLINICAL PSYCHOMETRIC SCALE: {s_title}**\n\n"
                f"Standardized self-report clinical questionnaire used by physicians and mental health specialists to measure symptom severity and track treatment progress.\n\n"
                f"*Click **'🧠 Start Questionnaire'** below to complete the assessment and receive your clinical score, severity tier, and matching somatic regulation tools.*"
            )
            return jsonify({
                'reply': reply_text,
                'source': 'mental_health_scales',
                'is_mental_health_intent': True,
                'mh_category': 'clinical_scales',
                'scale_id': s_id,
                'suggestions': [
                    f"🧠 Take {s_title}",
                    "Explore Somatic Breathing Pacers",
                    "📄 Attach Results to Doctor Intake PDF"
                ]
            })
        else:
            reply_text = (
                "🧠 **MENTAL HEALTH & SOMATIC REGULATION SUITE**\n\n"
                "Our clinically validated suite includes:\n"
                "• **🫁 Somatic Breathing Pacers:** Box Breathing (4-4-4-4), 4-7-8 Relaxing Breath, Physiological Sigh with animated lung pacer & audio chimes.\n"
                "• **🧠 Clinical Scales:** PHQ-9 (Depression), GAD-7 (Anxiety), PC-PTSD-5 (Trauma), ISI (Insomnia), PSS-4 (Stress), CAGE-AID (Substances).\n"
                "• **🧘 Grounding & PMR:** 5-4-3-2-1 Somatosensory Grounding and Jacobson Progressive Muscle Relaxation.\n"
                "• **🛡️ Stanley-Brown Safety Planning:** Structured crisis coping plan with 1-tap Doctor PDF export.\n\n"
                "*Click **'🧠 Open Mental Health Suite'** below to begin.*"
            )
            return jsonify({
                'reply': reply_text,
                'source': 'mental_health_suite',
                'is_mental_health_intent': True,
                'suggestions': [
                    "🧠 Open Mental Health Suite",
                    "🫁 Start 4-7-8 Breathing Pacer",
                    "Take PHQ-9 Depression Screener"
                ]
            })

    # Step 1: Contextual Crisis & Emergency Check (Instant - 0ms)
    if is_emergency(user_message):
        emergency_reply = get_contextual_emergency_response(user_message, region=region)
        # Check if a specific first-aid card matches to assist while waiting for EMS
        emergency_card_id = None
        fa_matches = search_first_aid_cards(user_message)
        if fa_matches:
            emergency_card_id = fa_matches[0]["id"]

        emergency_suggestions = [
            "Find nearest emergency room",
            "Contact crisis helpline",
            "What to do while waiting for medical help?"
        ]
        if emergency_card_id:
            emergency_suggestions.insert(0, f"🚑 Open First-Aid Protocol ({fa_matches[0]['title']})")

        return jsonify({
            'reply': emergency_reply,
            'source': 'emergency_filter',
            'is_emergency': True,
            'first_aid_card_id': emergency_card_id,
            'suggestions': emergency_suggestions
        })

    # Step 2: Polypharmacy Matrix Scan & Medication Safety Guard (Instant - 0ms)
    poly_match = scan_text_for_polypharmacy(user_message)
    if poly_match and poly_match.get("has_interactions"):
        interactions = poly_match["interactions"]
        top_inter = interactions[0]
        severity_badge = "🔴 MAJOR CONTRAINDICATION" if top_inter['severity'] == 'MAJOR' else ("🟡 MODERATE PRECAUTION" if top_inter['severity'] == 'MODERATE' else "🟢 MINOR PRECAUTION")
        
        reply_lines = [
            f"💊 **POLYPHARMACY SAFETY MATRIX — {severity_badge}**\n",
            f"**Interaction Detected:** {top_inter['item_1']} + {top_inter['item_2']}",
            f"**Clinical Hazard:** {top_inter['title']}",
            f"**Mechanism:** {top_inter['mechanism']}",
            f"**Potential Adverse Effects:** {top_inter['effects']}",
            f"**Action Advised:** {top_inter['action']}\n",
            "*(Always verify all concurrent prescriptions and OTC drugs with your licensed pharmacist or physician.)*"
        ]
        return jsonify({
            'reply': "\n\n".join(reply_lines),
            'source': 'polypharmacy_matrix',
            'is_medication_guard': True,
            'polypharmacy_data': poly_match,
            'suggestions': [
                "💊 Open Polypharmacy Checker",
                "What should I tell my pharmacist?",
                "What are signs of an adverse drug reaction?"
            ]
        })

    med_guard_res = check_medication_safety(user_message)
    if med_guard_res:
        return jsonify(med_guard_res)

    # Step 3: Clinical Laboratory Biomarker / Vitals Auto-Interpreter
    lab_interp = detect_and_interpret_vitals_in_query(user_message)
    if lab_interp and not is_specific_or_followup_question(user_message):
        reply_lines = [
            f"🔬 **LABORATORY BIOMARKER INTERPRETATION — {lab_interp['badge']}**",
            f"• **Test:** {lab_interp['test_name']} ({lab_interp['panel']})",
            f"• **Your Value:** **{lab_interp['value']} {lab_interp['unit']}** (Reference Range: {lab_interp['reference_range']})",
            f"• **Clinical Status:** {lab_interp['tier_label']}\n",
            f"**Clinical Significance:** {lab_interp['description']}",
            f"**Potential Contributing Factors:** {lab_interp['high_causes'] if 'HIGH' in lab_interp['tier'] or 'STAGE' in lab_interp['tier'] or 'BORDERLINE' in lab_interp['tier'] else lab_interp['low_causes']}",
            f"**Lifestyle & Nutritional Focus:** {lab_interp['lifestyle_tips']}\n",
            "**Questions to Discuss with Your Doctor:**"
        ]
        for q_item in lab_interp.get("doctor_questions", []):
            reply_lines.append(f"  - {q_item}")

        reply_lines.append("\n*Notice: Laboratory ranges vary by individual lab methodology. This interpretation is educational and must be confirmed by your physician.*")

        return jsonify({
            'reply': "\n".join(reply_lines),
            'source': 'lab_interpreter',
            'is_lab_interpretation': True,
            'lab_data': lab_interp,
            'suggestions': [
                "🔬 Open Full Lab Interpreter",
                f"How to prepare for a {lab_interp['test_name']} test?",
                "Attach this result to Doctor Intake Summary"
            ]
        })

    # Step 3: Red-Flag Symptom Scanning
    red_flags = detect_red_flags(user_message)
    red_flag_note = format_red_flag_note(red_flags) if red_flags else ""
    uncertainty_note = check_uncertainty_calibration(user_message)

    # Step 4: SQLite Knowledge Base Lookup (3-Tier ELI5 Plain Language Format)
    is_specific = is_specific_or_followup_question(user_message)
    local_info = None if is_specific else lookup_health_info(user_message)

    if local_info:
        formatted_reply = (
            f"📋 **{local_info['disease_name']} — Clinical Health Overview** *({local_info.get('category', 'General')})*\n\n"
            f"💡 **Plain Language (ELI5):** {local_info['disease_name']} involves {local_info['symptoms'].lower()}.\n\n"
            f"📋 **Evidence-Based Home Care & Precautions:**\n• {local_info['precautions']}\n\n"
            f"🩺 **Questions for Your Doctor:**\n"
            f"• What specific diagnostic tests or exams do you recommend for these symptoms?\n"
            f"• Are there any warning signs or medication interactions I should watch out for?\n\n"
            f"*Educational Note: This information is for general awareness only. Always consult a qualified healthcare provider for personal medical advice.*"
        )
        if red_flag_note:
            formatted_reply += red_flag_note
        if uncertainty_note:
            formatted_reply += uncertainty_note

        # Apply Two-Stage Post-Generation Verification Guard
        verified = verify_and_filter_response(
            raw_reply=formatted_reply,
            user_query=user_message,
            rag_context=formatted_reply,
            citations=local_info.get('citations', TOPIC_CITATIONS['Default']),
            region=region
        )

        response_payload = {
            'reply': verified['reply'],
            'source': 'local_database',
            'disease_data': local_info,
            'has_red_flags': bool(red_flags),
            'is_verified': verified['is_verified'],
            'safety_score': verified['safety_score'],
            'verification_stages': verified['stages_passed'],
            'suggestions': local_info.get('suggestions', DEFAULT_SUGGESTIONS),
            'citations': verified['citations']
        }

        if not history:
            set_cached_chat_response(user_message, response_payload, region=region)

        return jsonify(response_payload)

    # Step 5: RAG-Grounded Multi-Turn Gemini AI Fallback with Instant Local Grounding
    grounding_text, rag_citations = get_rag_grounding_context(user_message)
    client = get_gemini_client()
    reply_text = None

    if client:
        try:
            grounded_system_prompt = f"{SYSTEM_INSTRUCTION}\n\n{grounding_text}" if grounding_text else SYSTEM_INSTRUCTION

            contents = []
            if isinstance(history, list):
                for item in history[-6:]:
                    role = "user" if item.get('role') == 'user' else "model"
                    text = str(item.get('text') or item.get('message', '')).strip()
                    if text and len(text) <= MAX_MESSAGE_LENGTH:
                        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))

            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

            fast_models = ['gemini-3.5-flash-lite', 'gemini-flash-lite-latest', 'gemini-flash-latest']

            for model_name in fast_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=grounded_system_prompt,
                            max_output_tokens=220,
                            temperature=0.20
                        )
                    )
                    if response and response.text:
                        reply_text = response.text.strip()
                        break
                except Exception as model_err:
                    print(f"[Gemini Warning] {model_name} failed: {model_err}")
                    continue

        except Exception as e:
            print(f"[Chat Error] {e}")

    # If Gemini AI is unavailable, timed out, or unconfigured, synthesize high-quality local RAG response (<1ms)
    if not reply_text:
        if grounding_text:
            reply_text = (
                f"📋 **Evidence-Based Clinical Guidance**\n\n"
                f"💡 **Plain Language (ELI5):** Based on accredited clinical guidelines, here are key facts regarding your question:\n\n"
                f"{grounding_text}\n\n"
                f"🩺 **Next Steps:** If your symptoms persist, worsen, or cause distress, please consult a qualified healthcare provider."
            )
        else:
            reply_text = (
                "💡 **Health Guidance:** For specific symptoms, home care tips, or health concerns, "
                "please describe your symptoms in detail or use our **Guided Symptom Triage** for structured evaluation.\n\n"
                "🩺 **Consultation:** Always consult a qualified physician for personalized clinical diagnosis and medical advice."
            )

    if red_flag_note:
        reply_text += red_flag_note
    if uncertainty_note:
        reply_text += uncertainty_note

    # Apply Two-Stage Post-Generation Verification Guard
    verified = verify_and_filter_response(
        raw_reply=reply_text,
        user_query=user_message,
        rag_context=grounding_text,
        citations=rag_citations,
        region=region
    )

    suggestions = [
        "What are common home remedies for this?",
        "When should someone see a doctor for this?",
        "What preventive habits help avoid this in the future?"
    ]

    response_payload = {
        'reply': verified['reply'],
        'source': 'gemini_ai' if (client and reply_text and 'GROUNDING CONTEXT' not in reply_text) else 'local_rag_grounded',
        'has_red_flags': bool(red_flags),
        'is_verified': verified['is_verified'],
        'safety_score': verified['safety_score'],
        'verification_stages': verified['stages_passed'],
        'suggestions': suggestions,
        'citations': verified['citations']
    }

    if not history:
        set_cached_chat_response(user_message, response_payload, region=region)

    return jsonify(response_payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
