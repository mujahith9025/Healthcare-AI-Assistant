"""
Clinically Validated Mental Health & Somatic Toolkits Engine.
Provides evidence-based psychometric assessment scales, somatic vagal regulation protocols,
and Stanley-Brown suicide safety planning interventions:

1. Clinical Psychometric Scales:
   - PHQ-9 (Patient Health Questionnaire 9 - Depression Severity with Suicide Gate)
   - GAD-7 (Generalized Anxiety Disorder 7-item Scale)
   - PC-PTSD-5 (Primary Care PTSD Screen for DSM-5)
   - ISI (Insomnia Severity Index - 7 items)
   - PSS-4 (Perceived Stress Scale 4-item Screener)
   - CAGE-AID (Substance & Alcohol Use Screener)

2. Somatic & Vagus Nerve Regulation Protocols:
   - Box Breathing (Square Breathing 4-4-4-4)
   - 4-7-8 Relaxing Breath (Dr. Andrew Weil Parasympathetic Pacer)
   - Physiological Sigh (Stanford Neurobiology / Dr. Huberman)
   - 5-4-3-2-1 Sensory Grounding Protocol
   - Progressive Muscle Relaxation (Jacobson PMR)
   - Bilateral Stimulation / Alternating Tapping Pacer
   - Autogenic Somatic Training Protocol

3. Stanley-Brown Safety Planning Intervention (Suicide Risk Reduction)
"""

from typing import Dict, Any, List, Optional
import re


# =============================================================================
# 1. Clinical Assessment Scales
# =============================================================================

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way"
]

def evaluate_phq9(answers: List[int]) -> Dict[str, Any]:
    """
    Evaluates PHQ-9 Depression Severity Scale (0 to 27).
    Answers: list of 9 integers (0 = Not at all, 1 = Several days, 2 = More than half the days, 3 = Nearly every day).
    Strict suicide safety gate enforced if Question 9 > 0.
    """
    if not answers or len(answers) != 9:
        answers = [0] * 9
    clean = [max(0, min(3, int(a))) for a in answers]
    score = sum(clean)

    # Suicide safety trigger on Question 9 (self-harm or death thoughts)
    has_suicide_flag = clean[8] > 0

    if score <= 4:
        tier = "MINIMAL"
        tier_label = "🟢 None-Minimal Depression (0–4)"
        clinical_action = "Depressive symptoms absent or minimal. Support general wellness and stress resilience."
    elif score <= 9:
        tier = "MILD"
        tier_label = "🟡 Mild Depression (5–9)"
        clinical_action = "Watchful waiting, psychoeducation, exercise, sleep hygiene, and somatic regulation. Re-evaluate in 4–6 weeks."
    elif score <= 14:
        tier = "MODERATE"
        tier_label = "🟠 Moderate Depression (10–14)"
        clinical_action = "Consider evidence-based psychotherapy (CBT / IPT) or first-line pharmacotherapy. Comprehensive clinical evaluation indicated."
    elif score <= 19:
        tier = "MODERATELY_SEVERE"
        tier_label = "🔴 Moderately Severe Depression (15–19)"
        clinical_action = "Active treatment with combination psychotherapy and antidepressant pharmacotherapy strongly recommended. Mental health specialist referral."
    else:
        tier = "SEVERE"
        tier_label = "🔴 Severe Depression (20–27)"
        clinical_action = "Immediate psychiatric evaluation and active multimodal treatment required. Assess functional impairment and continuous safety."

    safety_alert = ""
    if has_suicide_flag:
        safety_alert = (
            "🚨 CRITICAL CRISIS ALERT: Positive endorsement on Question 9 (thoughts of death or self-harm). "
            "Immediate suicide risk assessment required. National Suicide & Crisis Lifeline: Call or text 988 (USA/Canada), "
            "111 (UK), 112 (EU/India), or text HOME to 741741 (Crisis Text Line)."
        )

    return {
        "scale_id": "phq9",
        "scale_title": "PHQ-9 Depression Severity Scale",
        "score": score,
        "max_score": 27,
        "score_unit": "points",
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "has_suicide_flag": has_suicide_flag,
        "safety_alert": safety_alert,
        "answers": clean,
        "citations": "Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med 2001; 16:606-613"
    }


GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen"
]

def evaluate_gad7(answers: List[int]) -> Dict[str, Any]:
    """
    Evaluates GAD-7 Generalized Anxiety Disorder Scale (0 to 21).
    Answers: list of 7 integers (0 = Not at all, 1 = Several days, 2 = More than half the days, 3 = Nearly every day).
    """
    if not answers or len(answers) != 7:
        answers = [0] * 7
    clean = [max(0, min(3, int(a))) for a in answers]
    score = sum(clean)

    if score <= 4:
        tier = "MINIMAL"
        tier_label = "🟢 Minimal Anxiety (0–4)"
        clinical_action = "Anxiety symptoms minimal. Practice routine autonomic balance, mindfulness, and somatic box breathing."
    elif score <= 9:
        tier = "MILD"
        tier_label = "🟡 Mild Anxiety (5–9)"
        clinical_action = "Watchful waiting, mindfulness-based stress reduction (MBSR), physiological sighs, and sleep hygiene."
    elif score <= 14:
        tier = "MODERATE"
        tier_label = "🟠 Moderate Anxiety (10–14)"
        clinical_action = "Probable Generalized Anxiety Disorder. Consider Cognitive Behavioral Therapy (CBT) and/or SSRI/SNRI medical consultation."
    else:
        tier = "SEVERE"
        tier_label = "🔴 Severe Anxiety (15–21)"
        clinical_action = "Active multimodal treatment indicated with psychological intervention and pharmacotherapy. Rule out comorbid panic disorder or depression."

    return {
        "scale_id": "gad7",
        "scale_title": "GAD-7 Generalized Anxiety Disorder Scale",
        "score": score,
        "max_score": 21,
        "score_unit": "points",
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "answers": clean,
        "citations": "Spitzer RL, Kroenke K, Williams JB, Löwe B. A brief measure for assessing generalized anxiety disorder: the GAD-7. Arch Intern Med 2006; 166:1092-1097"
    }


PC_PTSD5_QUESTIONS = [
    "Had nightmares about the event(s) or thought about the event(s) when you did not want to?",
    "Tried hard not to think about the event(s) or went out of your way to avoid situations that reminded you of the event(s)?",
    "Been constantly on guard, watchful, or easily startled?",
    "Felt numb or detached from people, activities, or your surroundings?",
    "Felt guilty or unable to stop blaming yourself or others for the event(s) or any problems the event(s) may have caused?"
]

def evaluate_pc_ptsd5(answers: List[bool]) -> Dict[str, Any]:
    """
    Evaluates Primary Care PTSD Screen for DSM-5 (PC-PTSD-5).
    Answers: list of 5 booleans (True = Yes, False = No).
    Clinical cutoff: score >= 3 indicates positive screen requiring comprehensive PTSD clinical assessment.
    """
    if not answers or len(answers) != 5:
        answers = [False] * 5
    clean = [bool(a) for a in answers]
    score = sum(1 for a in clean if a)

    is_positive = score >= 3
    if is_positive:
        tier = "POSITIVE_SCREEN"
        tier_label = f"🔴 Positive PTSD Screen (Score {score}/5 ≥ 3)"
        clinical_action = "Positive screen for Post-Traumatic Stress Disorder. Comprehensive diagnostic evaluation by a licensed mental health professional recommended (CAPS-5 or PCL-5). Consider trauma-focused therapies (EMDR, CPT, PE)."
    else:
        tier = "NEGATIVE_SCREEN"
        tier_label = f"🟢 Negative PTSD Screen (Score {score}/5 < 3)"
        clinical_action = "Screening is below the diagnostic threshold for PTSD. Continue somatic grounding and supportive stress resilience practices."

    return {
        "scale_id": "pc_ptsd5",
        "scale_title": "PC-PTSD-5 Primary Care PTSD Screen",
        "score": score,
        "max_score": 5,
        "score_unit": "points",
        "is_positive": is_positive,
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "citations": "Prins A, et al. The Primary Care PTSD Screen for DSM-5 (PC-PTSD-5): Development and Evaluation Within a Veteran Primary Care Sample. J Gen Intern Med 2016; 31:1206-1211"
    }


ISI_QUESTIONS = [
    "Difficulty falling asleep",
    "Difficulty staying asleep",
    "Problems waking up too early",
    "How SATISFIED/DISSATISFIED are you with your CURRENT sleep pattern?",
    "How NOTICEABLE to others do you think your sleep problem is in terms of impairing the quality of your life?",
    "How WORRIED/DISTRESSED are you about your current sleep problem?",
    "To what extent do you consider your sleep problem to INTERFERE with your daily functioning (e.g. fatigue, concentration, memory, mood)?"
]

def evaluate_isi(answers: List[int]) -> Dict[str, Any]:
    """
    Evaluates Insomnia Severity Index (ISI, 0 to 28).
    Answers: list of 7 integers (0 to 4).
    """
    if not answers or len(answers) != 7:
        answers = [0] * 7
    clean = [max(0, min(4, int(a))) for a in answers]
    score = sum(clean)

    if score <= 7:
        tier = "NO_INSOMNIA"
        tier_label = "🟢 No Clinically Significant Insomnia (0–7)"
        clinical_action = "Sleep parameters are within normal healthy thresholds. Maintain consistent circadian sleep-wake schedule."
    elif score <= 14:
        tier = "SUBTHRESHOLD"
        tier_label = "🟡 Subthreshold / Mild Insomnia (8–14)"
        clinical_action = "Subthreshold insomnia. Emphasize Sleep Hygiene rules, 4-7-8 relaxing breath before bed, avoid screens 60 min before sleep, and limit caffeine past 12 PM."
    elif score <= 21:
        tier = "MODERATE"
        tier_label = "🟠 Clinical Insomnia — Moderate Severity (15–21)"
        clinical_action = "Moderate clinical insomnia. First-line evidence-based recommendation: Cognitive Behavioral Therapy for Insomnia (CBT-I: sleep restriction, stimulus control). Consult physician."
    else:
        tier = "SEVERE"
        tier_label = "🔴 Clinical Insomnia — Severe (22–28)"
        clinical_action = "Severe clinical insomnia. Medical and behavioral sleep medicine evaluation required to screen for primary sleep disorders (Sleep Apnea, Restless Legs Syndrome) and initiate structured CBT-I."

    return {
        "scale_id": "isi",
        "scale_title": "Insomnia Severity Index (ISI)",
        "score": score,
        "max_score": 28,
        "score_unit": "points",
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "citations": "Morin CM, Belleville G, Bélanger L, Ivers H. The Insomnia Severity Index: psychometric indicators to detect insomnia cases and evaluate treatment response. Sleep 2011; 34:601-608"
    }


PSS4_QUESTIONS = [
    "In the last month, how often have you felt that you were unable to control the important things in your life?",
    "In the last month, how often have you felt confident about your ability to handle your personal problems? (Reverse Scored)",
    "In the last month, how often have you felt that things were going your way? (Reverse Scored)",
    "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?"
]

def evaluate_pss4(answers: List[int]) -> Dict[str, Any]:
    """
    Evaluates Perceived Stress Scale 4-item (PSS-4, 0 to 16).
    Answers: list of 4 integers (0 = Never, 1 = Almost Never, 2 = Sometimes, 3 = Fairly Often, 4 = Very Often).
    Questions 2 and 3 are reverse scored: 0->4, 1->3, 2->2, 3->1, 4->0.
    """
    if not answers or len(answers) != 4:
        answers = [0] * 4
    clean = [max(0, min(4, int(a))) for a in answers]
    
    # Reverse score questions 2 and 3 (0-indexed: indices 1 and 2)
    q0 = clean[0]
    q1 = 4 - clean[1]
    q2 = 4 - clean[2]
    q3 = clean[3]
    score = q0 + q1 + q2 + q3

    if score <= 5:
        tier = "LOW"
        tier_label = "🟢 Low Perceived Stress (0–5)"
        clinical_action = "Perceived stress is well managed. Continue protective daily wellness routines."
    elif score <= 8:
        tier = "MODERATE"
        tier_label = "🟡 Moderate Perceived Stress (6–8)"
        clinical_action = "Moderate stress burden. Incorporate daily 5-minute somatic Box Breathing, structured boundary setting, and regular aerobic activity."
    else:
        tier = "HIGH"
        tier_label = "🔴 High Perceived Stress (9–16)"
        clinical_action = "Substantial stress overload. Recommended: Structured stress reduction program (MBSR), workload audit, progressive muscle relaxation, and counseling support."

    return {
        "scale_id": "pss4",
        "scale_title": "Perceived Stress Scale (PSS-4)",
        "score": score,
        "max_score": 16,
        "score_unit": "points",
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "citations": "Cohen S, Kamarck T, Mermelstein R. A global measure of perceived stress. J Health Soc Behav 1983; 24:385-396"
    }


CAGE_AID_QUESTIONS = [
    "Have you ever felt you ought to CUT DOWN on your drinking or drug use?",
    "Have people ANNOYED you by criticizing your drinking or drug use?",
    "Have you ever felt bad or GUILTY about your drinking or drug use?",
    "Have you ever had a drink or used drugs first thing in the morning to steady your nerves or get rid of a hangover (EYE-OPENER)?"
]

def evaluate_cage_aid(answers: List[bool]) -> Dict[str, Any]:
    """
    Evaluates CAGE-AID (CAGE Adapted to Include Drugs).
    Answers: list of 4 booleans.
    Score >= 2 is clinically significant and warrants comprehensive addiction evaluation.
    """
    if not answers or len(answers) != 4:
        answers = [False] * 4
    clean = [bool(a) for a in answers]
    score = sum(1 for a in clean if a)

    is_positive = score >= 2
    if is_positive:
        tier = "POSITIVE_SCREEN"
        tier_label = f"🔴 Positive Substance Screen (Score {score}/4 ≥ 2)"
        clinical_action = "Clinically significant screen for substance or alcohol misuse. Professional addiction screening and physician consultation strongly recommended. SAMHSA National Helpline: 1-800-662-4357 (Free, confidential 24/7 treatment referral)."
    elif score == 1:
        tier = "BORDERLINE"
        tier_label = "🟡 Borderline / At-Risk Use (Score 1/4)"
        clinical_action = "Borderline result. Monitor consumption frequency, reflect on triggers, and consider brief primary care discussion."
    else:
        tier = "NEGATIVE_SCREEN"
        tier_label = "🟢 Negative Screen (Score 0/4)"
        clinical_action = "No current evidence of hazardous substance use patterns."

    return {
        "scale_id": "cage_aid",
        "scale_title": "CAGE-AID Substance Screening Tool",
        "score": score,
        "max_score": 4,
        "score_unit": "points",
        "is_positive": is_positive,
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": clinical_action,
        "citations": "Brown RL, Rounds LA. Conjoint screening questionnaires for alcohol and other drug abuse: criterion validity in a primary care practice. WMJ 1995; 94:135-140"
    }


# =============================================================================
# 2. Somatic & Vagus Regulation Protocols
# =============================================================================

SOMATIC_PROTOCOLS = {
    "box_breathing": {
        "id": "box_breathing",
        "title": "Box Breathing (4-4-4-4 Square Pacer)",
        "category": "vagal_pacing",
        "icon": "⏹️",
        "badge": "Navy SEALs / Autonomic Balance",
        "summary": "Equalized 4-phase breathing cycle to stabilize heart rate variability (HRV), decrease amygdala reactivity, and restore autonomic equilibrium.",
        "duration_minutes": 5,
        "phases": [
            {"name": "Inhale", "duration": 4, "instruction": "Slow, deep diaphragmatic inhalation through the nose", "lung_state": "expand"},
            {"name": "Hold", "duration": 4, "instruction": "Gently hold breath with lungs full without straining", "lung_state": "hold_full"},
            {"name": "Exhale", "duration": 4, "instruction": "Smooth, complete exhalation through the mouth or nose", "lung_state": "contract"},
            {"name": "Hold", "duration": 4, "instruction": "Rest quietly with lungs empty before the next breath", "lung_state": "hold_empty"}
        ],
        "vagal_mechanism": "Rhythmic square pacing equalizes baroreceptor firing, increases high-frequency HRV, and balances sympathetic-parasympathetic tone.",
        "best_for": ["High acute stress", "Focus and mental clarity", "Pre-performance anxiety", "Emotional regulation"]
    },
    "relaxing_478": {
        "id": "relaxing_478",
        "title": "4-7-8 Parasympathetic Relaxing Breath",
        "category": "vagal_pacing",
        "icon": "🌊",
        "badge": "Dr. Andrew Weil / Vagal Brake",
        "summary": "Extended exhalation protocol that stimulates the vagus nerve, rapidly lowers resting heart rate, and promotes deep physical relaxation.",
        "duration_minutes": 4,
        "phases": [
            {"name": "Inhale", "duration": 4, "instruction": "Quietly inhale through the nose to a count of 4", "lung_state": "expand"},
            {"name": "Hold", "duration": 7, "instruction": "Hold your breath comfortably for 7 seconds", "lung_state": "hold_full"},
            {"name": "Exhale", "duration": 8, "instruction": "Make a whooshing sound as you exhale completely through mouth for 8 seconds", "lung_state": "contract"}
        ],
        "vagal_mechanism": "Prolonged exhalation relative to inhalation engages the vagus nerve brake on the sinoatrial node, triggering acetylcholine release and cardiac deceleration.",
        "best_for": ["Panic surges", "Bedtime insomnia", "Anger/agitation de-escalation", "Acute tension headaches"]
    },
    "physiological_sigh": {
        "id": "physiological_sigh",
        "title": "Physiological Sigh (Rapid Autonomic Reset)",
        "category": "vagal_pacing",
        "icon": "🫁",
        "badge": "Stanford Neurobiology / Dr. Huberman",
        "summary": "Two consecutive inhales followed by a prolonged exhale. The fastest scientifically proven real-time tool to down-regulate autonomic arousal in 1–3 breaths.",
        "duration_minutes": 3,
        "phases": [
            {"name": "Deep Inhale", "duration": 2.5, "instruction": "Deep inhalation through the nose filling 80% of lungs", "lung_state": "expand_partial"},
            {"name": "Top-Off Inhale", "duration": 1.0, "instruction": "Sharp second inhale to completely inflate collapsed alveoli", "lung_state": "expand_full"},
            {"name": "Long Exhale", "duration": 6.5, "instruction": "Slow, relaxed sigh all the way out through open mouth", "lung_state": "contract"}
        ],
        "vagal_mechanism": "The second micro-inhale pops open collapsed pulmonary alveoli, optimizing carbon dioxide offloading and activating parasympathetic vagal afferents.",
        "best_for": ["Instant panic/hyperventilation relief", "Acute shock/hyperarousal", "Post-argument calming", "Rapid reset between tasks"]
    },
    "grounding_54321": {
        "id": "grounding_54321",
        "title": "5-4-3-2-1 Somatosensory Grounding",
        "category": "sensory_grounding",
        "icon": "👁️",
        "badge": "Trauma-Informed CBT",
        "summary": "Step-by-step sensory orientation technique to anchor awareness into the physical environment and interrupt dissociation, flashbacks, and panic spirals.",
        "duration_minutes": 5,
        "steps": [
            {"step_num": 5, "sense": "Sight", "count": 5, "instruction": "Acknowledge 5 things you can SEE around you (e.g. a shadow, a pen, texture on the wall).", "icon": "👁️"},
            {"step_num": 4, "sense": "Touch", "count": 4, "instruction": "Acknowledge 4 things you can physically FEEL (e.g. feet on the floor, fabric of your shirt, cool air on skin).", "icon": "✋"},
            {"step_num": 3, "sense": "Hearing", "count": 3, "instruction": "Acknowledge 3 distinct sounds you can HEAR (e.g. traffic, computer hum, distant bird, own breath).", "icon": "👂"},
            {"step_num": 2, "sense": "Smell", "count": 2, "instruction": "Acknowledge 2 things you can SMELL (e.g. coffee, fresh air, hand soap, or imagine calming lavender).", "icon": "👃"},
            {"step_num": 1, "sense": "Taste", "count": 1, "instruction": "Acknowledge 1 thing you can TASTE (e.g. mint, water, lingering coffee, or focus on inside of mouth).", "icon": "👅"}
        ],
        "vagal_mechanism": "Directs cortical attention away from threat-focused limbic networks and re-engages the prefrontal cortex via external sensory pathways.",
        "best_for": ["Dissociation / derealization", "PTSD flashbacks", "Severe panic attacks", "Sensory overload"]
    },
    "pmr_jacobson": {
        "id": "pmr_jacobson",
        "title": "Progressive Muscle Relaxation (PMR)",
        "category": "somatic_release",
        "icon": "💪",
        "badge": "Jacobson Clinical PMR",
        "summary": "Systematic isometric tension followed by sudden conscious somatic release through 8 major muscle groups to dissolve chronic physical muscle armoring.",
        "duration_minutes": 10,
        "muscle_zones": [
            {"zone": "Hands & Forearms", "tension_seconds": 5, "release_seconds": 10, "action": "Clench both fists tightly like squeezing a lemon, feel tension in forearms, then abruptly release and feel warmth."},
            {"zone": "Biceps & Upper Arms", "tension_seconds": 5, "release_seconds": 10, "action": "Bend elbows and tense biceps as hard as possible, hold, then let arms fall limp to your sides."},
            {"zone": "Forehead & Brow", "tension_seconds": 5, "release_seconds": 10, "action": "Raise eyebrows high wrinkling forehead, squeeze eyes shut, hold, then completely smooth out facial muscles."},
            {"zone": "Jaw & Cheeks", "tension_seconds": 5, "release_seconds": 10, "action": "Clench teeth gently and pull corners of mouth back, hold, then release jaw letting mouth fall slightly open."},
            {"zone": "Shoulders & Neck", "tension_seconds": 5, "release_seconds": 10, "action": "Shrug shoulders high up toward your ears, feel the tightness, then drop them heavily and feel relief."},
            {"zone": "Chest & Abdomen", "tension_seconds": 5, "release_seconds": 10, "action": "Take a deep breath and tighten stomach muscles hard like preparing for a punch, hold, then exhale and soften belly."},
            {"zone": "Thighs & Glutes", "tension_seconds": 5, "release_seconds": 10, "action": "Squeeze thigh muscles and press heels into the floor, hold, then release all tension in upper legs."},
            {"zone": "Calves & Feet", "tension_seconds": 5, "release_seconds": 10, "action": "Point toes upward toward your shins, flexing calf muscles, hold, then release and feel tingling relaxation."}
        ],
        "vagal_mechanism": "Neuromuscular feedback loops recalibrate Golgi tendon organs and down-regulate sympathetic gamma-motoneuron discharge.",
        "best_for": ["Somatic tension & jaw clenching", "Chronic stress holding patterns", "Fibromyalgia / tension aches", "Insomnia"]
    },
    "bilateral_tapping": {
        "id": "bilateral_tapping",
        "title": "Bilateral Stimulation & Butterfly Hug Pacer",
        "category": "somatic_release",
        "icon": "🦋",
        "badge": "EMDR Somatic Protocol",
        "summary": "Alternating left-right tactile or visual rhythmic pulse (1.0–1.2 Hz) to stimulate interhemispheric communication and down-regulate distress during acute emotional overwhelm.",
        "duration_minutes": 5,
        "cadence_hz": 1.1,
        "instructions": [
            "Cross your arms over your chest so your hands rest on opposite shoulders/clavicles (The Butterfly Hug).",
            "Slowly alternate tapping left hand, then right hand, in rhythm with the visual/audio pacer.",
            "Take slow, gentle breaths while noticing distressing emotions without trying to change them, allowing them to pass like clouds."
        ],
        "vagal_mechanism": "Alternating bilateral stimulation facilitates working memory taxing, decreases amygdala hyperarousal, and promotes adaptive memory reprocessing.",
        "best_for": ["Traumatic distress spikes", "Intense grief / crying spells", "Phobic avoidance", "Emotional overwhelm"]
    },
    "autogenic_training": {
        "id": "autogenic_training",
        "title": "Autogenic Somatic Training (Schultz)",
        "category": "somatic_release",
        "icon": "☀️",
        "badge": "Psychosomatic Medicine",
        "summary": "Self-directed somatosensory formulas focusing on somatic heaviness and warmth to induce peripheral vasodilation and autonomic parasympathetic dominance.",
        "duration_minutes": 6,
        "verbal_formulas": [
            "My right arm is heavy and warm... My left arm is heavy and warm...",
            "My arms and legs are delightfully heavy and warm...",
            "My heartbeat is calm and regular... My breathing is calm and effortless...",
            "My solar plexus is warm... My forehead is pleasantly cool..."
        ],
        "vagal_mechanism": "Biofeedback conditioning drives sympathetic withdrawal and peripheral arteriolar vasodilation, increasing skin temperature by 1–3°C.",
        "best_for": ["Hypertension stress spikes", "Raynaud's / cold extremities", "Chronic tension", "General relaxation"]
    }
}


# =============================================================================
# 3. Stanley-Brown Crisis Safety Plan Generator
# =============================================================================

def generate_stanley_brown_safety_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and structures an evidence-based Stanley-Brown Safety Planning Intervention.
    Steps:
    1. Personal Warning Signs (triggers, thoughts, physical sensations)
    2. Internal Coping Strategies (activities done alone without contacting others)
    3. People & Social Settings that Provide Distraction
    4. Trusted Friends / Family to Ask for Help
    5. Healthcare Professionals & Crisis Agencies (with hotlines)
    6. Making the Environment Safe (securing medications, lethal means)
    """
    data = plan_data or {}
    
    warning_signs = [str(w).strip() for w in data.get("warning_signs", []) if str(w).strip()]
    coping_strategies = [str(c).strip() for c in data.get("coping_strategies", []) if str(c).strip()]
    social_distractions = [str(s).strip() for s in data.get("social_distractions", []) if str(s).strip()]
    trusted_contacts = [str(t).strip() for t in data.get("trusted_contacts", []) if str(t).strip()]
    professionals = [str(p).strip() for p in data.get("professionals", []) if str(p).strip()]
    environment_safety = [str(e).strip() for e in data.get("environment_safety", []) if str(e).strip()]

    # Standard emergency hotlines always included
    crisis_hotlines = [
        {"name": "National Suicide & Crisis Lifeline (US/CA)", "contact": "Call or Text 988 (Available 24/7, Free, Confidential)"},
        {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
        {"name": "NHS Mental Health Services (UK)", "contact": "Call 111 (Option 2 for mental health crisis) or 999"},
        {"name": "National Emergency Number (India)", "contact": "Call 112 or Tele-MANAS: 14416 (24/7 toll-free)"},
        {"name": "Trevor Project (LGBTQ+ Crisis)", "contact": "Call 1-866-488-7386 or Text START to 678-678"},
        {"name": "Veterans Crisis Line", "contact": "Dial 988 then press 1, or text 838255"}
    ]

    is_complete = bool(warning_signs and coping_strategies and (trusted_contacts or professionals))

    return {
        "success": True,
        "is_complete": is_complete,
        "plan": {
            "step1_warning_signs": warning_signs or ["Feeling isolated", "Racing heart", "Negative self-talk"],
            "step2_internal_coping": coping_strategies or ["Box Breathing 4-4-4-4", "5-4-3-2-1 Sensory Grounding", "Going for a walk outside"],
            "step3_social_distractions": social_distractions or ["Visiting a coffee shop", "Calling a friend to talk about sports", "Listening to favorite music"],
            "step4_trusted_contacts": trusted_contacts or ["Family member / close friend"],
            "step5_professionals": professionals or ["Primary Care Physician", "Therapist / Counselor"],
            "step5_emergency_hotlines": crisis_hotlines,
            "step6_environment_safety": environment_safety or ["Store medications safely", "Remove or lock away dangerous items", "Stay with a supportive person"]
        },
        "citations": "Stanley B, Brown GK. Safety Planning Intervention: A brief intervention to mitigate suicide risk. Cogn Behav Pract 2012; 19:256-264"
    }


# =============================================================================
# 4. Catalog Registry & Dispatcher
# =============================================================================

def get_mental_health_catalog() -> Dict[str, Any]:
    """Returns complete catalog of clinical scales, somatic exercises, and crisis hotlines."""
    scales = {
        "phq9": {
            "id": "phq9",
            "title": "PHQ-9 Depression Severity Scale",
            "badge": "DSM-5 Validated",
            "items_count": 9,
            "questions": PHQ9_QUESTIONS,
            "description": "Standard clinical screening questionnaire for depression with mandatory suicide safety monitoring."
        },
        "gad7": {
            "id": "gad7",
            "title": "GAD-7 Generalized Anxiety Scale",
            "badge": "Anxiety Screener",
            "items_count": 7,
            "questions": GAD7_QUESTIONS,
            "description": "7-item validated screener to assess generalized anxiety and panic severity."
        },
        "pc_ptsd5": {
            "id": "pc_ptsd5",
            "title": "PC-PTSD-5 Primary Care PTSD Screen",
            "badge": "Trauma Screen",
            "items_count": 5,
            "questions": PC_PTSD5_QUESTIONS,
            "description": "5-item DSM-5 primary care screening tool to evaluate post-traumatic stress symptoms."
        },
        "isi": {
            "id": "isi",
            "title": "Insomnia Severity Index (ISI)",
            "badge": "Sleep Medicine",
            "items_count": 7,
            "questions": ISI_QUESTIONS,
            "description": "7-item measure assessing sleep maintenance, onset difficulty, and daytime fatigue."
        },
        "pss4": {
            "id": "pss4",
            "title": "Perceived Stress Scale (PSS-4)",
            "badge": "Stress Metric",
            "items_count": 4,
            "questions": PSS4_QUESTIONS,
            "description": "Brief 4-item global metric for perceived life stress and coping efficacy."
        },
        "cage_aid": {
            "id": "cage_aid",
            "title": "CAGE-AID Substance Screener",
            "badge": "Addiction Screening",
            "items_count": 4,
            "questions": CAGE_AID_QUESTIONS,
            "description": "Evidence-based 4-item screener for alcohol and substance use concerns."
        }
    }

    return {
        "success": True,
        "scales": scales,
        "somatic_protocols": SOMATIC_PROTOCOLS,
        "categories": {
            "somatic_pacers": {"title": "🫁 Somatic Breathing Pacers", "count": 3},
            "clinical_scales": {"title": "🧠 Clinical Assessment Scales", "count": 6},
            "grounding_pmr": {"title": "🧘 Grounding & Somatic Release", "count": 4},
            "crisis_safety": {"title": "🛡️ Crisis Safety Plan", "count": 1}
        }
    }


def evaluate_mental_health_assessment(scale_id: str, answers: Any) -> Dict[str, Any]:
    """Universal dispatcher for evaluating psychological screening scales."""
    sid = str(scale_id).lower().strip()
    
    try:
        if sid == "phq9":
            res = evaluate_phq9(answers)
        elif sid == "gad7":
            res = evaluate_gad7(answers)
        elif sid in ["pc_ptsd5", "ptsd"]:
            res = evaluate_pc_ptsd5(answers)
        elif sid == "isi":
            res = evaluate_isi(answers)
        elif sid == "pss4":
            res = evaluate_pss4(answers)
        elif sid == "cage_aid":
            res = evaluate_cage_aid(answers)
        else:
            return {"success": False, "error": f"Unknown scale ID '{scale_id}'"}

        # Cross-recommend matching somatic interventions based on scale outcome
        recommended_somatic = []
        if sid in ["gad7", "pss4"]:
            recommended_somatic = ["box_breathing", "physiological_sigh", "grounding_54321"]
        elif sid == "isi":
            recommended_somatic = ["relaxing_478", "pmr_jacobson", "autogenic_training"]
        elif sid == "pc_ptsd5":
            recommended_somatic = ["grounding_54321", "bilateral_tapping", "box_breathing"]
        elif sid == "phq9":
            recommended_somatic = ["physiological_sigh", "grounding_54321", "pmr_jacobson"]

        res["success"] = True
        res["recommended_somatic_protocols"] = [SOMATIC_PROTOCOLS[pid] for pid in recommended_somatic if pid in SOMATIC_PROTOCOLS]
        return res

    except Exception as e:
        return {"success": False, "error": f"Evaluation error: {str(e)}"}


def detect_mental_health_intent(text: str) -> Optional[Dict[str, Any]]:
    """
    Detects user intent for mental health scales, somatic breathing exercises, panic grounding, or safety planning.
    """
    if not text:
        return None
    lower = text.lower()

    # Crisis / Safety Plan
    if re.search(r'\b(safety plan|stanley brown|suicide plan|crisis plan|self harm plan|safety planning)\b', lower):
        return {"type": "safety_plan", "title": "Stanley-Brown Crisis Safety Plan", "icon": "🛡️"}

    # Somatic Breathing Pacers
    if re.search(r'\b(box breath|square breath|box breathing|4-4-4-4|breathe box)\b', lower):
        return {"type": "somatic", "protocol_id": "box_breathing", "info": SOMATIC_PROTOCOLS["box_breathing"]}
    if re.search(r'\b(4-7-8|4 7 8|relaxing breath|parasympathetic breath|sleep breath)\b', lower):
        return {"type": "somatic", "protocol_id": "relaxing_478", "info": SOMATIC_PROTOCOLS["relaxing_478"]}
    if re.search(r'\b(physiological sigh|double inhale|sigh breath|huberman breath|calm down breath)\b', lower):
        return {"type": "somatic", "protocol_id": "physiological_sigh", "info": SOMATIC_PROTOCOLS["physiological_sigh"]}
    if re.search(r'\b(5-4-3-2-1|grounding|sensory grounding|dissociation|flashback grounding)\b', lower):
        return {"type": "somatic", "protocol_id": "grounding_54321", "info": SOMATIC_PROTOCOLS["grounding_54321"]}
    if re.search(r'\b(progressive muscle|pmr|muscle relaxation|jacobson)\b', lower):
        return {"type": "somatic", "protocol_id": "pmr_jacobson", "info": SOMATIC_PROTOCOLS["pmr_jacobson"]}
    if re.search(r'\b(bilateral stimulation|butterfly hug|emdr tapping|tapping pacer)\b', lower):
        return {"type": "somatic", "protocol_id": "bilateral_tapping", "info": SOMATIC_PROTOCOLS["bilateral_tapping"]}

    # Assessment Scales
    if re.search(r'\b(phq-9|phq9|depression test|depression scale|depression questionnaire|am i depressed)\b', lower):
        return {"type": "scale", "scale_id": "phq9", "title": "PHQ-9 Depression Severity Scale"}
    if re.search(r'\b(gad-7|gad7|anxiety test|anxiety scale|anxiety questionnaire|am i anxious|panic attack test)\b', lower):
        return {"type": "scale", "scale_id": "gad7", "title": "GAD-7 Generalized Anxiety Scale"}
    if re.search(r'\b(ptsd screen|pc-ptsd|trauma test|ptsd test)\b', lower):
        return {"type": "scale", "scale_id": "pc_ptsd5", "title": "PC-PTSD-5 Trauma Screen"}
    if re.search(r'\b(insomnia test|insomnia scale|sleep quality score|isi sleep|insomnia severity)\b', lower):
        return {"type": "scale", "scale_id": "isi", "title": "Insomnia Severity Index (ISI)"}
    if re.search(r'\b(stress test|perceived stress|pss-4|stress level score)\b', lower):
        return {"type": "scale", "scale_id": "pss4", "title": "Perceived Stress Scale (PSS-4)"}
    if re.search(r'\b(alcohol screen|substance screen|cage questionnaire|cage-aid)\b', lower):
        return {"type": "scale", "scale_id": "cage_aid", "title": "CAGE-AID Substance Screener"}

    # General Mental Health / Somatic Toolkits
    if re.search(r'\b(mental health|somatic tool|somatic exercise|calm my nervous system|vagus nerve|vagal tone|breathing exercise|panic attack relief)\b', lower):
        return {"type": "general_toolkit", "title": "Mental Health & Somatic Suite", "icon": "🧠"}

    return None
