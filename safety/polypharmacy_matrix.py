"""
Multi-Drug Interaction & Polypharmacy Matrix Safety Engine.
Provides comprehensive risk stratification for Drug-Drug, Drug-Condition, and Drug-Food interactions.
Enforces FDA, WHO, and clinical pharmacology consensus guardrails.
"""

import re
from typing import List, Dict, Any, Tuple, Optional

# Comprehensive Clinical Polypharmacy Interaction Database
# Format: Tuple of normalized lowercase terms sorted alphabetically
DRUG_INTERACTIONS_DB: Dict[Tuple[str, str], Dict[str, Any]] = {
    # 1. Anticoagulants & NSAIDs (Major Bleeding)
    ("ibuprofen", "warfarin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Gastrointestinal Bleeding & Hemorrhage Risk",
        "mechanism": "Ibuprofen inhibits platelet COX-1 and causes gastric mucosal erosion, while Warfarin inhibits vitamin K-dependent clotting factors, drastically multiplying hemorrhage risk.",
        "effects": "High risk of gastrointestinal bleeding, hematuria, prolonged bleeding time, and internal hemorrhage.",
        "action": "Avoid concurrent use. Use non-NSAID alternatives (e.g. Acetaminophen under medical guidance) and consult your doctor immediately."
    },
    ("aspirin", "warfarin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Bleeding & Anticoagulant Potentiation",
        "mechanism": "Dual inhibition of platelet aggregation and coagulation cascade leading to severe hemorrhagic diathesis.",
        "effects": "Major systemic bleeding, gastrointestinal ulceration, cerebral hemorrhage.",
        "action": "Strictly contraindicated unless prescribed by a cardiologist for specific mechanical heart valve or vascular indications."
    },
    ("apixaban", "ibuprofen"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Major Bleeding Risk with Direct Oral Anticoagulant (DOAC)",
        "mechanism": "Additive antiplatelet and direct factor Xa inhibition.",
        "effects": "Marked increase in spontaneous major bleeding and gastrointestinal ulceration.",
        "action": "Avoid NSAIDs with DOACs (Eliquis/Xarelto). Consult physician or pharmacist for safe pain management."
    },
    ("naproxen", "warfarin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Gastrointestinal Hemorrhage Hazard",
        "mechanism": "Potent long-acting NSAID antiplatelet effect combined with vitamin K antagonism.",
        "effects": "High risk of severe stomach ulcers and uncontrolled bleeding.",
        "action": "Do not combine. Seek physician consultation."
    },

    # 2. ACE Inhibitors / ARBs & Potassium / Potassium-Sparing Diuretics
    ("lisinopril", "potassium"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Life-Threatening Hyperkalemia & Cardiac Arrhythmia Risk",
        "mechanism": "ACE inhibitors reduce aldosterone secretion, decreasing renal potassium excretion; supplemental potassium causes rapid toxic serum accumulation.",
        "effects": "Severe hyperkalemia (>5.5 mEq/L), muscle weakness, bradycardia, fatal ventricular fibrillation.",
        "action": "Avoid potassium supplements and potassium-based salt substitutes unless prescribed with regular serum electrolyte monitoring."
    },
    ("losartan", "potassium"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Hyperkalemia Hazard with Angiotensin Receptor Blocker",
        "mechanism": "ARBs suppress aldosterone production, significantly reducing renal potassium clearance.",
        "effects": "Dangerous elevation in serum potassium, cardiac conduction abnormalities.",
        "action": "Do not take potassium supplements with Losartan without explicit nephrology/cardiology supervision."
    },
    ("lisinopril", "spironolactone"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Dual Potassium-Sparing Hyperkalemia Risk",
        "mechanism": "Combined inhibition of aldosterone synthesis and aldosterone receptor blockade.",
        "effects": "Dangerous hyperkalemia and acute kidney stress, especially in dehydrated patients.",
        "action": "Requires frequent serum potassium and creatinine blood monitoring."
    },
    ("ibuprofen", "lisinopril"): {
        "severity": "MODERATE",
        "type": "drug_drug",
        "title": "Reduced Antihypertensive Efficacy & Acute Renal Stress",
        "mechanism": "NSAIDs inhibit renal prostaglandins, causing sodium retention and blunting ACE-inhibitor blood pressure reduction.",
        "effects": "Elevated blood pressure, reduced glomerular filtration, and potential acute kidney injury.",
        "action": "Limit NSAID duration. Monitor blood pressure and renal function regularly."
    },

    # 3. Antidepressants, Triptans & Opioids (Serotonin Syndrome)
    ("sertraline", "tramadol"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Life-Threatening Serotonin Syndrome & Seizure Risk",
        "mechanism": "Both agents inhibit serotonin reuptake while Tramadol lowers seizure threshold and acts on mu-opioid receptors.",
        "effects": "Serotonin syndrome (hyperthermia, agitation, muscle rigidity, tremor, hyperreflexia), and increased seizure risk.",
        "action": "Avoid co-administration. Contact prescribing physician for alternative analgesic options."
    },
    ("fluoxetine", "sumatriptan"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Serotonin Toxicity Risk (SSRI + Triptan)",
        "mechanism": "Excessive 5-HT receptor stimulation from combined serotonin reuptake inhibition and 5-HT1B/1D agonist activity.",
        "effects": "Mental status changes, neuromuscular hyperactivity, autonomic instability.",
        "action": "Use with extreme caution under physician supervision. Seek emergency care if confusion or shivering occurs."
    },
    ("paroxetine", "tramadol"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Serotonin Syndrome & CYP2D6 Metabolic Blockade",
        "mechanism": "Paroxetine potently inhibits CYP2D6 metabolism of Tramadol, elevating toxic serotonin concentrations.",
        "effects": "Severe autonomic storm, hyperpyrexia, confusion, delirium.",
        "action": "Contraindicated. Consult healthcare provider."
    },

    # 4. Central Nervous System Depressants (Fatal Respiratory Depression)
    ("alcohol", "alprazolam"): {
        "severity": "MAJOR",
        "type": "drug_substance",
        "title": "Fatal CNS & Respiratory Depression Risk",
        "mechanism": "Synergistic GABA-A receptor potentiation causing profound central nervous system and medullary respiratory center suppression.",
        "effects": "Profound sedation, coma, respiratory arrest, and fatal overdose.",
        "action": "Strictly avoid all alcohol consumption while taking benzodiazepines (Xanax)."
    },
    ("alcohol", "lorazepam"): {
        "severity": "MAJOR",
        "type": "drug_substance",
        "title": "Profound Sedation & Respiratory Arrest Hazard",
        "mechanism": "Additive central depressant action on brainstem respiratory centers.",
        "effects": "Severe loss of consciousness, hypoventilation, airway collapse.",
        "action": "Do not consume alcoholic beverages."
    },
    ("oxycodone", "xanax"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "FDA Black Box Warning: Fatal Opioid + Benzodiazepine Interaction",
        "mechanism": "Dual suppression of central respiratory drive and protective airway reflexes.",
        "effects": "Extreme somnolence, respiratory depression, coma, and death.",
        "action": "Strictly contraindicated unless under specialized inpatient palliative supervision."
    },

    # 5. Cardiovascular, Statins & Anti-Infectives
    ("atorvastatin", "clarithromycin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Statin Toxicity & Rhabdomyolysis Risk",
        "mechanism": "Clarithromycin is a potent CYP3A4 inhibitor that increases Atorvastatin plasma exposure by over 400%.",
        "effects": "Severe myopathy, muscle breakdown (rhabdomyolysis), acute renal failure, and liver enzyme elevation.",
        "action": "Temporarily suspend Atorvastatin therapy during Clarithromycin course as directed by your physician."
    },
    ("atorvastatin", "grapefruit"): {
        "severity": "MODERATE",
        "type": "drug_food",
        "title": "Statin Overdose Risk via Intestinal CYP3A4 Inhibition",
        "mechanism": "Grapefruit furanocoumarins irreversibly inhibit intestinal CYP3A4, elevating circulating statin levels.",
        "effects": "Increased incidence of muscle aches, cramps, and elevated liver enzymes.",
        "action": "Avoid large quantities of grapefruit or grapefruit juice while taking Atorvastatin or Simvastatin."
    },
    ("amiodarone", "digoxin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Life-Threatening Digoxin Toxicity & Severe Bradycardia",
        "mechanism": "Amiodarone inhibits P-glycoprotein renal and biliary transport of Digoxin, doubling serum Digoxin concentrations.",
        "effects": "Digoxin toxicity: visual disturbances (yellow halos), nausea, fatal ventricular arrhythmias, severe heart block.",
        "action": "Requires 50% Digoxin dose reduction and close serum drug level monitoring."
    },

    # 6. Metabolic & Diabetes Interventions
    ("alcohol", "metformin"): {
        "severity": "MAJOR",
        "type": "drug_substance",
        "title": "Lactic Acidosis Hazard",
        "mechanism": "Alcohol impairs hepatic gluconeogenesis and lactate clearance, potentiating Metformin's inhibition of mitochondrial respiration.",
        "effects": "Severe lactic acidosis (nausea, deep rapid breathing, severe abdominal pain, hypothermia, high mortality).",
        "action": "Avoid excessive or binge alcohol intake while taking Metformin."
    },
    ("contrast", "metformin"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Contrast-Induced Nephropathy & Lactic Acidosis",
        "mechanism": "Iodinated radiopaque contrast can cause transient renal impairment, leading to acute Metformin accumulation.",
        "effects": "High risk of acute kidney injury and fatal lactic acidosis.",
        "action": "Withhold Metformin 48 hours before/after contrast imaging until renal function is verified normal."
    },
    ("atenolol", "insulin"): {
        "severity": "MODERATE",
        "type": "drug_drug",
        "title": "Masking of Hypoglycemia Symptoms",
        "mechanism": "Beta-blockers block adrenergic tachycardia and tremor responses that alert patients to low blood sugar.",
        "effects": "Unrecognized severe hypoglycemia (diaphoresis/sweating is usually the only remaining symptom).",
        "action": "Perform frequent blood glucose testing if combining beta-blockers and insulin."
    },

    # 7. Antibiotics, Minerals & Chelation
    ("calcium", "ciprofloxacin"): {
        "severity": "MODERATE",
        "type": "drug_food",
        "title": "Fluoroquinolone Chelation & Treatment Failure",
        "mechanism": "Polyvalent cations (calcium, iron, magnesium, aluminum) bind Ciprofloxacin in GI tract, forming insoluble chelates.",
        "effects": "Up to 90% reduction in antibiotic absorption leading to clinical infection failure.",
        "action": "Take Ciprofloxacin at least 2 hours before or 6 hours after calcium supplements, dairy, or antacids."
    },
    ("dairy", "doxycycline"): {
        "severity": "MODERATE",
        "type": "drug_food",
        "title": "Tetracycline Absorption Inhibition",
        "mechanism": "Calcium in milk and dairy products binds Doxycycline.",
        "effects": "Significantly impaired antibiotic bioavailability.",
        "action": "Space dairy intake 2 to 3 hours away from Doxycycline doses."
    },
    ("alcohol", "metronidazole"): {
        "severity": "MAJOR",
        "type": "drug_substance",
        "title": "Disulfiram-Like Toxic Reaction",
        "mechanism": "Metronidazole inhibits acetaldehyde dehydrogenase, causing rapid toxic acetaldehyde accumulation.",
        "effects": "Severe flushing, throbbing headache, violent vomiting, tachycardia, and chest tightness.",
        "action": "Strictly avoid alcohol during Metronidazole therapy and for at least 48 hours after the last dose."
    },

    # 8. High-Risk Immunosuppressants & Mood Stabilizers
    ("ibuprofen", "lithium"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Lithium Toxicity Hazard",
        "mechanism": "NSAIDs decrease renal prostaglandin synthesis, reducing renal clearance of lithium by 30–60%.",
        "effects": "Lithium toxicity: ataxia, coarse tremors, hyperreflexia, renal impairment, seizures, and coma.",
        "action": "Avoid NSAIDs. Use acetaminophen under medical guidance and monitor serum lithium levels."
    },
    ("ibuprofen", "methotrexate"): {
        "severity": "MAJOR",
        "type": "drug_drug",
        "title": "Severe Bone Marrow Suppression & Methotrexate Toxicity",
        "mechanism": "NSAIDs compete for renal tubular secretion, drastically elevating serum Methotrexate levels.",
        "effects": "Severe pancytopenia, bone marrow failure, stomatitis, and acute nephrotoxicity.",
        "action": "Strictly contraindicated without specialized oncologic/rheumatologic clearance."
    }
}

# Drug-Condition Contraindication Rules
DRUG_CONDITION_CONTRAINDICATIONS: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("asthma", "propranolol"): {
        "severity": "MAJOR",
        "type": "drug_condition",
        "title": "Contraindicated: Beta-Blocker Induced Bronchospasm",
        "mechanism": "Non-selective beta-1 and beta-2 blockade blocks bronchial dilation, triggering severe, potentially fatal bronchospasm.",
        "effects": "Acute asthma exacerbation, severe wheezing, life-threatening airway obstruction.",
        "action": "Non-selective beta-blockers are contraindicated in asthma. Cardioselective agents or alternative classes should be used."
    },
    ("asthma", "ibuprofen"): {
        "severity": "MAJOR",
        "type": "drug_condition",
        "title": "Aspirin/NSAID-Exacerbated Respiratory Disease (AERD)",
        "mechanism": "Inhibition of COX-1 shunts arachidonic acid metabolism into the 5-lipoxygenase pathway, increasing cysteinyl leukotrienes.",
        "effects": "Severe bronchospasm, rhinorrhea, and acute asthmatic distress within hours of ingestion.",
        "action": "Avoid NSAIDs if you have a history of aspirin/NSAID-sensitive asthma."
    },
    ("ckd", "ibuprofen"): {
        "severity": "MAJOR",
        "type": "drug_condition",
        "title": "Contraindicated in Chronic Kidney Disease (CKD)",
        "mechanism": "NSAID inhibition of vasodilatory prostaglandins reduces renal blood flow and causes ischemic medullary injury.",
        "effects": "Rapid decline in eGFR, fluid retention, worsening hypertension, and acute on chronic renal failure.",
        "action": "Avoid NSAIDs in kidney disease. Acetaminophen is generally preferred for mild pain."
    },
    ("ulcer", "ibuprofen"): {
        "severity": "MAJOR",
        "type": "drug_condition",
        "title": "Contraindicated in Peptic Ulcer Disease",
        "mechanism": "Direct topical irritation and systemic inhibition of gastroprotective prostaglandin synthesis.",
        "effects": "Gastric ulcer perforation, severe upper GI hemorrhage, melena.",
        "action": "Avoid all NSAIDs in active ulcer disease. Consult physician."
    },
    ("hypertension", "pseudoephedrine"): {
        "severity": "MODERATE",
        "type": "drug_condition",
        "title": "Blood Pressure Spike Hazard with Oral Decongestants",
        "mechanism": "Alpha-1 adrenergic vasoconstriction elevates systemic vascular resistance.",
        "effects": "Significant elevation of systolic and diastolic blood pressure, palpitations.",
        "action": "Use saline nasal sprays or consult physician before taking oral decongestants (Sudafed) if you have high blood pressure."
    },
    ("pregnancy", "lisinopril"): {
        "severity": "MAJOR",
        "type": "drug_condition",
        "title": "FDA Black Box: Teratogenic Fetal Toxicity in Pregnancy",
        "mechanism": "ACE inhibitors cause severe disruption of fetal renal development and cranial ossification.",
        "effects": "Fetal renal failure, oligohydramnios, skeletal deformities, and neonatal death.",
        "action": "Strictly contraindicated in pregnancy. Switch to pregnancy-safe antihypertensives (Labetalol, Methyldopa) immediately."
    }
}

# Standardized Drug / Condition Alias Dictionary
DRUG_ALIASES = {
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "brufen": "ibuprofen",
    "tylenol": "paracetamol",
    "acetaminophen": "paracetamol",
    "panadol": "paracetamol",
    "aleve": "naproxen",
    "bayer": "aspirin",
    "ecotrin": "aspirin",
    "eliquis": "apixaban",
    "xarelto": "rivaroxaban",
    "coumadin": "warfarin",
    "jantoven": "warfarin",
    "zestril": "lisinopril",
    "prinivil": "lisinopril",
    "cozaar": "losartan",
    "aldactone": "spironolactone",
    "lipitor": "atorvastatin",
    "zocor": "simvastatin",
    "crestor": "rosuvastatin",
    "zoloft": "sertraline",
    "prozac": "fluoxetine",
    "paxil": "paroxetine",
    "ultram": "tramadol",
    "imitrex": "sumatriptan",
    "xanax": "alprazolam",
    "ativan": "lorazepam",
    "valium": "diazepam",
    "oxycontin": "oxycodone",
    "percocet": "oxycodone",
    "glucophage": "metformin",
    "inderal": "propranolol",
    "tenormin": "atenolol",
    "cipro": "ciprofloxacin",
    "biaxin": "clarithromycin",
    "flagyl": "metronidazole",
    "vibramycin": "doxycycline",
    "sudafed": "pseudoephedrine",
    "eskalith": "lithium",
    "trexall": "methotrexate",
    "potassium supplement": "potassium",
    "potassium pills": "potassium",
    "salt substitute": "potassium",
    "grapefruit juice": "grapefruit",
    "milk": "dairy",
    "kidney disease": "ckd",
    "chronic kidney disease": "ckd",
    "renal disease": "ckd",
    "peptic ulcer": "ulcer",
    "stomach ulcer": "ulcer",
    "high blood pressure": "hypertension",
    "pregnant": "pregnancy"
}

def normalize_entity(name: str) -> str:
    """Normalize medication or clinical condition name to canonical standardized key."""
    cleaned = name.lower().strip()
    return DRUG_ALIASES.get(cleaned, cleaned)

def check_polypharmacy_interactions(entities: List[str]) -> Dict[str, Any]:
    """
    Evaluates pairwise interactions across all supplied medications, conditions, and foods.
    Returns structured interaction analysis with severity stratification and safety advice.
    """
    if not entities or len(entities) < 2:
        return {
            "has_interactions": False,
            "severity_summary": "NONE",
            "total_interactions": 0,
            "interactions": [],
            "checked_entities": entities or []
        }

    normalized = [normalize_entity(e) for e in entities if e and e.strip()]
    unique_entities = list(set(normalized))
    
    found_interactions = []
    highest_severity = "NONE"
    severity_rank = {"MAJOR": 3, "MODERATE": 2, "MINOR": 1, "NONE": 0}

    # Check Pairwise Drug-Drug / Drug-Food / Drug-Substance Interactions
    for i in range(len(unique_entities)):
        for j in range(i + 1, len(unique_entities)):
            pair = tuple(sorted([unique_entities[i], unique_entities[j]]))
            
            # 1. Check in Drug-Drug / Food DB
            if pair in DRUG_INTERACTIONS_DB:
                data = DRUG_INTERACTIONS_DB[pair]
                found_interactions.append({
                    "item_1": pair[0].title(),
                    "item_2": pair[1].title(),
                    "severity": data["severity"],
                    "type": data["type"],
                    "title": data["title"],
                    "mechanism": data["mechanism"],
                    "effects": data["effects"],
                    "action": data["action"]
                })
                if severity_rank[data["severity"]] > severity_rank[highest_severity]:
                    highest_severity = data["severity"]

            # 2. Check in Drug-Condition DB
            if pair in DRUG_CONDITION_CONTRAINDICATIONS:
                data = DRUG_CONDITION_CONTRAINDICATIONS[pair]
                found_interactions.append({
                    "item_1": pair[0].title(),
                    "item_2": pair[1].title(),
                    "severity": data["severity"],
                    "type": data["type"],
                    "title": data["title"],
                    "mechanism": data["mechanism"],
                    "effects": data["effects"],
                    "action": data["action"]
                })
                if severity_rank[data["severity"]] > severity_rank[highest_severity]:
                    highest_severity = data["severity"]

    # Sort interactions by severity (Major first)
    found_interactions.sort(key=lambda x: severity_rank.get(x["severity"], 0), reverse=True)

    return {
        "has_interactions": len(found_interactions) > 0,
        "severity_summary": highest_severity,
        "total_interactions": len(found_interactions),
        "interactions": found_interactions,
        "checked_entities": [e.title() for e in unique_entities]
    }

def scan_text_for_polypharmacy(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts medications and conditions from freeform text and evaluates interactions.
    """
    if not text or not isinstance(text, str):
        return None

    lower_text = text.lower()
    all_known_entities = list(DRUG_ALIASES.keys()) + [
        "ibuprofen", "warfarin", "aspirin", "apixaban", "naproxen", "lisinopril",
        "potassium", "losartan", "spironolactone", "sertraline", "tramadol",
        "fluoxetine", "sumatriptan", "paroxetine", "alcohol", "alprazolam",
        "lorazepam", "oxycodone", "atorvastatin", "clarithromycin", "grapefruit",
        "amiodarone", "digoxin", "metformin", "contrast", "atenolol", "insulin",
        "calcium", "ciprofloxacin", "dairy", "doxycycline", "metronidazole",
        "lithium", "methotrexate", "asthma", "propranolol", "ckd", "ulcer",
        "hypertension", "pseudoephedrine", "pregnancy"
    ]

    detected = []
    for ent in set(all_known_entities):
        pattern = r'\b' + re.escape(ent) + r'\b'
        if re.search(pattern, lower_text):
            detected.append(ent)

    if len(detected) >= 2:
        res = check_polypharmacy_interactions(detected)
        if res["has_interactions"]:
            return res

    return None
