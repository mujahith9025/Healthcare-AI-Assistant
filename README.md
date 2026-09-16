# 🩺 AI Healthcare Information Assistant

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render_Hosted-00d97e?style=for-the-badge&logo=render&logoColor=white)](https://healthcare-ai-assistant-tsn2.onrender.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Framework-Flask_3.1-black.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Gemini Vision](https://img.shields.io/badge/AI-Gemini_Multimodal_Vision-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)

An educational, plain-language healthcare intelligence platform designed to provide safe, general wellness guidance, symptom summaries, clinical risk scores, and medical document OCR with strict safety grounding.

🌐 **Live Application URL**: **[https://healthcare-ai-assistant-tsn2.onrender.com/](https://healthcare-ai-assistant-tsn2.onrender.com/)**

> ⚠️ **Important Safety Disclaimer**: This application is strictly an **educational information tool** and is **NOT** a diagnostic system. It never diagnoses medical conditions, prescribes medication, or replaces professional medical consultation. Always consult a qualified physician or healthcare provider for personal health concerns. In an emergency, contact local emergency services (e.g., 911, 112, 999) immediately.

---

## 🌟 Core Features & 4 Unified Health Hubs

1. **🩺 Hub 1: Symptom Triage & Interactive 2D Body Map**:
   - 2D anatomical locator (Head, Neck, Chest, Abdomen, Pelvis, Spine, Knees, Feet)
   - 5-step guided clinical risk stratification wizard (Levels 1–4)
2. **💊 Hub 2: Medications, 25+ Lab Biomarker Gauges & Nutrition Therapy**:
   - Multi-drug polypharmacy contraindication matrix (50+ drug-drug pairings)
   - 25+ laboratory biomarker reference gauges (Glucose, HbA1c, Lipids, eGFR, Creatinine)
   - Diet-Disease nutrition therapy prescriptor with conflict resolution
3. **🧮 Hub 3: Evidence-Based Clinical Risk Suite**:
   - ASCVD 10-Year Cardiovascular Risk Calculator (ACC/AHA)
   - CHA₂DS₂-VASc Atrial Fibrillation Stroke Risk
   - CKD-EPI eGFR Kidney Function Staging
   - FIB-4 Liver Fibrosis Index, CURB-65 Pneumonia Severity, Wells' DVT/PE Criteria & BMI
4. **🧠 Hub 4: Calm & Mental Wellbeing Hub**:
   - Somatosensory vagus lung pacers (Box Breathing 4-4-4-4, 4-7-8 Parasympathetic)
   - Clinically validated psychometric screening scales (PHQ-9, GAD-7, PC-PTSD-5, ISI)
   - Stanley-Brown Crisis Safety Plan generator
5. **📸 Multimodal Vision OCR & Radiology Summarizer**:
   - 3-Tier ELI5 extraction for prescriptions, bloodwork slips, and **Diagnostic Radiology Reports (Chest X-Ray, Lumbar Spine MRI, CT Scans, Ultrasound, ECG)**
   - Plain-Language Medical Jargon Glossary explaining complex Latin terms
   - 1-Click *"Locate on 2D Body Map"* cross-linking
6. **🚑 First-Aid Emergency Flashcards & 110 BPM CPR Metronome**:
   - 14 interactive emergency protocols with real-time audio metronome
7. **📄 Doctor Intake Summary PDF Export**:
   - 1-Click generation of high-resolution, printable pre-consultation reports

---

## 🏛️ 3-Tier Response Architecture

Every user question is processed through a strict, safety-first pipeline:

```
[ User Query ]
       │
       ▼
1. Emergency Filter (0ms) ──────────► [ 🚨 Urgent-Care Response ] (Skip AI/DB)
       │ (No Match)
       ▼
2. Local SQLite Database (0ms) ─────► [ 📋 Structured Symptoms & Precautions ] (No API call)
       │ (No Match)
       ▼
3. Gemini AI Fallback (< 2s) ──────► [ 💬 Plain-Language Educational Summary + Disclaimer ]
```

1. **Tier 1 — Instant Emergency Triage**: Checks against high-risk triggers (*chest pain, difficulty breathing, unconscious, severe bleeding, overdose, etc.*). Immediately returns an emergency alert without delay.
2. **Tier 2 — Curated SQLite Knowledge Base**: Checks `database/health_info.db` containing 123 verified clinical conditions with FTS5 indexing for instantaneous, verified summaries.
3. **Tier 3 — Google Gemini API**: Calls `gemini-3.5-flash-lite` via the official `google-genai` SDK with strict safety system instructions, keeping responses concise, non-diagnostic, and concluding with a doctor consultation reminder.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10+
- A Google Gemini API Key ([Get one free at Google AI Studio](https://aistudio.google.com/))

### 1. Clone & Navigate to Project
```bash
git clone https://github.com/mujahith9025/Healthcare-AI-Assistant.git
cd Healthcare-AI-Assistant
```

### 2. 1-Click Start

- **On Windows**: Double-click **`start.bat`**
- **On macOS / Linux**: Run **`bash start.sh`**

*(Or manually run `python -m venv venv`, `pip install -r requirements.txt`, and `python app.py`)*

Visit **`http://localhost:5000`** in your web browser.

---

## 📁 Project Structure

```text
Healthcare-AI-Assistant/
├── app.py                     # Main Flask server with multi-tier pipeline
├── requirements.txt           # Pinned production dependencies
├── Procfile                   # Gunicorn deployment configuration
├── start.bat                  # 1-Click Windows launcher
├── start.sh                   # 1-Click macOS/Linux launcher
├── .env.example               # Environment variable template
├── .gitignore                 # Ignores .env, caches, venv, and *.db
├── README.md                  # Comprehensive project documentation
├── benchmarks/
│   ├── golden_dataset.json    # 50-case curated Medical QA benchmark dataset
│   ├── benchmark_runner.py    # Automated test runner & metrics scorecard
│   ├── benchmark_report.md    # Generated clinical scorecard markdown
│   └── benchmark_results.json # Machine-readable benchmark test results
├── database/
│   ├── health_info.db         # SQLite database with 123 conditions & FTS5 indexing
│   ├── setup_db.py            # Database initialization and seed script
│   └── db_helper.py           # FTS5 search, RAG context retrieval & citations
├── safety/
│   ├── emergency_check.py     # 0ms contextual emergency hotlines & red flags
│   ├── medication_guard.py    # 0ms drug interaction & dosage safety guard
│   ├── guided_triage.py       # 5-step clinical risk stratification engine
│   ├── lab_interpreter.py     # 25+ lab biomarker target ranges & interpretation
│   ├── polypharmacy_matrix.py # Multi-drug interaction matrix & CYP450 checks
│   ├── nutrition_therapy.py   # Medical Nutrition Therapy prescriptor
│   ├── first_aid_cards.py     # 14 emergency first-aid protocols & metronome
│   ├── clinical_calculators.py# ASCVD, eGFR, CHA₂DS₂-VASc, FIB-4, Wells', CURB-65
│   ├── mental_health_toolkit.py# Somatic pacers, PHQ-9/GAD-7, Safety plan
│   ├── vision_ocr.py          # Multimodal Vision OCR & Radiology Summarizer
│   └── post_verification.py   # 2-stage verification & fact-checking guard
├── templates/
│   └── index.html             # Responsive unified dashboard & modals
└── static/
    ├── style.css              # Modern responsive CSS (desktop, tablet, mobile)
    └── script.js              # State controller, multi-turn history & hub wizards
```

---

## 🧪 Running Unit Tests & Medical QA Benchmark Suite

Run the full automated 112-case test suite:
```bash
python -m unittest discover -s tests -v
```

Run the 50-case Medical QA Golden Benchmark evaluation:
```bash
python benchmarks/benchmark_runner.py
```

---

## 🌐 Live Deployment

The application is deployed on **Render**:
- **Live URL**: **`https://healthcare-ai-assistant-tsn2.onrender.com/`**
- **Hosting**: Render Web Service (Python 3 / Gunicorn)
- **CI/CD**: Automatic zero-downtime deployment on git push to `main` branch.

---

## 🔒 Safety & Medical Compliance Controls

- **0ms Contextual Crisis Hotlines**: Instant region-specific redirection (US: 911/988, UK: 999/111, India: 112/108, CA: 911/988).
- **0ms Pharmacological Guard**: Blocks drug combination queries and prescription dosage requests.
- **Red-Flag Clinical Warnings**: Identifies acute symptoms (meningitis, stroke, internal bleeding, DVT) and attaches warning banners.
- **Fact Grounding (RAG)**: Injects vetted SQLite facts and links authoritative references (WHO, NIH, CDC, AHA, Mayo Clinic).
- **Uncertainty Calibration**: Qualifies biological recovery variations and firmly denies 100% cure claims.
- **Input Sanitization & Rate Limiting**: 500-character cap, control character stripping, sliding-window abuse prevention.
