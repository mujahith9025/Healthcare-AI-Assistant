"""
Interactive First-Aid & Emergency Action Flashcards Module.
Provides step-by-step, clinically grounded, high-contrast emergency action protocols
for life-threatening emergencies, traumatic injuries, medical crises, and common first-aid scenarios.
Conforms to American Heart Association (AHA), Red Cross, and European Resuscitation Council (ERC) standards.
"""

from typing import Dict, Any, List, Optional
import re

FIRST_AID_CARDS_CATALOG: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 1. Life-Threatening Emergencies (Category: life_threatening)
    # -------------------------------------------------------------------------
    "cpr_adult": {
        "id": "cpr_adult",
        "title": "Adult CPR & Cardiac Arrest",
        "category": "life_threatening",
        "category_label": "🚨 Life-Threatening",
        "icon": "💓",
        "priority": "CRITICAL",
        "summary": "Hands-Only chest compressions and 30:2 Cardiopulmonary Resuscitation for unresponsive adults with absent or abnormal breathing.",
        "call_emergency_first": True,
        "metronome_bpm": 110,
        "critical_donots": [
            "DO NOT delay chest compressions to give rescue breaths if you are untrained (use Hands-Only CPR).",
            "DO NOT stop compressions for more than 10 seconds at any time.",
            "DO NOT perform compressions on a responsive or normally breathing individual.",
            "DO NOT place hands over the xiphoid process (lower tip of breastbone) or abdomen."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Check Responsiveness & Breathing",
                "action": "Tap shoulders firmly and shout: 'Are you okay?'. Look at the chest for 5–10 seconds for normal breathing or gasping.",
                "detail": "If person is unresponsive and not breathing or only gasping (agonal breaths), treat as sudden cardiac arrest.",
                "visual_hint": "Tap & Shout ➔ Scan chest movements"
            },
            {
                "step_num": 2,
                "title": "Call Emergency & Request an AED",
                "action": "Point to a specific bystander: 'Call 911 / 112 / 999 and get an Automated External Defibrillator (AED) immediately!'.",
                "detail": "If alone with a mobile phone, place it on speaker while initiating CPR immediately.",
                "visual_hint": "Call 911 / 112 ➔ Put on speaker ➔ Get AED"
            },
            {
                "step_num": 3,
                "title": "Hand Placement on Center of Chest",
                "action": "Place heel of one hand on center of chest (lower half of breastbone). Interlock other hand over top.",
                "detail": "Keep elbows locked, arms straight, and shoulders positioned directly over your hands.",
                "visual_hint": "Heel of hand on center breastbone ➔ Interlock fingers"
            },
            {
                "step_num": 4,
                "title": "Deliver Hard & Fast Compressions (100–120 BPM)",
                "action": "Compress at least 2 inches (5 cm) deep at a rate of 100–120 beats/minute. Allow full chest recoil after every compression.",
                "detail": "Match the compression cadence to the 110 BPM metronome or songs like 'Stayin' Alive'. Continue until AED arrives or EMS takes over.",
                "visual_hint": "Compress 2 inches deep ➔ 110 BPM cadence ➔ Full chest recoil"
            },
            {
                "step_num": 5,
                "title": "Apply AED as Soon as Available",
                "action": "Turn on AED, attach pads to bare chest (upper right chest & lower left ribs), and follow voice prompts.",
                "detail": "Ensure nobody touches the patient when the AED announces: 'Analyzing heart rhythm' or 'Delivering shock'. Resume CPR immediately after shock.",
                "visual_hint": "Power on AED ➔ Stick pads ➔ Follow voice prompts"
            }
        ],
        "recovery_or_monitoring": "If patient regains consciousness and breathes normally, place in the recovery position on their side and monitor airway continuously.",
        "citations": "AHA Guidelines for CPR & ECC / Red Cross Resuscitation Standards"
    },

    "choking_adult": {
        "id": "choking_adult",
        "title": "Choking & Airway Obstruction (Heimlich)",
        "category": "life_threatening",
        "category_label": "🚨 Life-Threatening",
        "icon": "🫁",
        "priority": "CRITICAL",
        "summary": "Rapid relief of complete airway obstruction in conscious adults and children using back blows and abdominal thrusts.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT perform abdominal thrusts on responsive infants under 1 year (use back slaps & chest thrusts instead).",
            "DO NOT perform blind finger sweeps in the mouth (can push foreign body deeper into larynx).",
            "DO NOT interfere if the person is coughing forcefully or able to speak."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Assess Severity & Ask for Consent",
                "action": "Look for universal choking sign (hands clutching throat), inability to speak, weak cough, or silent panic.",
                "detail": "Ask: 'Are you choking? Can you speak?'. If they cannot speak or breathe, tell them you are going to help.",
                "visual_hint": "Universal clutching throat sign ➔ Silent panic"
            },
            {
                "step_num": 2,
                "title": "Deliver 5 Firm Back Blows",
                "action": "Lean the person forward supporting their chest with one arm. Give 5 sharp blows with the heel of your hand between shoulder blades.",
                "detail": "Gravity assisted by firm back blows helps dislodge foreign body from the subglottic airway.",
                "visual_hint": "Lean forward ➔ 5 firm heel blows between shoulder blades"
            },
            {
                "step_num": 3,
                "title": "Deliver 5 Inward & Upward Abdominal Thrusts",
                "action": "Stand behind person, wrap arms around waist. Place fist thumb-side in just above navel, grasp with other hand, thrust sharply in and up.",
                "detail": "Repeat cycles of 5 back blows and 5 abdominal thrusts until object is expelled or person loses consciousness.",
                "visual_hint": "Fist above navel ➔ Quick upward 'J' hook thrusts"
            },
            {
                "step_num": 4,
                "title": "If Person Becomes Unresponsive: Initiate CPR",
                "action": "Lower person safely to the floor. Call emergency immediately, begin 30 chest compressions.",
                "detail": "Before delivering rescue breaths, open airway and look in mouth; remove object ONLY if clearly visible.",
                "visual_hint": "Lower to floor ➔ Call 911 ➔ Start CPR compressions"
            }
        ],
        "recovery_or_monitoring": "Anyone who receives abdominal thrusts must be evaluated by a physician to rule out internal abdominal or rib trauma.",
        "citations": "AHA / Red Cross Choking & Airway Management Protocol"
    },

    "choking_infant": {
        "id": "choking_infant",
        "title": "Infant Choking (<1 Year Old)",
        "category": "life_threatening",
        "category_label": "🚨 Life-Threatening",
        "icon": "👶",
        "priority": "CRITICAL",
        "summary": "Specialized back slaps and gentle chest thrusts for infants under 12 months with complete foreign body airway obstruction.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT perform abdominal Heimlich thrusts on infants (can rupture delicate liver or spleen).",
            "DO NOT perform blind finger sweeps.",
            "DO NOT shake the infant."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Position Infant Face-Down on Forearm",
                "action": "Support infant's jaw and head with fingers. Rest forearm on thigh, keeping infant's head lower than their chest.",
                "detail": "Ensures gravity helps dislodge the foreign obstruction out of the mouth.",
                "visual_hint": "Face-down on forearm ➔ Head lower than trunk ➔ Support jaw"
            },
            {
                "step_num": 2,
                "title": "Deliver 5 Firm Back Slaps",
                "action": "Give 5 distinct, firm blows between shoulder blades using the heel of your free hand.",
                "detail": "Each blow should be a separate, deliberate effort to relieve obstruction.",
                "visual_hint": "5 heel-of-hand slaps between shoulder blades"
            },
            {
                "step_num": 3,
                "title": "Turn Face-Up & Give 5 Chest Thrusts",
                "action": "Sandwich infant between forearms, flip face-up on thigh. Place 2 fingers on center of chest just below nipple line; deliver 5 quick downward compressions (1.5 inches deep).",
                "detail": "Alternate 5 back slaps and 5 chest thrusts until object is expelled or infant becomes unresponsive.",
                "visual_hint": "Flip face-up ➔ 2 fingers below nipple line ➔ 5 quick thrusts"
            },
            {
                "step_num": 4,
                "title": "If Infant Becomes Unconscious",
                "action": "Place on firm flat surface, call 911 / 112 immediately, begin infant CPR (30 compressions : 2 gentle breaths).",
                "detail": "Check mouth before breaths; remove object only if visible.",
                "visual_hint": "Firm surface ➔ 30 compressions with 2 fingers"
            }
        ],
        "recovery_or_monitoring": "Always have emergency medical personnel examine an infant after any airway obstruction episode.",
        "citations": "AHA Pediatric First Aid & Resuscitation Consensus"
    },

    "severe_bleeding": {
        "id": "severe_bleeding",
        "title": "Severe Bleeding & Hemorrhage Control",
        "category": "trauma",
        "category_label": "🩸 Trauma & Bleeding",
        "icon": "🩸",
        "priority": "CRITICAL",
        "summary": "Life-saving techniques to arrest arterial or venous traumatic hemorrhage using direct pressure, wound packing, and tourniquets.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT remove embedded knives, glass, or large foreign objects (stabilize around them).",
            "DO NOT release direct pressure to check if bleeding has stopped.",
            "DO NOT apply a tourniquet directly over a joint (knee or elbow); place 2–3 inches above wound.",
            "DO NOT remove or loosen an applied tourniquet once tightened."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Ensure Safety & Call Emergency",
                "action": "Wear protective gloves if available. Call 911 / 112 for life-threatening spurting or pooling blood.",
                "detail": "Expose the wound completely by cutting or removing clothing to see exact hemorrhage source.",
                "visual_hint": "Gloves on ➔ Call 911 ➔ Expose wound"
            },
            {
                "step_num": 2,
                "title": "Apply Immediate Direct Firm Pressure",
                "action": "Place sterile gauze, clean cloth, or bare hands directly over bleeding vessel. Press down with maximum body weight.",
                "detail": "Lock elbows and lean your weight into the pressure point. Maintain continuous relentless pressure.",
                "visual_hint": "Gauze on wound ➔ Bodyweight firm continuous pressure"
            },
            {
                "step_num": 3,
                "title": "Wound Packing for Junctional / Deep Wounds",
                "action": "For groin, armpit, or deep muscle cavities, tightly pack hemostatic gauze directly into wound down to bone, then maintain 3 mins firm pressure.",
                "detail": "Packing creates mechanical tamponade against severed deep vessels.",
                "visual_hint": "Pack gauze deep into cavity ➔ Hold firm pressure"
            },
            {
                "step_num": 4,
                "title": "Apply Tourniquet for Severe Limb Hemorrhage",
                "action": "Place commercial tourniquet (CAT/SOFTT) 2–3 inches proximal to wound (between wound and heart). Tighten windlass until bleeding stops and distal pulse is absent.",
                "detail": "Lock windlass clip. Write the exact application time (e.g. 'T: 14:35') on the tourniquet time strap.",
                "visual_hint": "2-3 inches above wound ➔ Twist windlass until bleeding stops ➔ Mark time"
            }
        ],
        "recovery_or_monitoring": "Keep patient warm with blankets to prevent hypothermia-induced coagulopathy. Elevate legs slightly if showing signs of hemorrhagic shock (pale, rapid pulse, confusion).",
        "citations": "Stop the Bleed Campaign / American College of Surgeons Trauma Guidelines"
    },

    "anaphylaxis": {
        "id": "anaphylaxis",
        "title": "Anaphylaxis & Severe Allergic Reaction",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "💉",
        "priority": "CRITICAL",
        "summary": "Rapid intervention for multi-system severe allergic shock involving airway swelling, wheezing, hives, and hypotension.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT delay epinephrine administration; antihistamines (Benadryl) do NOT stop laryngeal edema or shock.",
            "DO NOT allow the person to stand or walk abruptly (can cause fatal vena cava collapse).",
            "DO NOT inject epinephrine into hands, feet, or buttocks (use mid-outer thigh only)."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Recognize Signs & Call 911 / 112",
                "action": "Look for throat tightness, swollen tongue/lips, wheezing, widespread hives, vomiting, or dizziness after allergen exposure.",
                "detail": "Anaphylaxis progresses rapidly within minutes; call emergency immediately.",
                "visual_hint": "Airway swelling ➔ Hives ➔ Wheezing ➔ Call 911"
            },
            {
                "step_num": 2,
                "title": "Administer Epinephrine Autoinjector (EpiPen)",
                "action": "Grasp autoinjector with fist, pull off safety cap. Swing and push orange/needle tip firmly at 90° into outer mid-thigh until it clicks.",
                "detail": "Hold firmly in place for 3 full seconds (or 10 seconds for older devices), then massage injection site for 10 seconds.",
                "visual_hint": "Remove safety cap ➔ 90° into outer thigh ➔ Hold 3 seconds"
            },
            {
                "step_num": 3,
                "title": "Position Patient Supine with Legs Elevated",
                "action": "Lay patient flat on their back with legs raised ~12 inches to maintain venous return to the heart.",
                "detail": "If breathing is difficult, allow them to sit upright slightly; if vomiting or unconscious, place in recovery position.",
                "visual_hint": "Flat on back ➔ Legs elevated 12 inches"
            },
            {
                "step_num": 4,
                "title": "Prepare Second Dose if No Improvement",
                "action": "If symptoms persist or worsen after 5–10 minutes and emergency EMS has not arrived, administer a second autoinjector in opposite thigh.",
                "detail": "Keep used autoinjectors in hard casing to hand over to arriving paramedics.",
                "visual_hint": "Wait 5-10 mins ➔ 2nd dose in other thigh if needed"
            }
        ],
        "recovery_or_monitoring": "Biphasic allergic reactions can occur up to 12–24 hours later; all anaphylaxis patients must be transported by ambulance for ER monitoring.",
        "citations": "World Allergy Organization (WAO) & AAAAI Guidelines"
    },

    "stroke_fast": {
        "id": "stroke_fast",
        "title": "Stroke Recognition (FAST Protocol)",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "🧠",
        "priority": "CRITICAL",
        "summary": "Rapid identification of acute ischemic or hemorrhagic cerebrovascular accident using the validated FAST screening protocol.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT give aspirin, medication, food, or water (can cause fatal aspiration and worsens hemorrhagic stroke).",
            "DO NOT let the person sleep or drive themselves to the hospital.",
            "DO NOT delay calling emergency to 'see if symptoms improve'."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "F - Face Drooping",
                "action": "Ask the person to smile. Look for unevenness, lopsided smile, or one side of face drooping or numb.",
                "detail": "Facial nerve weakness is a hallmark sign of acute cortical infarction.",
                "visual_hint": "Ask to smile ➔ Check for one-sided facial droop"
            },
            {
                "step_num": 2,
                "title": "A - Arm Weakness",
                "action": "Ask person to raise both arms in front of them with palms up and eyes closed for 10 seconds.",
                "detail": "Check if one arm drifts downward or cannot be raised at all (pronator drift).",
                "visual_hint": "Raise both arms ➔ Check if one arm drifts down"
            },
            {
                "step_num": 3,
                "title": "S - Speech Difficulty",
                "action": "Ask person to repeat a simple sentence: 'The sky is blue in the morning'.",
                "detail": "Listen for slurred speech, garbled words, word-finding difficulty (aphasia), or inability to comprehend.",
                "visual_hint": "Repeat simple phrase ➔ Listen for slurred/garbled speech"
            },
            {
                "step_num": 4,
                "title": "T - Time to Call 911 / 112 & Note Last Known Normal",
                "action": "If ANY of these signs are positive, call emergency immediately. State: 'I suspect an acute stroke'.",
                "detail": "Note the exact time when patient was last seen completely normal; thrombolytic tPA window is typically within 3–4.5 hours.",
                "visual_hint": "Call 911 / 112 immediately ➔ Record exact time of onset"
            }
        ],
        "recovery_or_monitoring": "Keep patient lying comfortably with head elevated 15–30°. Keep airway clear and monitor breathing until EMS arrives.",
        "citations": "American Heart Association / American Stroke Association Guidelines"
    },

    "heart_attack": {
        "id": "heart_attack",
        "title": "Heart Attack & Acute Coronary Syndrome",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "❤️",
        "priority": "CRITICAL",
        "summary": "First-aid response for acute myocardial infarction, chest tightness, radiating pain, and sudden cardiac distress.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT drive yourself to the hospital (paramedics initiate cardiac monitoring & treatment en route).",
            "DO NOT give aspirin if patient has known severe aspirin allergy or active gastrointestinal bleeding.",
            "DO NOT allow patient to exert themselves or walk around."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Recognize Warning Signs",
                "action": "Look for heavy crushing pressure, squeezing, or pain in center of chest lasting >few minutes; pain radiating to left arm, shoulder, neck, jaw, or back; cold sweats, nausea, and shortness of breath.",
                "detail": "Women and elderly individuals frequently experience atypical symptoms: unexplained fatigue, nausea, back pain, or lightheadedness without overt chest pain.",
                "visual_hint": "Chest pressure ➔ Arm/Jaw pain ➔ Cold sweat ➔ Nausea"
            },
            {
                "step_num": 2,
                "title": "Call 911 / 112 / 999 Immediately",
                "action": "Activate emergency medical services right away. Tell dispatcher you suspect an acute heart attack.",
                "detail": "Early EMS notification enables hospital catheterization labs to prep before patient arrival.",
                "visual_hint": "Call emergency immediately ➔ Request cardiac ambulance"
            },
            {
                "step_num": 3,
                "title": "Position Patient in Semi-Sitting Rest",
                "action": "Sit patient comfortably on floor or chair with knees bent and back supported (W-position).",
                "detail": "Reduces cardiac preload and decreases myocardial oxygen demand.",
                "visual_hint": "Semi-seated with back supported ➔ Knees bent"
            },
            {
                "step_num": 4,
                "title": "Administer Chewable Aspirin (324 mg)",
                "action": "If patient is conscious, has no aspirin allergy, and no active GI bleeding, have them chew 1 adult (325 mg) or 4 low-dose baby aspirins (81 mg each).",
                "detail": "Chewing accelerates platelet anti-aggregation within 5–10 minutes compared to swallowing whole pills.",
                "visual_hint": "Chew 324 mg aspirin (4 baby aspirins) ➔ Do not swallow whole"
            },
            {
                "step_num": 5,
                "title": "Assist with Prescribed Nitroglycerin & Prepare for CPR",
                "action": "If patient has prescribed sublingual nitroglycerin, help them take 1 dose under tongue. If patient collapses and becomes unresponsive, begin CPR immediately.",
                "detail": "Locate nearest AED in building while waiting for ambulance.",
                "visual_hint": "Sublingual nitro if prescribed ➔ Standby for CPR/AED"
            }
        ],
        "recovery_or_monitoring": "Continuously monitor pulse and breathing. Keep calm and loosen tight collars or neckties.",
        "citations": "AHA / ACC Emergency Cardiac Care Guidelines"
    },

    "cpr_infant": {
        "id": "cpr_infant",
        "title": "Infant CPR & Pediatric Arrest",
        "category": "life_threatening",
        "category_label": "🚨 Life-Threatening",
        "icon": "👶",
        "priority": "CRITICAL",
        "summary": "Cardiopulmonary resuscitation for unresponsive infants (<1 year) using two-finger or two-thumb chest compressions and gentle rescue breaths.",
        "call_emergency_first": True,
        "metronome_bpm": 110,
        "critical_donots": [
            "DO NOT tilt the infant's head back too far (hyper-extension collapses infant airway; maintain neutral sniffing position).",
            "DO NOT deliver heavy forceful breaths into an infant (puff gently from cheeks to avoid pneumothorax).",
            "DO NOT compress the xiphoid tip (bottom of breastbone)."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Check Responsiveness & Breathing",
                "action": "Flick soles of infant's feet and call name. Look at chest for 5–10 seconds for normal breathing or gasping.",
                "detail": "If unresponsive and not breathing or only gasping, immediately initiate pediatric emergency action.",
                "visual_hint": "Flick bottom of feet ➔ Scan chest for breathing"
            },
            {
                "step_num": 2,
                "title": "Call Emergency or Start 2 Mins of CPR if Alone",
                "action": "Shout for someone to call 911 / 112 / 999. If alone, perform 2 minutes (5 cycles of 30:2) of CPR before leaving to call.",
                "detail": "Hypoxia is the primary cause of pediatric cardiac arrest; immediate oxygenation and compressions are vital.",
                "visual_hint": "Call 911 ➔ If alone, 2 mins CPR before calling"
            },
            {
                "step_num": 3,
                "title": "Two-Finger Chest Compressions (110 BPM)",
                "action": "Place 2 fingers in center of chest just below nipple line. Compress 1.5 inches (4 cm) deep at 100–120 compressions/min (110 BPM metronome).",
                "detail": "Allow complete chest recoil between each compression without removing fingers from skin.",
                "visual_hint": "2 fingers just below nipple line ➔ 1.5 inches deep ➔ 110 BPM cadence"
            },
            {
                "step_num": 4,
                "title": "Deliver 2 Gentle Puffs (30:2 Ratio)",
                "action": "Cover infant's nose and mouth with your mouth. Give 2 gentle puffs just until chest visibly rises.",
                "detail": "Each breath should last ~1 second. Resume 30 compressions immediately.",
                "visual_hint": "Cover nose and mouth ➔ 2 gentle cheek puffs ➔ Resume compressions"
            }
        ],
        "recovery_or_monitoring": "Continue 30:2 CPR cycles until infant breathes normally or emergency paramedics arrive.",
        "citations": "AHA Pediatric Basic Life Support (PBLS) Guidelines"
    },

    "seizure": {
        "id": "seizure",
        "title": "Seizures & Convulsions First Aid",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "⚡",
        "priority": "URGENT",
        "summary": "Protective first-aid management during generalized tonic-clonic convulsions and post-ictal recovery.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT put ANYTHING in the person's mouth (cannot swallow tongue; objects cause broken teeth and airway obstruction).",
            "DO NOT hold down, restrain, or fight their jerky movements.",
            "DO NOT give food, water, or medication until fully awake and alert."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Protect from Physical Injury & Clear Area",
                "action": "Guide person gently to floor if falling. Move hard, sharp, or hot objects away from immediate area.",
                "detail": "Place something soft and flat (folded jacket or pillow) under their head.",
                "visual_hint": "Clear sharp furniture ➔ Soft cushion under head"
            },
            {
                "step_num": 2,
                "title": "Time the Seizure",
                "action": "Look at watch or phone to record exact start time of convulsions.",
                "detail": "Call 911 / 112 immediately if seizure lasts >5 minutes (Status Epilepticus), if second seizure follows without waking, if pregnant, or if injured.",
                "visual_hint": "Note start time ➔ Call 911 if >5 minutes"
            },
            {
                "step_num": 3,
                "title": "Loosen Clothing & Turn onto Side (Recovery Position)",
                "action": "Loosen tight neckties or collars. As soon as convulsions subside or if vomiting, roll person gently onto their side.",
                "detail": "Side position prevents saliva, vomit, or tongue from occluding the airway.",
                "visual_hint": "Loosen collar ➔ Roll onto side into recovery position"
            },
            {
                "step_num": 4,
                "title": "Stay Calm & Reassure as They Awaken",
                "action": "Stay with person until fully awake and alert. Speak calmly and explain what happened.",
                "detail": "Post-ictal confusion and extreme fatigue are normal for 10–30 minutes following a seizure.",
                "visual_hint": "Stay until alert ➔ Offer calm reassurance"
            }
        ],
        "recovery_or_monitoring": "Call emergency if this is the person's first seizure, if it occurred in water, or if normal breathing does not resume within 2 minutes.",
        "citations": "Epilepsy Foundation & CDC First Aid for Seizures"
    },

    "burns_scalds": {
        "id": "burns_scalds",
        "title": "Burns & Scalds Management",
        "category": "trauma",
        "category_label": "🩸 Trauma & Bleeding",
        "icon": "🔥",
        "priority": "URGENT",
        "summary": "Immediate thermal, chemical, or electrical burn care to halt tissue destruction and prevent infection.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT apply ice or ice water directly to burns (causes vasoconstriction and worsens tissue necrosis).",
            "DO NOT apply butter, toothpaste, oil, or home remedies (traps heat and induces severe bacterial infection).",
            "DO NOT pop or burst blisters (intact skin is natural sterile barrier).",
            "DO NOT peel off clothing that is melted or stuck to burned flesh."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Remove Source of Heat & Ensure Safety",
                "action": "Extinguish flames or disconnect power source for electrical burns. Remove hot liquids or smoldering clothing.",
                "detail": "For chemical burns, brush off dry powder, then flush continuously with water.",
                "visual_hint": "Remove heat source ➔ Protect yourself"
            },
            {
                "step_num": 2,
                "title": "Cool with Running Water for 20 Minutes",
                "action": "Hold burn under cool running tap water (10–20°C / 50–68°F) for at least 20 continuous minutes.",
                "detail": "Cooling within first 3 hours stops thermal progression, reduces edema, and accelerates healing depth.",
                "visual_hint": "Cool running tap water ➔ Full 20 minutes timer"
            },
            {
                "step_num": 3,
                "title": "Remove Constrictive Jewelry & Loose Clothing",
                "action": "Gently remove rings, watches, bracelets, and tight clothes near burn before swelling begins.",
                "detail": "Swelling occurs rapidly; constrictive bands can compromise distal arterial blood supply.",
                "visual_hint": "Remove rings/watches before swelling begins"
            },
            {
                "step_num": 4,
                "title": "Cover Loosely with Clean Non-Adherent Dressing",
                "action": "Cover loosely with sterile plastic cling film (layered flat, not wrapped tightly) or sterile non-stick gauze.",
                "detail": "Plastic wrap provides a sterile, non-adherent barrier that reduces pain by shielding exposed nerve endings from air.",
                "visual_hint": "Layer clean plastic wrap flat over burn"
            }
        ],
        "recovery_or_monitoring": "Seek immediate hospital care for burns larger than the patient's palm, burns on face/hands/joints/genitals, circumferential burns, or chemical/electrical burns.",
        "citations": "American Burn Association & British Burn Association Standards"
    },

    "poisoning_ingestion": {
        "id": "poisoning_ingestion",
        "title": "Poisoning & Toxic Substance Ingestion",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "🧪",
        "priority": "CRITICAL",
        "summary": "Urgent intervention for swallowed household chemicals, toxic plants, medication overdoses, or corrosive agents.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT induce vomiting unless specifically instructed by Poison Control (caustic acids/alkalis burn esophagus twice).",
            "DO NOT give activated charcoal, syrup of ipecac, milk, or raw eggs without medical direction.",
            "DO NOT wait for symptoms to appear before calling Poison Help."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Assess Scene & Remove from Immediate Hazard",
                "action": "Ensure personal safety. If toxic fumes/gas present, move patient to fresh air immediately.",
                "detail": "Do not enter enclosed spaces without protective equipment.",
                "visual_hint": "Move to fresh air ➔ Secure the poison container"
            },
            {
                "step_num": 2,
                "title": "Identify the Substance & Keep Packaging",
                "action": "Secure container, pill bottle, plant leaf, or label. Note estimated quantity ingested and exact time.",
                "detail": "Essential for medical toxicologists to determine specific antidote and gastric decontamination window.",
                "visual_hint": "Read container label ➔ Note time & estimated amount"
            },
            {
                "step_num": 3,
                "title": "Call Regional Poison Center / Emergency Hotline",
                "action": "In US: 1-800-222-1222. In UK: 111. In India: 1800-116-117. In Canada: 1-844-POISON-X. If unresponsive, call 911 / 112 directly.",
                "detail": "Poison specialists provide free, expert, 24/7 step-by-step guidance tailored to the exact chemical formulation.",
                "visual_hint": "Call 1-800-222-1222 / 911 ➔ Follow toxicologist instructions"
            },
            {
                "step_num": 4,
                "title": "Rinse Mouth / Skin if Exposed",
                "action": "For corrosive liquid on lips or mouth, have person gently spit and rinse with small sips of water if conscious. For skin contact, flush with water for 15 minutes.",
                "detail": "If patient becomes drowsy or uncoordinated, place in recovery position on side to protect airway.",
                "visual_hint": "Rinse mouth ➔ Place on side in recovery position"
            }
        ],
        "recovery_or_monitoring": "Bring the poison container or sample with you to the emergency department.",
        "citations": "American Association of Poison Control Centers (AAPCC) Protocols"
    },

    "asthma_attack": {
        "id": "asthma_attack",
        "title": "Asthma Attack & Severe Bronchospasm",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "🌬️",
        "priority": "URGENT",
        "summary": "First-aid protocol for acute wheezing, chest tightness, and respiratory distress using the 4x4x4 inhaler protocol.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT lay the person flat on their back (severely restricts lung volume and diaphragm expansion).",
            "DO NOT crowd around the patient; ensure fresh circulating air.",
            "DO NOT use cold water drinks which can trigger further bronchospasm."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Sit Upright & Reassure Calmly",
                "action": "Sit person upright leaning slightly forward with elbows resting on knees or a table (tripod position).",
                "detail": "Loosen tight neckwear. Help them breathe slowly and steadily.",
                "visual_hint": "Sit upright ➔ Lean slightly forward (Tripod position)"
            },
            {
                "step_num": 2,
                "title": "Deliver 4 Puffs of Fast-Acting Blue Reliever (Albuterol)",
                "action": "Shake blue inhaler, attach spacer if available. Give 1 puff into spacer, take 4 slow breaths. Repeat for 4 total puffs.",
                "detail": "Using a spacer improves bronchodilator lung deposition by up to 50%.",
                "visual_hint": "Shake inhaler ➔ 1 puff with 4 slow breaths ➔ Repeat for 4 puffs"
            },
            {
                "step_num": 3,
                "title": "Wait 4 Minutes & Re-Evaluate",
                "action": "If person still cannot breathe comfortably or speak in full sentences, deliver another 4 puffs (1 puff at a time).",
                "detail": "Monitor for chest retraction (sucking in of ribs/neck) or blue lips.",
                "visual_hint": "Wait 4 minutes ➔ Deliver another 4 puffs if not improved"
            },
            {
                "step_num": 4,
                "title": "Call 911 / 112 if No Improvement After 8 Puffs",
                "action": "If still distressed after second round, call emergency immediately. Continue giving 4 puffs every 4 minutes until ambulance arrives.",
                "detail": "Inform dispatch that patient is experiencing severe refractory acute asthma.",
                "visual_hint": "Call 911 ➔ Continue 4 puffs every 4 minutes until EMS arrives"
            }
        ],
        "recovery_or_monitoring": "Even if symptoms improve, have patient contact their primary physician to adjust maintenance steroid inhaler therapies.",
        "citations": "Global Initiative for Asthma (GINA) & British Thoracic Society First Aid"
    },

    "hypoglycemia": {
        "id": "hypoglycemia",
        "title": "Hypoglycemia (Diabetic Low Blood Sugar)",
        "category": "medical_crisis",
        "category_label": "⚡ Medical Crises",
        "icon": "🍬",
        "priority": "URGENT",
        "summary": "Rapid glucose restoration using the validated 15-15 clinical rule for trembling, sweating, and confusion in diabetic patients.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT give food, liquids, or oral sugar to someone who is unconscious or having seizures (aspiration hazard).",
            "DO NOT use high-fat sweets like chocolate, ice cream, or pastries (fat delays glucose absorption).",
            "DO NOT inject insulin during a low blood sugar episode."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Recognize Symptoms & Check Glucose",
                "action": "Look for shakiness, diaphoresis (cold sweats), dizziness, pale skin, irritability, or confusion.",
                "detail": "If glucometer available, test blood glucose: $<70\text{ mg/dL}$ ($<3.9\text{ mmol/L}$) confirms hypoglycemia.",
                "visual_hint": "Shakiness / Sweating / Confusion ➔ Check fingerstick glucose"
            },
            {
                "step_num": 2,
                "title": "The 15-15 Rule: Administer 15 Grams of Fast-Acting Sugar",
                "action": "Provide ONE of the following: 4 glucose tablets, 1/2 cup (4 oz) fruit juice or non-diet soda, or 1 tablespoon of honey/sugar.",
                "detail": "Pure fast-acting carbohydrates raise systemic blood glucose within 10–15 minutes.",
                "visual_hint": "4 glucose tablets OR 1/2 cup fruit juice / non-diet soda"
            },
            {
                "step_num": 3,
                "title": "Wait 15 Minutes & Re-Test",
                "action": "Rest for 15 minutes, then re-check blood glucose level.",
                "detail": "If still $<70\text{ mg/dL}$ ($<3.9\text{ mmol/L}$), administer another 15 grams of fast-acting sugar.",
                "visual_hint": "Wait 15 mins ➔ Recheck ➔ Repeat 15g if still <70 mg/dL"
            },
            {
                "step_num": 4,
                "title": "Eat Complex Snack Once Glucose Normalizes",
                "action": "Once blood sugar rises $\ge 70\text{ mg/dL}$, have person eat a balanced snack (e.g. half a sandwich, crackers with cheese, or their scheduled meal).",
                "detail": "Complex carbohydrates and protein sustain normal glucose levels and prevent recurrent rebound dips.",
                "visual_hint": "Eat small meal/snack (sandwich or crackers) to sustain levels"
            }
        ],
        "recovery_or_monitoring": "If patient becomes unconscious or cannot swallow safely, administer intramuscular/nasal Glucagon (Baqsimi) if trained and call 911 / 112 immediately.",
        "citations": "American Diabetes Association (ADA) Standards of Medical Care"
    },

    "heatstroke_exhaustion": {
        "id": "heatstroke_exhaustion",
        "title": "Heatstroke vs. Heat Exhaustion",
        "category": "trauma",
        "category_label": "🩸 Trauma & Bleeding",
        "icon": "☀️",
        "priority": "CRITICAL",
        "summary": "Differentiating life-threatening heatstroke ($>104^\circ\text{F}$, altered mental state) from heat exhaustion and applying aggressive rapid cooling.",
        "call_emergency_first": True,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT delay cooling a heatstroke patient (every minute of severe hyperthermia increases brain damage risk).",
            "DO NOT give antipyretic medications (Tylenol/Aspirin do NOT work for environmental hyperthermia and stress liver/kidneys).",
            "DO NOT force fluids if patient is vomiting or confused."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Differentiate Heat Exhaustion vs. Heatstroke",
                "action": "Heat Exhaustion: Heavy sweating, pale/clammy skin, dizziness, nausea, normal mental status. Heatstroke (EMERGENCY): Hot red dry/wet skin, confusion, slurred speech, delirium, seizures, temperature $>104^\circ\text{F}$ ($40^\circ\text{C}$).",
                "detail": "If confusion or altered mental state is present, treat as life-threatening Heatstroke immediately and call 911.",
                "visual_hint": "Confusion / Delirium + Hot skin = HEATSTROKE EMERGENCY"
            },
            {
                "step_num": 2,
                "title": "Move to Cool Environment & Strip Heavy Clothing",
                "action": "Move patient into air-conditioned room or deep shade. Remove excess layers of clothing down to underwear.",
                "detail": "Maximizes body surface area exposed to convective and evaporative cooling.",
                "visual_hint": "Move to AC/shade ➔ Strip outer clothing"
            },
            {
                "step_num": 3,
                "title": "Aggressive Active Cooling for Heatstroke",
                "action": "Immerse in cold water tub up to neck, or douse body with cold water while fanning vigorously. Apply ice packs to neck, armpits, and groin.",
                "detail": "Rapid whole-body cold water immersion is the clinical gold standard for reducing core temperature under $102^\circ\text{F}$.",
                "visual_hint": "Cold water immersion OR ice packs on neck/armpits/groin + fanning"
            },
            {
                "step_num": 4,
                "title": "Hydrate ONLY if Fully Conscious (Heat Exhaustion)",
                "action": "If person is fully alert and not vomiting, provide cool water or electrolyte sports drink to sip slowly.",
                "detail": "Avoid ice-cold drinks in large gulps to prevent stomach cramps.",
                "visual_hint": "Sip cool electrolyte water slowly (Alert patients only)"
            }
        ],
        "recovery_or_monitoring": "Heatstroke requires emergency ambulance transport and ICU hemodynamic stabilization.",
        "citations": "CDC Extreme Heat Guidelines & Wilderness Medical Society Consensus"
    },

    "hypothermia_frostbite": {
        "id": "hypothermia_frostbite",
        "title": "Hypothermia & Cold Exposure",
        "category": "trauma",
        "category_label": "🩸 Trauma & Bleeding",
        "icon": "❄️",
        "priority": "URGENT",
        "summary": "Core body temperature restoration and safe rewarming protocols for acute cold exposure, shivering, and frostbite.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT rub or massage frostbitten tissue or snow onto skin (causes catastrophic ice crystal mechanical injury).",
            "DO NOT use direct intense heat like hot radiators, heating pads, or fires (causes severe burns due to loss of sensation).",
            "DO NOT give alcohol or caffeinated beverages."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Move to Warm Shelter & Remove Wet Clothing",
                "action": "Bring person out of cold/wind into heated shelter. Gently remove wet clothes and pat dry.",
                "detail": "Handle gently; rough movement can precipitate ventricular fibrillation in cold myocardium.",
                "visual_hint": "Shelter from cold ➔ Gently strip wet clothing"
            },
            {
                "step_num": 2,
                "title": "Insulate & Apply Passive Rewarming",
                "action": "Wrap person in multiple warm dry blankets, sleeping bags, and cover head leaving only face exposed.",
                "detail": "Insulate from cold ground using foam pads or dry coats.",
                "visual_hint": "Multi-layer dry blankets ➔ Cover head"
            },
            {
                "step_num": 3,
                "title": "Apply Active External Heat to Core",
                "action": "Place warm (not hot) water bottles or chemical heating pads wrapped in cloth onto chest, neck, and groin.",
                "detail": "Applying heat to core prevents peripheral vasodilation and core temperature afterdrop.",
                "visual_hint": "Warm wrapped packs on chest / armpits / groin"
            },
            {
                "step_num": 4,
                "title": "Provide Warm Sweet Fluids if Conscious",
                "action": "Offer warm sweetened non-caffeinated drinks (warm broth or tea) if fully awake and swallowing normally.",
                "detail": "Provides calories for thermogenesis and combats dehydration.",
                "visual_hint": "Warm sweet drinks (Conscious only)"
            }
        ],
        "recovery_or_monitoring": "Seek emergency medical care if shivering ceases while remaining cold, or if confusion, slurred speech, or lethargy develops.",
        "citations": "Wilderness Medical Society Clinical Practice Guidelines on Hypothermia"
    },

    "fractures_sprains": {
        "id": "fractures_sprains",
        "title": "Fractures, Sprains & Joint Injuries",
        "category": "everyday_injuries",
        "category_label": "🩹 Everyday First-Aid",
        "icon": "🦴",
        "priority": "STANDARD",
        "summary": "Stabilization, splinting principles, and R.I.C.E. protocol for suspected broken bones, dislocations, and severe ligament sprains.",
        "call_emergency_first": False,
        "metronome_bpm": None,
        "critical_donots": [
            "DO NOT attempt to straighten, realign, or push back protruding bone ends in open fractures.",
            "DO NOT apply ice directly onto bare skin (always wrap ice packs in a cloth).",
            "DO NOT allow patient to bear weight or walk on suspected fracture/dislocation."
        ],
        "steps": [
            {
                "step_num": 1,
                "title": "Immobilize & Support the Injured Limb",
                "action": "Support the limb in the position found. Ask patient to keep limb completely still.",
                "detail": "Preventing movement avoids further laceration of surrounding muscles, blood vessels, and nerves.",
                "visual_hint": "Support limb in position found ➔ Prevent movement"
            },
            {
                "step_num": 2,
                "title": "Check Distal Circulation, Sensation & Movement (CSM)",
                "action": "Check fingers/toes beyond injury: Are they warm and pink? Can patient feel touch and wiggle digits? Is a distal pulse palpable?",
                "detail": "If limb is cold, blue, pulseless, or numb, seek immediate emergency orthopedic evaluation.",
                "visual_hint": "Check pulse, warmth, sensation, and movement in digits"
            },
            {
                "step_num": 3,
                "title": "Apply R.I.C.E. Protocol for Sprains & Closed Injuries",
                "action": "R - Rest limb. I - Ice wrapped in towel for 15–20 mins every 2 hours. C - Compress with elastic bandage (snug, not tight). E - Elevate above heart level.",
                "detail": "Significantly curbs acute inflammatory edema and hematoma expansion.",
                "visual_hint": "Rest ➔ Ice 20 mins ➔ Compress bandage ➔ Elevate above heart"
            },
            {
                "step_num": 4,
                "title": "Splinting if Transporting Without EMS",
                "action": "Pad rigid object (cardboard, folded magazine, splint) and secure above and below the injured joint with cloth or tape.",
                "detail": "Do not tie splint bandages too tightly; re-check distal circulation after splinting.",
                "visual_hint": "Rigid padded splint above and below joint ➔ Recheck pulse"
            }
        ],
        "recovery_or_monitoring": "Open compound fractures (bone visible) or deformed joints require immediate ER evaluation, X-ray imaging, and tetanus prophylaxis.",
        "citations": "American Academy of Orthopaedic Surgeons (AAOS) First Aid Guidelines"
    }
}


def get_all_first_aid_cards() -> Dict[str, Any]:
    """Returns all first-aid emergency flashcards categorized and indexed."""
    categories = {
        "all": {"title": "All Cards", "icon": "📚", "count": len(FIRST_AID_CARDS_CATALOG)},
        "life_threatening": {"title": "🚨 Life-Threatening Emergencies", "icon": "🚨", "cards": []},
        "trauma": {"title": "🩸 Trauma & Bleeding", "icon": "🩸", "cards": []},
        "medical_crisis": {"title": "⚡ Medical Crises", "icon": "⚡", "cards": []},
        "everyday_injuries": {"title": "🩹 Everyday Injuries", "icon": "🩹", "cards": []}
    }

    card_summaries = []
    for cid, cdata in FIRST_AID_CARDS_CATALOG.items():
        summary_obj = {
            "id": cid,
            "title": cdata["title"],
            "category": cdata["category"],
            "category_label": cdata["category_label"],
            "icon": cdata["icon"],
            "priority": cdata["priority"],
            "summary": cdata["summary"],
            "call_emergency_first": cdata["call_emergency_first"],
            "has_metronome": bool(cdata.get("metronome_bpm")),
            "step_count": len(cdata["steps"])
        }
        card_summaries.append(summary_obj)
        cat_key = cdata["category"]
        if cat_key in categories:
            categories[cat_key]["cards"].append(summary_obj)

    return {
        "success": True,
        "total_cards": len(FIRST_AID_CARDS_CATALOG),
        "categories": categories,
        "cards": card_summaries
    }


def get_first_aid_card(card_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full detailed protocol for a single first aid card."""
    if not card_id:
        return None
    key = card_id.lower().strip()
    card = FIRST_AID_CARDS_CATALOG.get(key)
    if not card:
        # Search by partial match
        for cid, cdata in FIRST_AID_CARDS_CATALOG.items():
            if key in cid or key in cdata["title"].lower():
                card = cdata
                break
    if not card:
        return None
    return {
        "success": True,
        "card": card
    }


STOP_WORDS = {
    "how", "to", "do", "for", "an", "a", "the", "in", "on", "of", "with", 
    "and", "or", "is", "are", "can", "what", "you", "me", "if", "it", "at", 
    "by", "as", "be", "this", "that", "from", "my", "your", "we", "give", 
    "help", "need", "please", "i", "instructions", "protocol", "protocols",
    "card", "cards", "action", "steps", "guidance", "first", "aid"
}


def search_first_aid_cards(query: str) -> List[Dict[str, Any]]:
    """Searches first aid catalog using keyword and synonym matching with tokenized word scoring."""
    if not query:
        return []
    clean_q = query.lower().strip()
    raw_words = [w for w in re.split(r'[\s,;:?./-]+', clean_q) if len(w) > 1]
    words = [w for w in raw_words if w not in STOP_WORDS]
    if not words:
        words = raw_words
    if not words:
        return []

    # Common clinical synonyms mapping
    synonyms_map = {
        "cpr": ["cardiac", "arrest", "resuscitation", "compression", "compressions", "chest", "unresponsive", "metronome"],
        "heimlich": ["choking", "airway", "throat", "obstruction", "back blows", "slaps"],
        "choking": ["heimlich", "airway", "throat", "obstruction", "back blows"],
        "burn": ["scald", "heat", "thermal", "fire", "blister", "scalds", "burns", "cool"],
        "burns": ["scald", "heat", "thermal", "fire", "blister", "scalds", "burn", "cool"],
        "sprain": ["fracture", "rice", "joint", "ankle", "twist", "splint", "strain", "broken", "bone"],
        "sprains": ["fracture", "rice", "joint", "ankle", "twist", "splint", "strain", "broken", "bone"],
        "bleeding": ["hemorrhage", "tourniquet", "blood", "wound", "pressure", "bleeding"],
        "epipen": ["anaphylaxis", "allergic", "allergy", "epinephrine", "hives", "shock"],
        "anaphylaxis": ["epipen", "allergic", "allergy", "epinephrine", "hives", "swelling"],
        "fast": ["stroke", "drooping", "slurred", "arm weakness", "brain", "infarct"],
        "stroke": ["fast", "drooping", "slurred", "speech", "arm weakness", "brain"],
        "cold": ["hypothermia", "frostbite", "shivering", "rewarming", "ice", "freezing"],
        "sugar": ["hypoglycemia", "diabetic", "glucose", "insulin", "diabetes"],
        "heat": ["heatstroke", "exhaustion", "cooling", "hyperthermia", "sunstroke"]
    }

    # Expand words with synonyms
    expanded_words = set(words)
    for w in words:
        if w in synonyms_map:
            expanded_words.update(synonyms_map[w])

    is_pediatric_query = any(pw in clean_q for pw in ["infant", "baby", "child", "pediatric", "toddler"])

    results = []
    for cid, cdata in FIRST_AID_CARDS_CATALOG.items():
        score = 0
        title_lower = cdata["title"].lower()
        summary_lower = cdata["summary"].lower()
        cat_lower = cdata["category"].lower()
        cid_clean = cid.lower().replace("_", " ")
        primary_matched_words = set()

        # Full exact query in title or summary
        if clean_q in title_lower:
            score += 120
            primary_matched_words.update(words)
        elif clean_q in summary_lower:
            score += 50

        # Direct word matches in primary fields (Title, ID, Summary)
        for w in words:
            word_hit_primary = False
            
            # Title match (Highest clinical priority)
            if re.search(r'\b' + re.escape(w) + r'\b', title_lower):
                score += 100
                word_hit_primary = True
            elif w in title_lower:
                score += 40
                word_hit_primary = True
            
            # Normalized Card ID match
            if re.search(r'\b' + re.escape(w) + r'\b', cid_clean):
                score += 80
                word_hit_primary = True
            elif w in cid_clean:
                score += 30
                word_hit_primary = True
                
            # Summary match
            if re.search(r'\b' + re.escape(w) + r'\b', summary_lower):
                score += 35
                word_hit_primary = True
            elif w in summary_lower:
                score += 15
                word_hit_primary = True
                
            if w in cat_lower:
                score += 10
                word_hit_primary = True

            # Step title match (Important action headers)
            for step in cdata.get("steps", []):
                s_title = step.get("title", "").lower()
                if re.search(r'\b' + re.escape(w) + r'\b', s_title):
                    score += 20
                    word_hit_primary = True
                    break
                elif w in s_title:
                    score += 10
                    word_hit_primary = True
                    break

            # Step action details (Incidental step match)
            for step in cdata.get("steps", []):
                s_action = step.get("action", "").lower()
                if re.search(r'\b' + re.escape(w) + r'\b', s_action) or w in s_action:
                    score += 6
                    break

            # Prohibited / DO NOTs match (Low weight to prevent counter-intent ranking)
            for donot in cdata.get("critical_donots", []):
                if re.search(r'\b' + re.escape(w) + r'\b', donot.lower()) or w in donot.lower():
                    score += 2
                    break

            if word_hit_primary:
                primary_matched_words.add(w)

        # Coordinate matching bonus ONLY for primary clinical matches
        if len(primary_matched_words) > 1:
            score += (len(primary_matched_words) ** 2) * 35

        # Synonym matches (Secondary capped weight)
        synonym_only_words = expanded_words - set(words)
        synonym_score = 0
        for w in synonym_only_words:
            if re.search(r'\b' + re.escape(w) + r'\b', title_lower):
                synonym_score += 15
            elif re.search(r'\b' + re.escape(w) + r'\b', cid_clean):
                synonym_score += 12
            elif re.search(r'\b' + re.escape(w) + r'\b', summary_lower):
                synonym_score += 6
        score += min(25, synonym_score)

        # Adult vs Pediatric bias
        if not is_pediatric_query and "adult" in cid:
            score += 35
        elif not is_pediatric_query and ("infant" in cid or "pediatric" in cid):
            score -= 25
        elif is_pediatric_query and ("infant" in cid or "pediatric" in cid):
            score += 60

        if score > 0:
            results.append({
                "id": cid,
                "title": cdata["title"],
                "category": cdata["category"],
                "category_label": cdata["category_label"],
                "icon": cdata["icon"],
                "priority": cdata["priority"],
                "summary": cdata["summary"],
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


