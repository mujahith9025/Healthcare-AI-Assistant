# 🩺 AI Healthcare Information Assistant

An educational, plain-language healthcare information chatbot designed to provide safe, general wellness guidance, symptom summaries, and health precautions.

> ⚠️ **Important Safety Disclaimer**: This application is strictly an **educational information tool** and is **NOT** a diagnostic system. It never diagnoses medical conditions, prescribes medication, or replaces professional medical consultation. Always consult a qualified physician or healthcare provider for personal health concerns. In an emergency, contact local emergency services (e.g., 911, 112, 999) immediately.

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
2. **Tier 2 — Curated SQLite Knowledge Base**: Checks `database/health_info.db` containing ~18 common conditions and symptom aliases (*Cold, Flu, Dengue, Diabetes, Hypertension, Migraine, etc.*) for instantaneous, verified summaries.
3. **Tier 3 — Google Gemini API**: Calls `gemini-3.5-flash-lite` via the official `google-genai` SDK with strict safety system instructions, keeping responses concise (<80 words), non-diagnostic, and concluding with a doctor consultation reminder.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10+
- A Google Gemini API Key ([Get one free at Google AI Studio](https://aistudio.google.com/))

### 1. Clone & Navigate to Project
```bash
cd ai-health-assistant
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Server
```bash
python app.py
```
Visit **`http://localhost:5000`** in your web browser.

---

## 📁 Project Structure

```text
ai-health-assistant/
├── app.py                     # Main Flask server with multi-tier pipeline
├── requirements.txt           # Pinned production dependencies
├── Procfile                   # Gunicorn deployment configuration
├── .env.example               # Environment variable template
├── .gitignore                 # Ignores .env, caches, venv, and *.db
├── README.md                  # Comprehensive project documentation
├── benchmarks/
│   ├── golden_dataset.json    # 50-case curated Medical QA benchmark dataset
│   ├── benchmark_runner.py    # Automated test runner & metrics scorecard
│   ├── benchmark_report.md    # Generated clinical scorecard markdown
│   └── benchmark_results.json # Machine-readable benchmark test results
├── database/
│   ├── health_info.db         # SQLite database with 58 conditions & FTS5 indexing
│   ├── setup_db.py            # Database initialization and seed script
│   └── db_helper.py           # FTS5 search, RAG context retrieval & citations
├── safety/
│   ├── emergency_check.py     # 0ms contextual emergency hotlines & red flags
│   ├── medication_guard.py    # 0ms drug interaction & dosage safety guard
│   └── guided_triage.py       # 5-step clinical risk stratification engine
├── templates/
│   └── index.html             # Responsive chat interface with Guided Triage modal
└── static/
    ├── style.css              # Modern responsive CSS (desktop, tablet, mobile)
    └── script.js              # State controller, multi-turn history & triage wizard
```

---

## 🧪 Running the Medical QA Golden Benchmark Suite

Run the automated 50-case benchmark evaluation suite across all 7 medical QA domains:
```bash
python benchmarks/benchmark_runner.py
```
This evaluates emergency recall, pharmacological safety, red-flag detection, RAG fact grounding, uncertainty calibration, and latency benchmarks, exporting results to `benchmarks/benchmark_report.md`.

---

## 🌐 Deployment to Render

1. Push your repository to **GitHub**.
2. In [Render Dashboard](https://dashboard.render.com/), create a new **Web Service** connected to your repository.
3. Configure the settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = *your_gemini_api_key*
5. Click **Deploy Web Service**.

---

## 🔒 Safety & Medical Compliance Controls

- **0ms Contextual Crisis Hotlines**: Instant region-specific redirection (US: 911/988, UK: 999/111, India: 112/108, CA: 911/988).
- **0ms Pharmacological Guard**: Blocks drug combination queries and prescription dosage requests.
- **Red-Flag Clinical Warnings**: Identifies acute symptoms (meningitis, stroke, internal bleeding, DVT) and attaches warning banners.
- **Fact Grounding (RAG)**: Injects vetted SQLite facts and links authoritative references (WHO, NIH, CDC, AHA, Mayo Clinic).
- **Uncertainty Calibration**: Qualifies biological recovery variations and firmly denies 100% cure claims.
- **Interactive Guided Triage**: 5-step structured clinical assessment with 4-tier risk stratification (Levels 1–4).
- **Input Sanitization & Rate Limiting**: 500-character cap, control character stripping, sliding-window abuse prevention.
