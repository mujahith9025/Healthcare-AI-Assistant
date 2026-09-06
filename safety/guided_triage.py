"""
Interactive Guided Symptom Triage Module.
Provides structured clinical risk stratification (Level 1: Emergency, Level 2: Urgent Care,
Level 3: Primary Care Consult, Level 4: Home Care & Monitoring) without diagnostic claims.
"""

from safety.emergency_check import REGIONAL_HOTLINES
from database.db_helper import TOPIC_CITATIONS

# Structured Triage Flow Configuration
TRIAGE_STEPS = {
    "categories": [
        {"id": "respiratory", "name": "🫁 Respiratory & Breathing", "desc": "Cough, congestion, sore throat, wheezing"},
        {"id": "neurological", "name": "🧠 Head & Neurological", "desc": "Headache, migraine, dizziness, lightheadedness"},
        {"id": "gastrointestinal", "name": "🥣 Digestive & Stomach", "desc": "Nausea, acidity, cramps, diarrhea, vomiting"},
        {"id": "fever_infection", "name": "🌡️ Fever & General Infection", "desc": "Body aches, chills, fatigue, sweating"},
        {"id": "dermatology", "name": "🧴 Skin, Rash & Eyes", "desc": "Itching, redness, rash, hives, eye irritation"},
        {"id": "musculoskeletal", "name": "🦴 Muscles & Joints", "desc": "Back pain, joint stiffness, sprains, soreness"},
        {"id": "general", "name": "🌿 General Wellness & Other", "desc": "Sleep issues, mild fatigue, general malaise"}
    ],
    "durations": [
        {"id": "under_24h", "label": "Less than 24 hours", "desc": "Brand new or sudden onset"},
        {"id": "1_to_3_days", "label": "1 to 3 days", "desc": "Active short-term symptoms"},
        {"id": "4_to_7_days", "label": "4 to 7 days", "desc": "Lingering almost a week"},
        {"id": "over_1_week", "label": "1 to 2 weeks", "desc": "Persistent without clear recovery"},
        {"id": "chronic", "label": "More than 2 weeks / Recurring", "desc": "Ongoing, chronic, or repeated flare-ups"}
    ],
    "severities": [
        {"id": "mild", "label": "🟢 Mild (Manageable)", "desc": "Noticeable but does not disrupt work, school, or sleep"},
        {"id": "moderate", "label": "🟡 Moderate (Disruptive)", "desc": "Limits daily activities; resting or taking frequent breaks"},
        {"id": "severe", "label": "🔴 Severe (Debilitating)", "desc": "Intense distress; unable to perform routine activities"}
    ],
    "red_flags": [
        {"id": "breathing_difficulty", "label": "Severe shortness of breath or struggling to speak in full sentences"},
        {"id": "chest_pain", "label": "Pressure, squeezing, or crushing pain in the chest or radiating to jaw/arm"},
        {"id": "confusion_stroke", "label": "Sudden confusion, facial drooping, one-sided weakness, or slurred speech"},
        {"id": "stiff_neck_fever", "label": "High fever combined with severe neck stiffness and sensitivity to light"},
        {"id": "dehydration_vomiting", "label": "Inability to keep any fluids down for >24 hours with extreme dizziness"},
        {"id": "severe_bleeding", "label": "Uncontrolled bleeding or coughing/vomiting blood"}
    ],
    "category_specific_questions": {
        "respiratory": [
            "Barking or wheezing cough",
            "Discolored thick mucus or phlegm",
            "History of asthma or allergies",
            "Chest tightness with deep breaths"
        ],
        "neurological": [
            "Throbbing pain on one side of head",
            "Nausea or sensitivity to light/sound",
            "Visual aura (flashing lights / blind spots)",
            "Tension or stiffness across forehead/scalp"
        ],
        "gastrointestinal": [
            "Burning sensation behind breastbone (acid reflux)",
            "Frequent watery stools or cramping",
            "Stomach ache shortly after meals",
            "Bloating and excessive gas"
        ],
        "fever_infection": [
            "Temperature exceeding 102°F (38.9°C)",
            "Intense body or muscle aches",
            "Swollen lymph nodes in neck or armpits",
            "Shivering or heavy night sweats"
        ],
        "dermatology": [
            "Spreading red or itchy patches",
            "Raised hives or allergic welts",
            "Flaking, peeling, or cracked dry skin",
            "Eye redness, itching, or discharge"
        ],
        "musculoskeletal": [
            "Joint swelling or warm to the touch",
            "Pain sharpens upon movement or weight-bearing",
            "Morning stiffness lasting over 30 minutes",
            "Recent physical strain, lift, or exercise"
        ],
        "general": [
            "Trouble falling or staying asleep",
            "Unexplained daytime fatigue",
            "Brain fog or difficulty concentrating",
            "Mild dehydration or dry mouth"
        ]
    }
}

def evaluate_triage(data: dict, region: str = "GLOBAL") -> dict:
    """
    Evaluates user responses from the 5-step triage flow.
    Returns structured clinical evaluation with risk level, recommended action,
    care guide, doctor checklist, and citations.
    """
    if not isinstance(data, dict):
        data = {}

    category_id = data.get("category", "general")
    duration_id = data.get("duration", "1_to_3_days")
    severity_id = data.get("severity", "mild")
    selected_red_flags = data.get("red_flags", [])
    accompanying = data.get("accompanying", [])

    # Map category display name
    cat_match = next((c for c in TRIAGE_STEPS["categories"] if c["id"] == category_id), None)
    category_name = cat_match["name"] if cat_match else "General Health"

    # Map duration label
    dur_match = next((d for d in TRIAGE_STEPS["durations"] if d["id"] == duration_id), None)
    duration_label = dur_match["label"] if dur_match else "1–3 days"

    # Map severity label
    sev_match = next((s for s in TRIAGE_STEPS["severities"] if s["id"] == severity_id), None)
    severity_label = sev_match["label"] if sev_match else "Mild"

    hotline_info = REGIONAL_HOTLINES.get(region.upper(), REGIONAL_HOTLINES["GLOBAL"])

    # Determine Triage Level
    if selected_red_flags and len(selected_red_flags) > 0:
        level = 1
        level_tag = "🔴 LEVEL 1 — IMMEDIATE EMERGENCY ATTENTION"
        level_class = "emergency-bubble"
        urgency = "Immediate Emergency Care Required"
        emergency_num = hotline_info.get('emergency', '911 / 112')
        mental_num = hotline_info.get('mental_health', '988 / 111')
        poison_num = hotline_info.get('poison', 'Local Poison Control')

        recommendation = (
            f"⚠️ **CRITICAL WARNING:** You reported one or more acute clinical red flags.\n\n"
            f"• **Immediate Action:** Contact **{emergency_num}** or proceed to the nearest Emergency Room (A&E / Casualty) right away.\n"
            f"• **Do Not Drive:** Have someone drive you or call an ambulance.\n"
            f"• **Mental Health / Crisis Support:** {mental_num}\n"
            f"• **Poison Control Helpline:** {poison_num}"
        )
        home_care = "Do not rely on home remedies. Await professional emergency evaluation."
        doctor_checklist = [
            "State your exact emergency symptoms immediately upon arrival.",
            "Bring a list of any active medications or allergies.",
            "Inform staff of when symptoms first began."
        ]

    elif severity_id == "severe" or duration_id in ["over_1_week", "chronic"]:
        level = 2
        level_tag = "🟠 LEVEL 2 — URGENT / SAME-DAY MEDICAL EVALUATION"
        level_class = "urgent-bubble"
        urgency = "Prompt Medical Attention Recommended (Within 24 Hours)"
        recommendation = (
            f"Based on your report of **{severity_label}** symptoms persisting for **{duration_label}**, "
            f"we strongly recommend consulting a physician or visiting an urgent care clinic today.\n\n"
            f"Prolonged or severe symptoms warrant clinical diagnostic testing (such as physical exam, blood work, or imaging) to prevent complications."
        )
        home_care = (
            "• Rest in a comfortable, quiet environment.\n"
            "• Stay adequately hydrated with water or electrolyte fluids.\n"
            "• Avoid strenuous physical activities until evaluated."
        )
        doctor_checklist = [
            f"Duration: Symptoms have persisted for {duration_label}.",
            f"Severity: Rated as {severity_label}.",
            "Ask: What diagnostic tests or physical examinations are indicated?",
            "Ask: What specific warning signs mean I should go to the emergency room?"
        ]

    elif severity_id == "moderate" or duration_id == "4_to_7_days":
        level = 3
        level_tag = "🟡 LEVEL 3 — ROUTINE PRIMARY CARE CLINIC VISIT"
        level_class = "routine-bubble"
        urgency = "Schedule an Appointment with Your Primary Care Doctor"
        recommendation = (
            f"Your symptoms are **{severity_label}** and have lasted **{duration_label}**. "
            f"While there are no acute emergency red flags indicated, scheduling a visit with your family doctor "
            f"or general practitioner in the next 1–3 days will help diagnose the underlying cause and guide recovery."
        )
        home_care = (
            "• Keep a symptom diary noting times of day when symptoms peak.\n"
            "• Maintain optimal hydration, light nutrition, and 7–8 hours of sleep.\n"
            "• If symptoms rapidly escalate or new red flags appear, seek urgent care."
        )
        doctor_checklist = [
            "Bring your symptom log and timeline.",
            "Mention any over-the-counter remedies you tried and their effects.",
            "Ask: What lifestyle or dietary adjustments can support healing?"
        ]

    else:
        # Level 4: Self-Care & Active Monitoring
        level = 4
        level_tag = "🟢 LEVEL 4 — HOME CARE & ACTIVE SELF-MONITORING"
        level_class = "selfcare-bubble"
        urgency = "Educational Home Care & Active Observation"
        recommendation = (
            f"Your reported symptoms appear **{severity_label}** and short-term (**{duration_label}**). "
            f"Most mild episodes improve with adequate rest, hydration, and supportive self-care. "
            f"Monitor your body closely over the next 48–72 hours."
        )
        home_care = (
            "• **Hydration & Rest:** Drink plenty of warm water, herbal teas, or broths; prioritize quality sleep.\n"
            "• **Symptom Tracking:** Note if symptoms improve or worsen day-by-day.\n"
            "• **When to Escalate:** Seek medical advice if symptoms persist beyond 5–7 days, a high fever develops, or you experience worsening pain."
        )
        doctor_checklist = [
            "Monitor body temperature twice daily if feeling warm.",
            "If symptoms do not improve within 3–5 days, book a routine consultation.",
            "Consult a pharmacist if considering over-the-counter soothing products."
        ]

    # Category Citations mapping
    category_map_citations = {
        "respiratory": TOPIC_CITATIONS.get("Respiratory", TOPIC_CITATIONS["Default"]),
        "neurological": TOPIC_CITATIONS.get("Neurological", TOPIC_CITATIONS["Default"]),
        "gastrointestinal": TOPIC_CITATIONS.get("Gastrointestinal", TOPIC_CITATIONS["Default"]),
        "fever_infection": TOPIC_CITATIONS.get("Infectious", TOPIC_CITATIONS["Default"]),
        "dermatology": TOPIC_CITATIONS.get("Dermatology", TOPIC_CITATIONS["Default"]),
        "musculoskeletal": TOPIC_CITATIONS.get("Cardiovascular", TOPIC_CITATIONS["Default"]),
        "general": TOPIC_CITATIONS.get("Default", TOPIC_CITATIONS["Default"])
    }
    citations = category_map_citations.get(category_id, TOPIC_CITATIONS["Default"])

    # Compile Structured 3-Tier ELI5 Markdown Reply
    accompanying_str = ", ".join(accompanying) if accompanying else "None reported"
    red_flag_str = ", ".join(selected_red_flags) if selected_red_flags else "None checked"

    step1_text = home_care.splitlines()[0].replace('•', '').strip() if home_care else "Rest and maintain comfortable hydration."
    step2_text = "Track your symptoms daily and note any sudden spikes in temperature or discomfort."
    step3_text = doctor_checklist[0] if doctor_checklist else "Discuss your symptom timeline with your doctor if symptoms persist."

    formatted_reply = (
        f"📊 **GUIDED SYMPTOM TRIAGE REPORT**\n\n"
        f"**{level_tag}**\n\n"
        f"**In Simple Terms (Takeaway):**\n"
        f"{recommendation}\n\n"
        f"💡 **3 Action Steps You Can Take:**\n"
        f"1. **Immediate Step:** {step1_text}\n"
        f"2. **Monitor Changes:** {step2_text}\n"
        f"3. **Doctor Checklist:** {step3_text}\n\n"
        f"<details class=\"clinical-details-dropdown\"><summary>🩺 View Doctor & Clinical Summary (Reported Inputs & Checklist)</summary>"
        f"<div class=\"clinical-details-content\">"
        f"<p style=\"margin: 0 0 6px 0;\"><strong>Area of Concern:</strong> {category_name} | <strong>Duration:</strong> {duration_label} | <strong>Severity:</strong> {severity_label}</p>"
        f"<p style=\"margin: 0 0 6px 0;\"><strong>Reported Symptoms:</strong> {accompanying_str}</p>"
        f"<p style=\"margin: 0 0 6px 0;\"><strong>Red Flags Checked:</strong> {red_flag_str}</p>"
        f"<div style=\"margin-top: 6px;\"><strong>Doctor Discussion Checklist:</strong><ul style=\"margin: 4px 0 0 16px; padding: 0;\">"
        + "".join([f"<li>{q}</li>" for q in doctor_checklist])
        + f"</ul></div>"
        f"<p style=\"font-size: 0.72rem; color: #64748b; margin-top: 8px;\">Educational Notice: This assessment is an informational triage guide and not a medical diagnosis. If you feel severely unwell, contact emergency services immediately.</p>"
        f"</div></details>"
    )

    suggestions = [
        "What questions should I ask my doctor about this?",
        "What are warning signs that require emergency care?",
        "How can I safely track my symptoms day-by-day?"
    ]

    return {
        "level": level,
        "level_tag": level_tag,
        "level_class": level_class,
        "urgency": urgency,
        "category_name": category_name,
        "duration_label": duration_label,
        "severity_label": severity_label,
        "reply": formatted_reply,
        "source": "guided_triage",
        "is_triage": True,
        "is_emergency": (level == 1),
        "citations": citations,
        "suggestions": suggestions
    }
