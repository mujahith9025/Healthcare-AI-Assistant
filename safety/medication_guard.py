"""
Medication & Drug-Interaction Safety Guard Module.
Strictly prevents the assistant from prescribing dosages, approving drug combinations,
or giving definitive pharmacological clearance without pharmacist/physician oversight.
"""

import re

# Common OTC, prescription medications, and pharmaceutical drug classes
COMMON_DRUGS = [
    "paracetamol", "acetaminophen", "tylenol",
    "ibuprofen", "advil", "motrin", "nsaids",
    "aspirin", "naproxen", "aleve",
    "amoxicillin", "antibiotic", "antibiotics", "azithromycin", "cipro",
    "metformin", "insulin", "glipizide",
    "lisinopril", "amlodipine", "losartan", "blood pressure pill",
    "atorvastatin", "statins", "cholesterol pill",
    "blood thinners", "warfarin", "eliquis", "xarelto",
    "antihistamine", "cetirizine", "zyrtec", "loratadine", "claritin", "benadryl", "diphenhydramine",
    "adderall", "xanax", "prozac", "sertraline", "antidepressant", "antidepressants",
    "steroids", "prednisone", "cortisone",
    "cough syrup", "decongestant", "pseudoephedrine", "omeprazole", "antacids",
    "alcohol", "beer", "wine"
]

INTERACTION_PATTERNS = [
    r'\bcan i take (.*?) (with|and) (.*?)\b',
    r'\btake (.*?) together\b',
    r'\bmix (.*?) with (.*?)\b',
    r'\binteraction between\b',
    r'\bdrug interaction\b',
    r'\bcombine (.*?) and\b',
    r'\bsafe to take (.*?) with\b',
    r'\bdrink alcohol while taking\b',
    r'\balcohol with (.*?)\b',
    r'\bmix alcohol and\b'
]

DOSAGE_PATTERNS = [
    r'\bhow many (mg|pills|tablets|doses|times a day)\b',
    r'\bwhat is the (dose|dosage) for\b',
    r'\bhow much (.*?) (should|can) i take\b',
    r'\bprescribe me\b',
    r'\bwhat medicine should i take\b',
    r'\bcorrect dosage of\b'
]

def check_medication_safety(query: str) -> dict | None:
    """
    Scan query for medication interaction or dosage requests.
    Returns structured safety advisory dict if medication risks are detected, else None.
    """
    if not query or not isinstance(query, str):
        return None

    normalized = query.lower()

    # Detect mentioned medications
    found_drugs = [drug for drug in COMMON_DRUGS if re.search(r'\b' + re.escape(drug) + r'\b', normalized)]

    # 1. Check for Drug-Drug / Drug-Substance Interaction queries
    is_interaction_query = any(re.search(p, normalized) for p in INTERACTION_PATTERNS) or (len(found_drugs) >= 2 and any(w in normalized for w in ["together", "with", "mix", "same time", "both"]))

    # 2. Check for Dosage / Prescription queries
    is_dosage_query = any(re.search(p, normalized) for p in DOSAGE_PATTERNS) or (len(found_drugs) >= 1 and any(w in normalized for w in ["dosage", "dose", "mg", "how many", "prescribe"]))

    if is_interaction_query or is_dosage_query:
        drugs_str = ", ".join([d.title() for d in found_drugs]) if found_drugs else "the mentioned medications"
        
        if is_interaction_query:
            advisory = (
                f"💊 **PHARMACOLOGICAL SAFETY ADVISORY — DRUG INTERACTIONS**\n\n"
                f"You asked about combining or interacting with **{drugs_str}**.\n\n"
                f"• **Critical Safety Policy:** This AI assistant is an educational tool and **cannot approve or clear medication combinations**.\n"
                f"• **Potential Interaction Risks:** Combining pharmaceuticals (such as NSAIDs, blood thinners, blood pressure agents, or sedatives) can alter therapeutic efficacy or cause severe adverse events (e.g., organ stress, bleeding, or blood pressure drops).\n"
                f"• **Action Required:** Always consult a **licensed pharmacist** or your **prescribing physician** before taking multiple medications, supplements, or over-the-counter drugs together."
            )
        else:
            advisory = (
                f"💊 **PHARMACOLOGICAL SAFETY ADVISORY — DOSAGE & PRESCRIPTION**\n\n"
                f"You asked about dosages or prescribing **{drugs_str}**.\n\n"
                f"• **Strict Non-Prescription Guard:** AI assistants are legally and clinically prohibited from calculating drug dosages, modifying regimens, or prescribing medications.\n"
                f"• **Individual Factors:** Safe drug dosages depend strictly on age, body weight, kidney/liver clearance, allergies, and individual medical history.\n"
                f"• **Action Required:** Refer to the official packaging label for general OTC instructions, or consult your **pharmacist or doctor** for personalized prescription guidance."
            )

        return {
            "reply": advisory,
            "source": "medication_guard",
            "is_medication_guard": True,
            "suggestions": [
                "What questions should I ask my pharmacist?",
                "How to read an OTC medication facts label?",
                "What are common symptoms of an allergic drug reaction?"
            ]
        }

    return None
