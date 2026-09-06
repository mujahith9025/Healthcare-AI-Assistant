import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), 'health_info.db')

# Expanded symptom/term aliases mapped to curated database topics for instant 0ms responses
DISEASE_ALIASES = {
    "fever": "Flu",
    "headache": "Migraine",
    "cold": "Common Cold",
    "cough": "Common Cold",
    "sneezing": "Common Cold",
    "sore throat": "Common Cold",
    "high blood pressure": "Hypertension",
    "blood pressure": "Hypertension",
    "high bp": "Hypertension",
    "low bp": "Hypotension",
    "low blood pressure": "Hypotension",
    "blood sugar": "Diabetes",
    "sugar level": "Diabetes",
    "thyroid": "Hypothyroidism",
    "cholesterol": "High Cholesterol",
    "stomach ache": "Food Poisoning",
    "stomach pain": "Food Poisoning",
    "vomiting": "Food Poisoning",
    "diarrhea": "Acute Diarrhea",
    "loose motions": "Acute Diarrhea",
    "heartburn": "GERD",
    "acid reflux": "GERD",
    "gas problem": "GERD",
    "bloating": "IBS",
    "pink eye": "Conjunctivitis",
    "joint pain": "Osteoarthritis",
    "knee pain": "Osteoarthritis",
    "back pain": "Lumbar Strain",
    "neck pain": "Cervical Spondylosis",
    "heel pain": "Plantar Fasciitis",
    "wrist pain": "Carpal Tunnel Syndrome",
    "sleeplessness": "Insomnia",
    "cant sleep": "Insomnia",
    "cannot sleep": "Insomnia",
    "trouble sleeping": "Insomnia",
    "anxiety": "Generalized Anxiety",
    "skin rash": "Eczema",
    "itchy skin": "Eczema",
    "dry skin": "Eczema",
    "pimples": "Acne Vulgaris",
    "acne": "Acne Vulgaris",
    "stye": "Stye",
    "kidney stone": "Kidney Stones",
    "urine burning": "UTI",
    "ear ache": "Ear Infection",
    "ringing ears": "Tinnitus Awareness",
    "sunburn": "Sunburn",
    "cold sores": "Cold Sores"
}

# Trusted clinical authority citations by category / topic
TOPIC_CITATIONS = {
    "Cardiovascular": [
        {"name": "American Heart Association (AHA)", "url": "https://www.heart.org/en/health-topics"},
        {"name": "WHO — Cardiovascular Diseases", "url": "https://www.who.int/health-topics/cardiovascular-diseases"}
    ],
    "Metabolic": [
        {"name": "American Diabetes Association (ADA)", "url": "https://diabetes.org/"},
        {"name": "NIH (NIDDK) — Metabolic Info", "url": "https://www.niddk.nih.gov/health-information"}
    ],
    "Infectious": [
        {"name": "CDC — Infectious Diseases", "url": "https://www.cdc.gov/"},
        {"name": "WHO — Global Health Guidelines", "url": "https://www.who.int/health-topics"}
    ],
    "Respiratory": [
        {"name": "American Lung Association", "url": "https://www.lung.org/"},
        {"name": "NIH (NHLBI) — Respiratory Health", "url": "https://www.nhlbi.nih.gov/"}
    ],
    "Neurological": [
        {"name": "American Migraine Foundation", "url": "https://americanmigrainefoundation.org/"},
        {"name": "Mayo Clinic — Neurology", "url": "https://www.mayoclinic.org/departments-centers/neurology"}
    ],
    "Gastrointestinal": [
        {"name": "American Gastroenterological Association", "url": "https://gastro.org/"},
        {"name": "NIH (NIDDK) — Digestive Health", "url": "https://www.niddk.nih.gov/health-information/digestive-diseases"}
    ],
    "Musculoskeletal": [
        {"name": "Arthritis Foundation", "url": "https://www.arthritis.org/"},
        {"name": "NIH (NIAMS) — Bone & Joint Health", "url": "https://www.niams.nih.gov/health-topics"}
    ],
    "Dermatology": [
        {"name": "American Academy of Dermatology (AAD)", "url": "https://www.aad.org/"},
        {"name": "National Eczema Association", "url": "https://nationaleczema.org/"}
    ],
    "Urological": [
        {"name": "Urology Care Foundation", "url": "https://www.urologyhealth.org/"},
        {"name": "NIH (NIDDK) — Kidney & Urologic Diseases", "url": "https://www.niddk.nih.gov/health-information/urologic-diseases"}
    ],
    "Reproductive": [
        {"name": "American College of Obstetricians and Gynecologists (ACOG)", "url": "https://www.acog.org/womens-health"},
        {"name": "NIH (NICHD) — Women's Health", "url": "https://www.nichd.nih.gov/health/topics/womenshealth"}
    ],
    "Sensory": [
        {"name": "American Academy of Ophthalmology", "url": "https://www.aao.org/eye-health"},
        {"name": "NIH (NIDCD) — Hearing & Ear Disorders", "url": "https://www.nidcd.nih.gov/health"}
    ],
    "Nutrition": [
        {"name": "NIH — Office of Dietary Supplements", "url": "https://ods.od.nih.gov/"},
        {"name": "Harvard T.H. Chan School of Public Health — Nutrition", "url": "https://www.hsph.harvard.edu/nutritionsource/"}
    ],
    "Default": [
        {"name": "World Health Organization (WHO)", "url": "https://www.who.int/"},
        {"name": "National Institutes of Health (NIH)", "url": "https://www.nih.gov/"},
        {"name": "Mayo Clinic Health Information", "url": "https://www.mayoclinic.org/"}
    ]
}

def get_db_connection():
    """Establish connection to health_info SQLite database."""
    if not os.path.exists(DB_PATH):
        from database.setup_db import init_db
        init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def sanitize_fts_query(query: str) -> str:
    """Sanitize user input string into safe FTS5 MATCH query syntax."""
    tokens = re.findall(r'[a-zA-Z0-9]+', query)
    if not tokens:
        return ""
    stopwords = {"what", "are", "the", "symptoms", "of", "and", "in", "is", "for", "how", "to", "treat", "have", "i", "a", "an"}
    meaningful_tokens = [t for t in tokens if t.lower() not in stopwords and len(t) > 2]
    if not meaningful_tokens:
        meaningful_tokens = tokens
    return " OR ".join([f'"{t}"' for t in meaningful_tokens[:6]])

def get_rag_grounding_context(query: str) -> tuple:
    """
    RAG Grounding: Retrieve verified clinical facts using Hybrid Retrieval (Dense Semantic Vectors + FTS5 BM25).
    Returns (grounding_text, citations_list).
    """
    if not query or not query.strip():
        return "", TOPIC_CITATIONS["Default"]

    try:
        from database.hybrid_retrieval import get_hybrid_engine
        engine = get_hybrid_engine()
        hybrid_matches = engine.hybrid_search(query, top_k=2)
    except Exception as e:
        print(f"[RAG Warning] Hybrid search exception: {e}")
        hybrid_matches = []

    matched_rows = []
    if hybrid_matches:
        for m in hybrid_matches:
            matched_rows.append({
                "disease_name": m["disease_name"],
                "category": m["category"],
                "symptoms": m["symptoms"],
                "precautions": m["precautions"]
            })
    else:
        # Fallback to direct FTS5 query
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            fts_query = sanitize_fts_query(query)
            if fts_query:
                cursor.execute('''
                    SELECT disease_name, category, symptoms, precautions, bm25(health_info_fts) as rank
                    FROM health_info_fts
                    WHERE health_info_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT 2
                ''', (fts_query,))
                matched_rows = [dict(r) for r in cursor.fetchall()]
        except Exception as err:
            print(f"[RAG Warning] FTS fallback exception: {err}")

        if not matched_rows:
            cursor.execute('SELECT disease_name, category, symptoms, precautions FROM health_info LIMIT 2')
            matched_rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

    if not matched_rows:
        return "", TOPIC_CITATIONS["Default"]

    # Format structured clinical context
    context_lines = ["GROUNDING CONTEXT FROM VERIFIED CLINICAL KNOWLEDGE BASE (HYBRID DENSE+SPARSE):"]
    citations = []

    for row in matched_rows:
        context_lines.append(
            f"• Condition: {row['disease_name']} ({row['category']})\n"
            f"  Verified Symptoms: {row['symptoms']}\n"
            f"  Verified Precautions: {row['precautions']}"
        )
        cat_citations = TOPIC_CITATIONS.get(row['category'], TOPIC_CITATIONS["Default"])
        for c in cat_citations:
            if c not in citations:
                citations.append(c)

    grounding_text = "\n".join(context_lines)
    return grounding_text, citations if citations else TOPIC_CITATIONS["Default"]

def lookup_health_info(query: str):
    """
    Intelligent Multi-Tier Hybrid Search:
    1. Exact Word-Boundary Name Match (0ms)
    2. Symptom / Clinical Alias Match (0ms)
    3. Dense Semantic Vector + SQLite FTS5 BM25 Reciprocal Rank Fusion (RRF)
    """
    if not query or not query.strip():
        return None

    cleaned_query = query.strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT disease_id, disease_name, category, symptoms, precautions FROM health_info')
    rows = cursor.fetchall()

    matched_disease = None

    # Tier A: Direct disease name match using exact word boundary
    for row in rows:
        name = row['disease_name']
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, cleaned_query, re.IGNORECASE):
            matched_disease = row
            break

    # Tier B: Symptom / term alias match
    if not matched_disease:
        for alias_key, target_disease in DISEASE_ALIASES.items():
            pattern = r'\b' + re.escape(alias_key) + r'\b'
            if re.search(pattern, cleaned_query, re.IGNORECASE):
                for row in rows:
                    if row['disease_name'].lower() == target_disease.lower():
                        matched_disease = row
                        break
                if matched_disease:
                    break

    conn.close()

    # Tier C: Dense Semantic Vector + Sparse FTS5 BM25 Reciprocal Rank Fusion
    if not matched_disease:
        try:
            from database.hybrid_retrieval import get_hybrid_engine
            engine = get_hybrid_engine()
            hybrid_results = engine.hybrid_search(cleaned_query, top_k=1)
            if hybrid_results:
                top_match = hybrid_results[0]
                if top_match["confidence"] >= 0.70 or top_match["dense_score"] >= 0.45:
                    matched_disease = top_match
        except Exception as h_err:
            print(f"[Hybrid Lookup Warning] Hybrid search failed: {h_err}")

    if matched_disease:
        d_name = matched_disease["disease_name"]
        category = matched_disease["category"]

        suggestions = [
            f"What are home care tips for {d_name}?",
            f"When should someone with {d_name} see a doctor?",
            f"What diet or lifestyle changes help {d_name}?"
        ]
        citations = TOPIC_CITATIONS.get(category, TOPIC_CITATIONS["Default"])

        return {
            "disease_id": matched_disease["disease_id"],
            "disease_name": d_name,
            "category": category,
            "symptoms": matched_disease["symptoms"],
            "precautions": matched_disease["precautions"],
            "suggestions": suggestions,
            "citations": citations,
            "source": "local_database"
        }

    return None
