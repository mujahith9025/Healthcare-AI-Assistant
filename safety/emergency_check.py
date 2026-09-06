"""
Emergency and Red-Flag detection module for instant, rule-based clinical safety triage.
Includes contextual crisis hotlines by region and red-flag symptom warning detection.
"""

import re

EMERGENCY_KEYWORDS = [
    "chest pain",
    "can't breathe",
    "cant breathe",
    "cannot breathe",
    "difficulty breathing",
    "lips are turning blue",
    "blue lips",
    "heart attack",
    "cardiac arrest",
    "unconscious",
    "passed out",
    "not breathing",
    "stopped breathing",
    "severe bleeding",
    "heavy bleeding",
    "pulsing bleeding",
    "coughing up blood",
    "vomiting blood",
    "stroke",
    "facial drooping",
    "slurred speech",
    "sudden numbness",
    "suicide",
    "kill myself",
    "self harm",
    "overdose",
    "choking",
    "seizure",
    "anaphylaxis",
    "swallowed poison",
    "drain cleaner",
    "bleach",
    "poisoning",
    "swallowed bleach"
]

# Contextual Regional Hotlines
REGIONAL_HOTLINES = {
    "US": {
        "emergency": "911",
        "mental_health": "988 (Suicide & Crisis Lifeline)",
        "poison": "1-800-222-1222 (Poison Help)"
    },
    "UK": {
        "emergency": "999",
        "mental_health": "111 (NHS Mental Health Services) / 0800 689 5652",
        "poison": "111 (NHS Direct)"
    },
    "IN": {
        "emergency": "112 (National Emergency Number)",
        "ambulance": "108 (Ambulance)",
        "mental_health": "14416 / 1800-891-4416 (Tele-MANAS Crisis Helpline)",
        "poison": "1800-116-117 (National Poisons Information Centre)"
    },
    "CA": {
        "emergency": "911",
        "mental_health": "988 (Suicide Crisis Helpline)",
        "poison": "1-844-POISON-X (1-844-764-7669)"
    },
    "GLOBAL": {
        "emergency": "112 or 911",
        "mental_health": "Your national crisis or suicide prevention helpline",
        "poison": "Your local poison control center"
    }
}

# Red-flag symptoms that require urgent medical evaluation (non-emergency triage)
RED_FLAG_PATTERNS = [
    ("stiff neck with fever", "Stiff neck accompanied by fever or severe headache (possible sign of meningitis)"),
    ("stiff neck", "Neck stiffness with headache or light sensitivity"),
    ("loss of vision", "Sudden partial or complete loss of vision"),
    ("vision loss", "Sudden vision changes or loss of sight"),
    ("blood in sputum", "Blood in sputum / coughing blood (requires prompt pulmonary evaluation)"),
    ("blood in phlegm", "Blood in sputum or phlegm"),
    ("blood in stool", "Blood in stool or dark tarry stools (potential internal gastrointestinal bleeding)"),
    ("black stool", "Black tarry stools"),
    ("fever for more than 5 days", "Prolonged high fever lasting over 5 days"),
    ("fever for 5 days", "High fever lasting 5 days or more"),
    ("high fever with rash", "High fever accompanied by a rapidly spreading rash"),
    ("cannot keep fluids down", "Severe persistent vomiting / inability to retain any liquids for 24 hours"),
    ("unable to keep any water", "Severe persistent vomiting / dehydration risk"),
    ("inability to keep liquids", "Inability to stay hydrated due to persistent vomiting"),
    ("continuous vomiting", "Continuous multi-day vomiting and dehydration risk"),
    ("pain radiating to arm", "Chest or back discomfort radiating to the left arm, jaw, or neck"),
    ("pain radiating to jaw", "Pain spreading to the jaw or shoulders"),
    ("sudden weakness in arm", "Sudden one-sided weakness, clumsiness, or numbness in limbs"),
    ("difficulty swallowing", "Sudden difficulty swallowing or breathing obstruction"),
    ("calf pain", "Unilateral calf pain with warmth, swelling, or redness (possible DVT clot)"),
    ("worst headache of my life", "Thunderclap sudden severe headache (possible subarachnoid hemorrhage)"),
    ("worst headache", "Severe sudden thunderclap headache")
]

EMERGENCY_RESPONSE = (
    "🚨 **EMERGENCY NOTICE**: If you or someone near you is experiencing a medical emergency, "
    "please call your local emergency hotline (e.g., 911, 112, 999) or go to the nearest emergency room immediately. "
    "This AI assistant is an educational tool only and cannot provide emergency medical assistance."
)

def is_emergency(query: str) -> bool:
    """Check if the query contains critical life-threatening emergency phrases."""
    if not query or not isinstance(query, str):
        return False

    normalized_query = query.lower()

    # Exclude non-emergency references like 'food poisoning' unless accompanied by severe emergency markers
    if "food poisoning" in normalized_query and not any(k in normalized_query for k in ["unconscious", "not breathing", "stopped breathing", "severe bleeding"]):
        return False

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in normalized_query:
            return True

    return False

def get_contextual_emergency_response(query: str, region: str = "GLOBAL") -> str:
    """Generate a localized emergency response with region-specific crisis hotlines."""
    region_key = region.upper() if region and region.upper() in REGIONAL_HOTLINES else "GLOBAL"
    info = REGIONAL_HOTLINES[region_key]
    normalized_query = query.lower() if query else ""

    is_mental_health = any(k in normalized_query for k in ["suicide", "kill myself", "self harm"])
    is_poison = any(k in normalized_query for k in ["poison", "overdose", "swallowed poison", "bleach", "drain cleaner"])

    lines = [
        "🚨 **IMMEDIATE EMERGENCY ALERT**",
        "",
        "If you or someone near you is experiencing a medical or life-threatening crisis, please seek immediate help:",
        f"• **Emergency Services:** Call **{info['emergency']}** or visit the nearest Emergency Room right away."
    ]

    if is_mental_health and "mental_health" in info:
        lines.append(f"• **Crisis / Suicide Lifeline:** Call or text **{info['mental_health']}** for immediate, confidential 24/7 support.")

    if is_poison and "poison" in info:
        lines.append(f"• **Poison Control Center:** Call **{info['poison']}**.")

    if region_key == "IN" and "ambulance" in info:
        lines.append(f"• **Ambulance Service:** Dial **{info['ambulance']}**.")

    lines.append("")
    lines.append("*⚠️ Note: This AI assistant cannot diagnose, triage, or provide emergency care. Do not delay professional medical attention.*")

    return "\n".join(lines)

def detect_red_flags(query: str) -> list:
    """
    Detect warning symptoms that warrant prompt physician evaluation.
    Returns a list of matched red flag descriptions.
    """
    if not query or not isinstance(query, str):
        return []

    normalized_query = query.lower()
    detected = []

    for pattern, description in RED_FLAG_PATTERNS:
        if pattern in normalized_query:
            if description not in detected:
                detected.append(description)

    # Flexible pattern checks (e.g. neck is extremely stiff)
    if re.search(r'\b(neck\s+(is\s+)?(extremely\s+)?stiff|stiff\s+neck)\b', normalized_query):
        desc = "Stiff neck accompanied by fever or severe headache (possible sign of meningitis)"
        if desc not in detected:
            detected.append(desc)

    return detected

def format_red_flag_note(flags: list) -> str:
    """Format detected red-flag symptoms into a prominent clinical warning note."""
    if not flags:
        return ""

    flag_bullets = "\n".join([f"  • {f}" for f in flags])
    return (
        f"\n\n🚩 **CLINICAL RED-FLAG NOTICE**:\n"
        f"You mentioned symptom(s) that require prompt in-person medical evaluation:\n"
        f"{flag_bullets}\n"
        f"*Please schedule an urgent appointment with a healthcare provider or visit an urgent care clinic.*"
    )
