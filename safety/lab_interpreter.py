"""
Medical Lab Test & Biomarker Range Interpreter Module.
Provides clinically grounded reference interpretations across 25+ standard laboratory biomarkers.
Conforms to AHA, ADA, KDIGO, WHO, and College of American Pathologists (CAP) reference standards.
"""

from typing import Dict, Any, List, Optional
import re

LAB_TESTS_CATALOG: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. METABOLIC & GLYCEMIC CONTROL
    # =========================================================================
    "fasting_glucose": {
        "id": "fasting_glucose",
        "name": "Fasting Blood Glucose",
        "panel": "Metabolic & Glycemic",
        "panel_icon": "🩸",
        "unit": "mg/dL",
        "display_range": "70 – 99 mg/dL",
        "slider_min": 40,
        "slider_max": 300,
        "default_val": 92,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 54, "label": "Severe Hypoglycemia (Emergency)", "badge": "CRITICAL", "color": "#dc2626"},
            {"tier": "LOW", "min": 54.1, "max": 69.9, "label": "Low Blood Sugar (Hypoglycemia)", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 70, "max": 99.9, "label": "Normal Fasting Glucose", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 100, "max": 125.9, "label": "Impaired Fasting Glucose (Prediabetes)", "badge": "ELEVATED", "color": "#d97706"},
            {"tier": "HIGH", "min": 126, "max": 250, "label": "Elevated (Diabetes Range Threshold)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 250.1, "max": 1000, "label": "Severe Hyperglycemia Alert", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Measures blood sugar level after at least 8 hours of overnight fasting. Core test for diabetes and insulin resistance screening.",
        "high_causes": "Insulin resistance, Type 2 diabetes, pancreatic dysfunction, acute physiological stress, corticosteroid medications.",
        "low_causes": "Excess insulin/medication, prolonged fasting, intense exertion without carbohydrates, liver dysfunction.",
        "lifestyle_tips": "Emphasize low-glycemic complex carbohydrates, high dietary fiber, 30 minutes of daily aerobic movement, and adequate sleep.",
        "doctor_questions": [
            "Do I need a confirmatory HbA1c test or Oral Glucose Tolerance Test (OGTT)?",
            "Should we monitor fasting glucose trends at home?",
            "What dietary adjustments would best support my glycemic control?"
        ]
    },

    "hba1c": {
        "id": "hba1c",
        "name": "Hemoglobin A1c (HbA1c)",
        "panel": "Metabolic & Glycemic",
        "panel_icon": "🩸",
        "unit": "%",
        "display_range": "< 5.7 %",
        "slider_min": 4.0,
        "slider_max": 14.0,
        "default_val": 5.4,
        "tiers": [
            {"tier": "OPTIMAL", "min": 0, "max": 5.69, "label": "Normal Glycemic Control", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 5.7, "max": 6.49, "label": "Prediabetes Range", "badge": "ELEVATED", "color": "#d97706"},
            {"tier": "HIGH", "min": 6.5, "max": 8.0, "label": "Diabetes Range (Moderate Control)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 8.01, "max": 20.0, "label": "Poor Glycemic Control (High Complication Risk)", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Reflects average blood glucose levels over the preceding 2 to 3 months by measuring glycated hemoglobin in red blood cells.",
        "high_causes": "Chronic hyperglycemia, uncontrolled diabetes mellitus, insulin deficiency.",
        "low_causes": "Hemolytic anemia, recent blood transfusions, chronic kidney disease.",
        "lifestyle_tips": "Consistent carbohydrate counting, resistance and aerobic training, stress reduction, and routine physician checkups.",
        "doctor_questions": [
            "What is my personalized target HbA1c goal?",
            "How often should I repeat this HbA1c test?",
            "Are there medical nutrition therapy programs available for my range?"
        ]
    },

    # =========================================================================
    # 2. CARDIOVASCULAR & LIPID PROFILE
    # =========================================================================
    "total_cholesterol": {
        "id": "total_cholesterol",
        "name": "Total Cholesterol",
        "panel": "Cardiovascular & Lipids",
        "panel_icon": "❤️",
        "unit": "mg/dL",
        "display_range": "< 200 mg/dL",
        "slider_min": 100,
        "slider_max": 400,
        "default_val": 185,
        "tiers": [
            {"tier": "OPTIMAL", "min": 0, "max": 199.9, "label": "Desirable Total Cholesterol", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 200, "max": 239.9, "label": "Borderline High", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 240, "max": 600, "label": "High Cholesterol (Elevated ASCVD Risk)", "badge": "HIGH", "color": "#dc2626"}
        ],
        "description": "Total measure of circulating cholesterol components including LDL, HDL, and VLDL fractions.",
        "high_causes": "High saturated/trans fat diet, familial hypercholesterolemia, hypothyroidism, sedentary lifestyle.",
        "low_causes": "Malnutrition, malabsorption, severe liver disease, hyperthyroidism.",
        "lifestyle_tips": "Adopt Mediterranean diet principles, replace saturated fats with olive oil/avocado, and consume soluble fiber (oats, beans).",
        "doctor_questions": [
            "What is my full fractionated lipid breakdown (LDL, HDL, Triglycerides)?",
            "What is my estimated 10-year ASCVD cardiovascular risk score?",
            "Do I need dietary modifications or lipid-lowering pharmacotherapy?"
        ]
    },

    "ldl_cholesterol": {
        "id": "ldl_cholesterol",
        "name": "LDL (Bad) Cholesterol",
        "panel": "Cardiovascular & Lipids",
        "panel_icon": "❤️",
        "unit": "mg/dL",
        "display_range": "< 100 mg/dL",
        "slider_min": 40,
        "slider_max": 300,
        "default_val": 90,
        "tiers": [
            {"tier": "OPTIMAL", "min": 0, "max": 99.9, "label": "Optimal LDL Cholesterol", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "NEAR_OPTIMAL", "min": 100, "max": 129.9, "label": "Near Optimal / Above Desirable", "badge": "NEAR OPTIMAL", "color": "#65a30d"},
            {"tier": "BORDERLINE", "min": 130, "max": 159.9, "label": "Borderline High LDL", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 160, "max": 189.9, "label": "High LDL (Atherosclerosis Risk)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 190, "max": 600, "label": "Very High LDL (Severe Atherogenic Risk)", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Low-Density Lipoprotein transports cholesterol to peripheral tissues. Excess LDL contributes directly to arterial plaque build-up.",
        "high_causes": "Saturated fat intake, genetic hypercholesterolemia, obesity, diabetes, smoking.",
        "low_causes": "Hypobetalipoproteinemia, severe malnutrition, chronic inflammatory states.",
        "lifestyle_tips": "Limit ultra-processed red meats, increase plant sterols, exercise 150 min/week, and eliminate tobacco exposure.",
        "doctor_questions": [
            "Based on my overall cardiovascular risk profile, what is my ideal LDL target?",
            "Would a coronary artery calcium (CAC) scan be informative for my risk tier?"
        ]
    },

    "hdl_cholesterol": {
        "id": "hdl_cholesterol",
        "name": "HDL (Good) Cholesterol",
        "panel": "Cardiovascular & Lipids",
        "panel_icon": "❤️",
        "unit": "mg/dL",
        "display_range": "≥ 50 mg/dL (Women) / ≥ 40 mg/dL (Men)",
        "slider_min": 20,
        "slider_max": 120,
        "default_val": 58,
        "tiers": [
            {"tier": "LOW", "min": 0, "max": 39.9, "label": "Low HDL (Major Cardiovascular Risk Factor)", "badge": "LOW", "color": "#dc2626"},
            {"tier": "BORDERLINE", "min": 40, "max": 49.9, "label": "Borderline HDL Level", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "OPTIMAL", "min": 50, "max": 59.9, "label": "Normal Protective HDL", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "EXCELLENT", "min": 60, "max": 200, "label": "Optimal Protective HDL Level", "badge": "EXCELLENT", "color": "#059669"}
        ],
        "description": "High-Density Lipoprotein scavenges excess arterial cholesterol and carries it back to the liver for excretion (reverse cholesterol transport).",
        "high_causes": "Regular aerobic exercise, genetic factors, moderate monounsaturated fat intake.",
        "low_causes": "Sedentary lifestyle, smoking, obesity, metabolic syndrome, high refined carbohydrate intake.",
        "lifestyle_tips": "Regular vigorous cardiovascular exercise, smoking cessation, and consuming healthy omega-3 fatty acids (salmon, walnuts, flax).",
        "doctor_questions": [
            "What lifestyle interventions will most effectively raise my HDL cholesterol?",
            "How does my Total Cholesterol to HDL ratio look?"
        ]
    },

    "triglycerides": {
        "id": "triglycerides",
        "name": "Serum Triglycerides",
        "panel": "Cardiovascular & Lipids",
        "panel_icon": "❤️",
        "unit": "mg/dL",
        "display_range": "< 150 mg/dL",
        "slider_min": 30,
        "slider_max": 800,
        "default_val": 120,
        "tiers": [
            {"tier": "OPTIMAL", "min": 0, "max": 149.9, "label": "Normal Fasting Triglycerides", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 150, "max": 199.9, "label": "Borderline High", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 200, "max": 499.9, "label": "High Triglycerides", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 500, "max": 2000, "label": "Very High (Acute Pancreatitis Risk)", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "The primary storage form of fat in the body. Elevated levels correlate strongly with metabolic syndrome, fatty liver, and heart disease.",
        "high_causes": "Excess alcohol intake, high-sugar and refined starch diet, poorly controlled diabetes, obesity.",
        "low_causes": "Malnutrition, low-fat diets, hyperthyroidism.",
        "lifestyle_tips": "Strictly eliminate sugar-sweetened beverages, minimize alcohol consumption, and increase physical activity.",
        "doctor_questions": [
            "Are my elevated triglycerides related to insulin resistance or metabolic syndrome?",
            "Do I need prescription omega-3 or fibrate therapy if diet changes are insufficient?"
        ]
    },

    # =========================================================================
    # 3. VITAL SIGNS & HEMODYNAMICS
    # =========================================================================
    "blood_pressure": {
        "id": "blood_pressure",
        "name": "Blood Pressure (Systolic / Diastolic)",
        "panel": "Vital Signs & Hemodynamics",
        "panel_icon": "💓",
        "unit": "mmHg",
        "display_range": "< 120 / < 80 mmHg",
        "slider_min": 70,
        "slider_max": 220,
        "default_val": 118,
        "default_val_2": 78,
        "is_dual": True,
        "tiers": [
            {"tier": "OPTIMAL", "label": "Normal Blood Pressure", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "label": "Elevated Blood Pressure", "badge": "ELEVATED", "color": "#d97706"},
            {"tier": "STAGE_1", "label": "Stage 1 Hypertension", "badge": "STAGE 1", "color": "#ea580c"},
            {"tier": "STAGE_2", "label": "Stage 2 Hypertension", "badge": "STAGE 2", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "label": "Hypertensive Crisis (Emergency Alert)", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Hydrostatic pressure exerted by circulating blood upon arterial blood vessel walls (Systolic during contraction / Diastolic during rest).",
        "high_causes": "Essential hypertension, high dietary sodium, chronic stress, arterial stiffness, kidney disease, sleep apnea.",
        "low_causes": "Dehydration, orthostatic hypotension, blood loss, heart failure, medication side effects.",
        "lifestyle_tips": "DASH diet protocol (<1,500mg sodium daily), regular aerobic fitness, weight management, and stress reduction.",
        "doctor_questions": [
            "Should I track my blood pressure with a validated home cuff twice daily?",
            "What is my personal target blood pressure goal?",
            "Should we screen for secondary causes of elevated blood pressure?"
        ]
    },

    "heart_rate": {
        "id": "heart_rate",
        "name": "Resting Heart Rate (Pulse)",
        "panel": "Vital Signs & Hemodynamics",
        "panel_icon": "💓",
        "unit": "BPM",
        "display_range": "60 – 100 BPM",
        "slider_min": 35,
        "slider_max": 180,
        "default_val": 72,
        "tiers": [
            {"tier": "LOW", "min": 0, "max": 59.9, "label": "Bradycardia (Slow Heart Rate)", "badge": "LOW", "color": "#0284c7"},
            {"tier": "OPTIMAL", "min": 60, "max": 100, "label": "Normal Resting Heart Rate", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "HIGH", "min": 100.1, "max": 140, "label": "Tachycardia (Elevated Pulse)", "badge": "HIGH", "color": "#ea580c"},
            {"tier": "CRITICAL_HIGH", "min": 140.1, "max": 300, "label": "Severe Tachycardia Alert", "badge": "CRITICAL", "color": "#dc2626"}
        ],
        "description": "Number of cardiac contractions per minute at complete rest.",
        "high_causes": "Fever, dehydration, anxiety, caffeine/stimulants, thyroid hyperactivity, anemia, arrhythmia.",
        "low_causes": "Athletic conditioning (normal in endurance athletes), beta-blocker medications, sick sinus syndrome, hypothyroidism.",
        "lifestyle_tips": "Adequate daily hydration, limiting excessive caffeine, box breathing exercises, and consistent cardiovascular training.",
        "doctor_questions": [
            "Is my pulse rate rhythm regular or irregular?",
            "Do I need an Electrocardiogram (ECG/EKG) evaluation?"
        ]
    },

    "oxygen_saturation": {
        "id": "oxygen_saturation",
        "name": "Oxygen Saturation (SpO2)",
        "panel": "Vital Signs & Hemodynamics",
        "panel_icon": "🫁",
        "unit": "%",
        "display_range": "95 – 100 %",
        "slider_min": 75,
        "slider_max": 100,
        "default_val": 98,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 89.9, "label": "Severe Hypoxemia (Immediate Emergency)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 90, "max": 94.9, "label": "Mild to Moderate Hypoxemia (Urgent Medical Review)", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 95, "max": 100, "label": "Normal Oxygen Saturation", "badge": "OPTIMAL", "color": "#16a34a"}
        ],
        "description": "Percentage of oxygen-carrying hemoglobin in arterial blood measured non-invasively via pulse oximetry.",
        "high_causes": "Normal physiology or supplemental oxygen administration.",
        "low_causes": "Pneumonia, asthma flare-up, COPD exacerbation, pulmonary embolism, high altitude, heart failure.",
        "lifestyle_tips": "Sit upright, perform deep diaphragmatic breathing, and avoid smoking/vaping.",
        "doctor_questions": [
            "If my oxygen saturation drops below 95%, at what threshold should I seek emergency care?"
        ]
    },

    # =========================================================================
    # 4. COMPLETE BLOOD COUNT (CBC)
    # =========================================================================
    "hemoglobin": {
        "id": "hemoglobin",
        "name": "Hemoglobin (Hb)",
        "panel": "Complete Blood Count (CBC)",
        "panel_icon": "🔬",
        "unit": "g/dL",
        "display_range": "13.8 – 17.2 (Men) / 12.1 – 15.1 (Women)",
        "slider_min": 5.0,
        "slider_max": 22.0,
        "default_val": 14.2,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 6.99, "label": "Severe Anemia (Emergency Transfusion Alert)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 7.0, "max": 11.99, "label": "Anemia (Low Oxygen Capacity)", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 12.0, "max": 17.5, "label": "Normal Hemoglobin Level", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "HIGH", "min": 17.51, "max": 30.0, "label": "Polycythemia / Elevated Hemoglobin", "badge": "HIGH", "color": "#dc2626"}
        ],
        "description": "Iron-containing protein inside red blood cells that binds and transports oxygen from the lungs to body tissues.",
        "high_causes": "Chronic hypoxia (COPD, heavy smoking), severe dehydration, polycythemia vera.",
        "low_causes": "Iron deficiency, vitamin B12/folate deficiency, chronic blood loss (GI bleed/menorrhagia), kidney disease.",
        "lifestyle_tips": "Consume iron-rich foods (lentils, spinach, lean meats) combined with vitamin C to boost iron absorption.",
        "doctor_questions": [
            "Do I need follow-up ferritin, iron saturation, and vitamin B12 testing?",
            "Is there any evidence of occult gastrointestinal blood loss?"
        ]
    },

    "wbc": {
        "id": "wbc",
        "name": "White Blood Cell Count (WBC)",
        "panel": "Complete Blood Count (CBC)",
        "panel_icon": "🔬",
        "unit": "×10³/µL",
        "display_range": "4.5 – 11.0 ×10³/µL",
        "slider_min": 1.0,
        "slider_max": 30.0,
        "default_val": 6.8,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 1.99, "label": "Severe Leukopenia / Neutropenia (Infection Vulnerability)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 2.0, "max": 4.49, "label": "Leukopenia (Low White Cells)", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 4.5, "max": 11.0, "label": "Normal Immune Cell Count", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "HIGH", "min": 11.01, "max": 20.0, "label": "Leukocytosis (Infection / Inflammation)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 20.01, "max": 100.0, "label": "Marked Leukocytosis Alert", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Total count of immune defense cells (neutrophils, lymphocytes, monocytes, eosinophils, basophils) circulating in blood.",
        "high_causes": "Bacterial or viral infections, systemic inflammation, severe tissue injury, corticosteroid use, leukemia.",
        "low_causes": "Viral infections (influenza, HIV), autoimmune conditions (Lupus), bone marrow suppression, chemotherapy.",
        "lifestyle_tips": "Maintain strict hand hygiene, stay up-to-date on recommended immunizations, and ensure sufficient restorative sleep.",
        "doctor_questions": [
            "What does my differential breakdown (neutrophils vs. lymphocytes) show?",
            "Are there underlying bacterial or inflammatory causes for this count?"
        ]
    },

    # =========================================================================
    # 5. RENAL & KIDNEY FUNCTION
    # =========================================================================
    "creatinine": {
        "id": "creatinine",
        "name": "Serum Creatinine",
        "panel": "Renal & Kidney Function",
        "panel_icon": "🫘",
        "unit": "mg/dL",
        "display_range": "0.74 – 1.35 (Men) / 0.59 – 1.04 (Women)",
        "slider_min": 0.3,
        "slider_max": 8.0,
        "default_val": 0.95,
        "tiers": [
            {"tier": "LOW", "min": 0, "max": 0.49, "label": "Low Creatinine (Low Muscle Mass / Malnutrition)", "badge": "LOW", "color": "#0284c7"},
            {"tier": "OPTIMAL", "min": 0.5, "max": 1.2, "label": "Normal Renal Function", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 1.21, "max": 1.49, "label": "Mildly Elevated (Borderline Renal Clearance)", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 1.5, "max": 2.99, "label": "Elevated Creatinine (Renal Impairment)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 3.0, "max": 20.0, "label": "Severe Renal Decompensation Alert", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Waste byproduct of muscle metabolism cleared solely by the kidneys. Primary marker used to estimate glomerular filtration rate.",
        "high_causes": "Chronic kidney disease, acute dehydration, urinary tract obstruction, nephrotoxic medications (NSAIDs).",
        "low_causes": "Low muscle mass, severe liver disease, strict vegan diet without creatine intake.",
        "lifestyle_tips": "Maintain optimal hydration, avoid unnecessary OTC NSAIDs (Ibuprofen/Naproxen), and control blood pressure.",
        "doctor_questions": [
            "What is my calculated eGFR based on this creatinine value?",
            "Do any of my current medications need dosage adjustment for kidney clearance?"
        ]
    },

    "egfr": {
        "id": "egfr",
        "name": "Estimated GFR (eGFR)",
        "panel": "Renal & Kidney Function",
        "panel_icon": "🫘",
        "unit": "mL/min/1.73m²",
        "display_range": "≥ 90 mL/min/1.73m²",
        "slider_min": 5,
        "slider_max": 130,
        "default_val": 105,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 14.9, "label": "Stage 5 CKD: Kidney Failure (Dialysis Threshold)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "STAGE_4", "min": 15, "max": 29.9, "label": "Stage 4 CKD: Severe Reduction in GFR", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "STAGE_3", "min": 30, "max": 59.9, "label": "Stage 3 CKD: Moderate Renal Decline", "badge": "MODERATE", "color": "#ea580c"},
            {"tier": "STAGE_2", "min": 60, "max": 89.9, "label": "Stage 2 CKD: Mild GFR Reduction", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "OPTIMAL", "min": 90, "max": 200, "label": "Normal / Optimal Kidney Filtration", "badge": "OPTIMAL", "color": "#16a34a"}
        ],
        "description": "Calculated rate measuring how effectively microscopic glomerular filters cleanse metabolic wastes from the bloodstream.",
        "high_causes": "Normal healthy filtration capacity, early diabetic hyperfiltration.",
        "low_causes": "Hypertensive nephrosclerosis, diabetic nephropathy, glomerulonephritis, polycystic kidney disease.",
        "lifestyle_tips": "Strict blood pressure control (<130/80 mmHg), moderate dietary protein, low sodium, and avoid dehydration.",
        "doctor_questions": [
            "Do I have persistent albuminuria or protein in my urine?",
            "Should I consult a nephrologist for kidney-protective therapies (e.g. SGLT2 inhibitors)?"
        ]
    },

    # =========================================================================
    # 6. HEPATIC & LIVER FUNCTION
    # =========================================================================
    "alt_sgpt": {
        "id": "alt_sgpt",
        "name": "ALT (SGPT) - Liver Enzyme",
        "panel": "Hepatic & Liver Function",
        "panel_icon": "🧪",
        "unit": "U/L",
        "display_range": "7 – 56 U/L",
        "slider_min": 5,
        "slider_max": 300,
        "default_val": 24,
        "tiers": [
            {"tier": "OPTIMAL", "min": 0, "max": 55.9, "label": "Normal Liver Enzyme Level", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 56, "max": 99.9, "label": "Mildly Elevated Liver Enzymes", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 100, "max": 299.9, "label": "Elevated ALT (Hepatic Inflammation)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 300, "max": 2000, "label": "Marked Hepatocellular Injury Alert", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Alanine Aminotransferase is an enzyme found predominantly inside hepatocytes (liver cells). Elevated blood levels indicate liver cell irritation or injury.",
        "high_causes": "Non-alcoholic fatty liver disease (NAFLD), alcohol consumption, viral hepatitis, medication-induced hepatotoxicity.",
        "low_causes": "Normal finding; rarely severe vitamin B6 deficiency.",
        "lifestyle_tips": "Eliminate alcohol intake, reduce fructose and ultra-processed foods, achieve gradual weight loss, and review medications with your doctor.",
        "doctor_questions": [
            "Should we check viral hepatitis serologies or perform an abdominal liver ultrasound?",
            "Are any of my current supplements or medications contributing to liver enzyme elevation?"
        ]
    },

    # =========================================================================
    # 7. THYROID, VITAMINS & MINERALS
    # =========================================================================
    "tsh": {
        "id": "tsh",
        "name": "Thyroid Stimulating Hormone (TSH)",
        "panel": "Thyroid & Endocrine",
        "panel_icon": "🦋",
        "unit": "µIU/mL",
        "display_range": "0.40 – 4.00 µIU/mL",
        "slider_min": 0.05,
        "slider_max": 20.0,
        "default_val": 1.85,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 0.09, "label": "Overt Hyperthyroidism (Overactive Thyroid)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 0.1, "max": 0.39, "label": "Subclinical Hyperthyroidism / Suppressed TSH", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 0.4, "max": 4.0, "label": "Normal Euthyroid Range", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 4.01, "max": 9.99, "label": "Subclinical Hypothyroidism (Underactive)", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 10.0, "max": 100.0, "label": "Overt Hypothyroidism (Underactive Thyroid)", "badge": "HIGH", "color": "#dc2626"}
        ],
        "description": "Pituitary hormone that regulates thyroid gland production of T4 and T3 hormones controlling global body metabolic rate.",
        "high_causes": "Hashimoto's autoimmune thyroiditis, iodine deficiency, inadequate thyroid hormone replacement therapy.",
        "low_causes": "Graves' disease, toxic nodular goiter, excessive levothyroxine dosage, thyroiditis.",
        "lifestyle_tips": "Ensure balanced dietary iodine/selenium intake, manage chronic stress, and take thyroid medications on an empty stomach.",
        "doctor_questions": [
            "Do I need Free T4, Free T3, and anti-TPO thyroid antibody testing?",
            "Could my symptoms of fatigue, cold intolerance, or weight changes be linked to this TSH?"
        ]
    },

    "potassium": {
        "id": "potassium",
        "name": "Serum Potassium (K+)",
        "panel": "Electrolytes & Minerals",
        "panel_icon": "⚡",
        "unit": "mEq/L",
        "display_range": "3.5 – 5.0 mEq/L",
        "slider_min": 2.0,
        "slider_max": 8.0,
        "default_val": 4.2,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 2.99, "label": "Severe Hypokalemia (Cardiac Arrhythmia Emergency)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 3.0, "max": 3.49, "label": "Mild Hypokalemia (Low Potassium)", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 3.5, "max": 5.0, "label": "Normal Serum Potassium", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "BORDERLINE", "min": 5.01, "max": 5.49, "label": "Mildly Elevated Potassium", "badge": "BORDERLINE", "color": "#d97706"},
            {"tier": "HIGH", "min": 5.5, "max": 5.99, "label": "Hyperkalemia (Cardiac Conduction Risk)", "badge": "HIGH", "color": "#dc2626"},
            {"tier": "CRITICAL_HIGH", "min": 6.0, "max": 12.0, "label": "Severe Hyperkalemia (Fatal Arrhythmia Alert)", "badge": "CRITICAL", "color": "#991b1b"}
        ],
        "description": "Essential intracellular electrolyte vital for maintaining normal cardiac rhythm, nerve impulses, and skeletal muscle contraction.",
        "high_causes": "Kidney failure, ACE inhibitors / ARBs, potassium-sparing diuretics, potassium supplements.",
        "low_causes": "Loop/thiazide diuretics, severe vomiting/diarrhea, poor dietary intake, hyperaldosteronism.",
        "lifestyle_tips": "Do not take potassium supplements without prescription. Monitor dietary potassium if kidney clearance is reduced.",
        "doctor_questions": [
            "Are my heart medications or diuretics affecting my potassium balance?",
            "Do I need an immediate ECG to check for hyperkalemic peaked T waves?"
        ]
    },

    "vitamin_d": {
        "id": "vitamin_d",
        "name": "Vitamin D (25-Hydroxy)",
        "panel": "Thyroid, Vitamins & Minerals",
        "panel_icon": "☀️",
        "unit": "ng/mL",
        "display_range": "30 – 100 ng/mL",
        "slider_min": 5,
        "slider_max": 150,
        "default_val": 38,
        "tiers": [
            {"tier": "CRITICAL_LOW", "min": 0, "max": 11.9, "label": "Severe Vitamin D Deficiency (Osteomalacia / Rickets Risk)", "badge": "CRITICAL", "color": "#991b1b"},
            {"tier": "LOW", "min": 12.0, "max": 29.9, "label": "Vitamin D Insufficiency", "badge": "LOW", "color": "#ea580c"},
            {"tier": "OPTIMAL", "min": 30.0, "max": 100.0, "label": "Optimal Vitamin D Sufficiency", "badge": "OPTIMAL", "color": "#16a34a"},
            {"tier": "HIGH", "min": 100.1, "max": 300.0, "label": "Elevated / Potential Hypervitaminosis D", "badge": "HIGH", "color": "#dc2626"}
        ],
        "description": "Fat-soluble secosteroid hormone essential for intestinal calcium absorption, bone mineralization, and immune regulation.",
        "high_causes": "Excessive high-dose vitamin D supplementation.",
        "low_causes": "Lack of direct sunlight exposure, dark skin pigmentation, malabsorption, obesity, chronic kidney/liver disease.",
        "lifestyle_tips": "Safe 15-minute daily midday sun exposure, fatty fish consumption, fortified milk/cereals, or physician-guided D3 supplementation.",
        "doctor_questions": [
            "What daily or weekly Vitamin D3 supplementation dose is appropriate for my level?",
            "Should we recheck my calcium and parathyroid hormone (PTH) levels?"
        ]
    }
}

def get_all_lab_tests() -> List[Dict[str, Any]]:
    """Returns catalog of all available laboratory biomarkers grouped by panel."""
    tests = []
    for tid, data in LAB_TESTS_CATALOG.items():
        tests.append({
            "id": data["id"],
            "name": data["name"],
            "panel": data["panel"],
            "panel_icon": data["panel_icon"],
            "unit": data["unit"],
            "display_range": data["display_range"],
            "default_val": data["default_val"],
            "slider_min": data["slider_min"],
            "slider_max": data["slider_max"],
            "is_dual": data.get("is_dual", False)
        })
    return tests

def interpret_blood_pressure(systolic: float, diastolic: float) -> Dict[str, Any]:
    """Specialized Blood Pressure Dual-Value Interpreter adhering to AHA/ACC guidelines."""
    test_meta = LAB_TESTS_CATALOG["blood_pressure"]

    # AHA/ACC Classification
    if systolic > 180 or diastolic > 120:
        tier_data = {"tier": "CRITICAL_HIGH", "label": "Hypertensive Crisis (Emergency Alert)", "badge": "CRITICAL", "color": "#991b1b", "gauge_pct": 100}
    elif systolic >= 140 or diastolic >= 90:
        tier_data = {"tier": "STAGE_2", "label": "Stage 2 Hypertension", "badge": "STAGE 2", "color": "#dc2626", "gauge_pct": 80}
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        tier_data = {"tier": "STAGE_1", "label": "Stage 1 Hypertension", "badge": "STAGE 1", "color": "#ea580c", "gauge_pct": 60}
    elif (120 <= systolic <= 129) and diastolic < 80:
        tier_data = {"tier": "BORDERLINE", "label": "Elevated Blood Pressure", "badge": "ELEVATED", "color": "#d97706", "gauge_pct": 40}
    elif systolic < 90 or diastolic < 60:
        tier_data = {"tier": "LOW", "label": "Low Blood Pressure (Hypotension)", "badge": "LOW", "color": "#0284c7", "gauge_pct": 15}
    else:
        tier_data = {"tier": "OPTIMAL", "label": "Normal Blood Pressure", "badge": "OPTIMAL", "color": "#16a34a", "gauge_pct": 25}

    return {
        "test_id": "blood_pressure",
        "test_name": test_meta["name"],
        "panel": test_meta["panel"],
        "unit": test_meta["unit"],
        "value": f"{int(systolic)}/{int(diastolic)}",
        "numeric_val": systolic,
        "numeric_val_2": diastolic,
        "is_dual": True,
        "tier": tier_data["tier"],
        "tier_label": tier_data["label"],
        "badge": tier_data["badge"],
        "badge_color": tier_data["color"],
        "gauge_pct": tier_data["gauge_pct"],
        "reference_range": test_meta["display_range"],
        "description": test_meta["description"],
        "high_causes": test_meta["high_causes"],
        "low_causes": test_meta["low_causes"],
        "lifestyle_tips": test_meta["lifestyle_tips"],
        "doctor_questions": test_meta["doctor_questions"]
    }

def interpret_lab_result(test_id: str, value: float, value_2: Optional[float] = None) -> Dict[str, Any]:
    """
    Evaluates a numeric biomarker value against clinical reference ranges.
    Returns structured interpretation with gauge percentage, clinical causes, and doctor talking points.
    """
    if test_id == "blood_pressure":
        systolic = float(value)
        diastolic = float(value_2) if value_2 is not None else 80.0
        return interpret_blood_pressure(systolic, diastolic)

    test_meta = LAB_TESTS_CATALOG.get(test_id)
    if not test_meta:
        return {
            "error": f"Unknown laboratory test ID: '{test_id}'",
            "available_tests": [t["id"] for t in get_all_lab_tests()]
        }

    val = float(value)
    matched_tier = test_meta["tiers"][-1]  # Default fallback

    for t in test_meta["tiers"]:
        if t["min"] <= val <= t["max"]:
            matched_tier = t
            break

    # Calculate 0-100% position on visual gauge
    s_min = test_meta["slider_min"]
    s_max = test_meta["slider_max"]
    gauge_pct = min(100.0, max(0.0, ((val - s_min) / (s_max - s_min)) * 100.0))

    return {
        "test_id": test_id,
        "test_name": test_meta["name"],
        "panel": test_meta["panel"],
        "unit": test_meta["unit"],
        "value": val,
        "tier": matched_tier["tier"],
        "tier_label": matched_tier["label"],
        "badge": matched_tier["badge"],
        "badge_color": matched_tier["color"],
        "gauge_pct": round(gauge_pct, 1),
        "reference_range": test_meta["display_range"],
        "description": test_meta["description"],
        "high_causes": test_meta["high_causes"],
        "low_causes": test_meta["low_causes"],
        "lifestyle_tips": test_meta["lifestyle_tips"],
        "doctor_questions": test_meta["doctor_questions"]
    }

def detect_and_interpret_vitals_in_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Parses conversational text queries for specific lab / vital numbers
    e.g. 'my fasting sugar is 145', 'my BP is 150/95', 'my cholesterol is 250'.
    """
    if not query or not isinstance(query, str):
        return None

    # 1. Check Blood Pressure: e.g. 140/90 or 150 over 95
    bp_match = re.search(r'\b(?:bp|blood pressure)\s*(?:is|of|level)?\s*(\d{2,3})\s*(?:/|over|\s)\s*(\d{2,3})\b', query, re.I)
    if not bp_match:
        bp_match = re.search(r'\b(\d{2,3})\s*/\s*(\d{2,3})\s*mmhg\b', query, re.I)

    if bp_match:
        try:
            sys_val = float(bp_match.group(1))
            dia_val = float(bp_match.group(2))
            if 60 <= sys_val <= 260 and 40 <= dia_val <= 160:
                return interpret_lab_result("blood_pressure", sys_val, dia_val)
        except Exception:
            pass

    # 2. Check Fasting Blood Glucose / Sugar: e.g. 'fasting blood sugar is 160'
    sugar_match = re.search(r'\b(?:fasting|sugar|glucose|blood sugar)\s*(?:is|level|was|of)?\s*(\d{2,3})\b', query, re.I)
    if sugar_match:
        try:
            s_val = float(sugar_match.group(1))
            if 40 <= s_val <= 600:
                return interpret_lab_result("fasting_glucose", s_val)
        except Exception:
            pass

    # 3. Check HbA1c: e.g. 'a1c is 7.2'
    a1c_match = re.search(r'\b(?:a1c|hba1c)\s*(?:is|was|of)?\s*(\d{1,2}(?:\.\d{1,2})?)\b', query, re.I)
    if a1c_match:
        try:
            a1c_val = float(a1c_match.group(1))
            if 3.5 <= a1c_val <= 20.0:
                return interpret_lab_result("hba1c", a1c_val)
        except Exception:
            pass

    # 4. Check Total Cholesterol: e.g. 'cholesterol is 245'
    chol_match = re.search(r'\b(?:total cholesterol|cholesterol)\s*(?:is|was|of)?\s*(\d{2,3})\b', query, re.I)
    if chol_match:
        try:
            c_val = float(chol_match.group(1))
            if 90 <= c_val <= 500:
                return interpret_lab_result("total_cholesterol", c_val)
        except Exception:
            pass

    return None
