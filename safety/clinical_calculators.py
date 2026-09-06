"""
Evidence-Based Clinical Risk Calculators & Vital Tools Engine.
Provides validated clinical equations, risk stratification algorithms,
and clinical guideline recommendations for:
1. ASCVD 10-Year Cardiovascular Disease Risk (ACC/AHA Pooled Cohort Equations)
2. CHA2DS2-VASc Atrial Fibrillation Stroke Risk (ESC/AHA Guidelines)
3. eGFR CKD-EPI 2021 Race-Free Creatinine Equation (KDIGO Guidelines)
4. FIB-4 Index for Non-Invasive Hepatic Fibrosis (AASLD/EASL Guidelines)
5. CURB-65 Community-Acquired Pneumonia Mortality & Triage (BTS Guidelines)
6. Wells' Criteria for Deep Vein Thrombosis (DVT)
7. qSOFA Quick Bedside Sepsis Organ Failure Screener (SCCM/ESICM Sepsis-3)
8. FINDRISC 10-Year Type 2 Diabetes Risk Score
9. PHQ-9 Depression Severity & GAD-7 Anxiety Screening Scales
10. Anthropometric & Metabolic Vital Suite (BMI, Devine IBW, Mosteller BSA, Mifflin-St Jeor BMR/TDEE)
"""

from typing import Dict, Any, List, Optional
import math
import re


# =============================================================================
# 1. ASCVD 10-Year Cardiovascular Risk Calculator (ACC/AHA 2013/2018)
# =============================================================================

def calculate_ascvd(
    age: float,
    sex: str,
    race: str = "white_other",
    systolic_bp: float = 120.0,
    total_cholesterol: float = 200.0,
    hdl_cholesterol: float = 50.0,
    is_diabetic: bool = False,
    is_smoker: bool = False,
    on_hypertension_treatment: bool = False
) -> Dict[str, Any]:
    """
    Computes 10-year risk of first hard ASCVD event (nonfatal MI, coronary heart disease death, or fatal/nonfatal stroke)
    using the validated 2013 ACC/AHA Pooled Cohort Equations.
    """
    age = max(20.0, min(79.0, float(age)))
    sbp = max(90.0, min(200.0, float(systolic_bp)))
    tc = max(130.0, min(320.0, float(total_cholesterol)))
    hdl = max(20.0, min(100.0, float(hdl_cholesterol)))
    is_female = sex.lower().startswith("f") or sex.lower() == "woman"
    is_aa = "african" in race.lower() or "black" in race.lower()

    ln_age = math.log(age)
    ln_tc = math.log(tc)
    ln_hdl = math.log(hdl)
    ln_sbp = math.log(sbp)

    if is_female:
        if is_aa:
            # African American Women
            mean_coeff = 86.61
            s10 = 0.9533
            sbp_term = (29.291 * ln_sbp - 6.432 * ln_age * ln_sbp) if on_hypertension_treatment else (27.820 * ln_sbp - 6.087 * ln_age * ln_sbp)
            indiv_sum = (
                17.114 * ln_age +
                0.940 * ln_tc -
                18.920 * ln_hdl +
                4.475 * ln_age * ln_hdl +
                sbp_term +
                (0.691 if is_smoker else 0.0) +
                (0.874 if is_diabetic else 0.0)
            )
        else:
            # White / Other Women
            mean_coeff = -29.18
            s10 = 0.9665
            sbp_term = (2.019 * ln_sbp) if on_hypertension_treatment else (1.957 * ln_sbp)
            indiv_sum = (
                -29.799 * ln_age +
                4.884 * (ln_age ** 2) +
                13.540 * ln_tc -
                3.114 * ln_age * ln_tc -
                13.578 * ln_hdl +
                3.149 * ln_age * ln_hdl +
                sbp_term +
                (7.574 if is_smoker else 0.0) -
                (1.665 * ln_age if is_smoker else 0.0) +
                (0.661 if is_diabetic else 0.0)
            )
    else:
        if is_aa:
            # African American Men
            mean_coeff = 19.54
            s10 = 0.8954
            sbp_term = (1.916 * ln_sbp) if on_hypertension_treatment else (1.809 * ln_sbp)
            indiv_sum = (
                2.469 * ln_age +
                0.302 * ln_tc -
                0.307 * ln_hdl +
                sbp_term +
                (0.549 if is_smoker else 0.0) +
                (0.645 if is_diabetic else 0.0)
            )
        else:
            # White / Other Men
            mean_coeff = 61.18
            s10 = 0.9144
            sbp_term = (1.797 * ln_sbp) if on_hypertension_treatment else (1.764 * ln_sbp)
            indiv_sum = (
                12.344 * ln_age +
                11.853 * ln_tc -
                2.664 * ln_age * ln_tc -
                7.990 * ln_hdl +
                1.769 * ln_age * ln_hdl +
                sbp_term +
                (7.837 if is_smoker else 0.0) -
                (1.795 * ln_age if is_smoker else 0.0) +
                (0.658 if is_diabetic else 0.0)
            )

    exponent = math.exp(indiv_sum - mean_coeff)
    raw_risk = (1.0 - (s10 ** exponent)) * 100.0
    risk_percent = max(0.1, min(99.0, round(raw_risk, 1)))

    if risk_percent < 5.0:
        tier = "LOW"
        tier_label = "🟢 Low Risk (<5.0%)"
        statin_rec = "Emphasize healthy lifestyle habits (Mediterranean diet, 150 min aerobic exercise/week). Statin therapy typically not indicated unless LDL-C ≥ 190 mg/dL."
    elif risk_percent < 7.5:
        tier = "BORDERLINE"
        tier_label = "🟡 Borderline Risk (5.0% - 7.4%)"
        statin_rec = "If risk-enhancing factors present (family history of premature ASCVD, metabolic syndrome, hs-CRP ≥ 2 mg/L, CAC > 0), consider moderate-intensity statin."
    elif risk_percent < 20.0:
        tier = "INTERMEDIATE"
        tier_label = "🟠 Intermediate Risk (7.5% - 19.9%)"
        statin_rec = "Moderate-intensity statin therapy recommended (reduce LDL-C by 30–49%). Consider Coronary Artery Calcium (CAC) scan if decision is uncertain."
    else:
        tier = "HIGH"
        tier_label = "🔴 High Risk (≥20.0%)"
        statin_rec = "High-intensity statin therapy strongly recommended (Atorvastatin 40–80 mg or Rosuvastatin 20–40 mg to reduce LDL-C by ≥50%). Aggressive blood pressure & lipid management."

    return {
        "calculator_id": "ascvd",
        "calculator_title": "ASCVD 10-Year Cardiovascular Disease Risk",
        "score": risk_percent,
        "score_unit": "%",
        "tier": tier,
        "tier_label": tier_label,
        "statin_recommendation": statin_rec,
        "parameters": {
            "Age": f"{int(age)} years",
            "Gender": "Female" if is_female else "Male",
            "Race": "African American" if is_aa else "White / Other",
            "Systolic BP": f"{int(sbp)} mmHg ({'Treated' if on_hypertension_treatment else 'Untreated'})",
            "Total Cholesterol": f"{int(tc)} mg/dL",
            "HDL Cholesterol": f"{int(hdl)} mg/dL",
            "Diabetes": "Yes" if is_diabetic else "No",
            "Smoking": "Yes" if is_smoker else "No"
        },
        "citations": "2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol"
    }


# =============================================================================
# 2. CHA2DS2-VASc Score for AFib Stroke Risk (ESC 2020 / AHA 2019)
# =============================================================================

def calculate_chads_vasc(
    age: int,
    is_female: bool,
    congestive_heart_failure: bool = False,
    hypertension: bool = False,
    diabetes: bool = False,
    stroke_or_tia: bool = False,
    vascular_disease: bool = False
) -> Dict[str, Any]:
    """
    Computes CHA2DS2-VASc score for stroke risk stratification in non-valvular atrial fibrillation.
    """
    score = 0
    breakdown = []

    if congestive_heart_failure:
        score += 1
        breakdown.append("Congestive Heart Failure / LVEF ≤40% (+1)")
    if hypertension:
        score += 1
        breakdown.append("Hypertension (+1)")
    
    if age >= 75:
        score += 2
        breakdown.append(f"Age ≥75 ({age} yrs) (+2)")
    elif age >= 65:
        score += 1
        breakdown.append(f"Age 65-74 ({age} yrs) (+1)")

    if diabetes:
        score += 1
        breakdown.append("Diabetes Mellitus (+1)")
    if stroke_or_tia:
        score += 2
        breakdown.append("Prior Stroke / TIA / Thromboembolism (+2)")
    if vascular_disease:
        score += 1
        breakdown.append("Vascular Disease (Prior MI, PAD, Aortic Plaque) (+1)")
    if is_female:
        score += 1
        breakdown.append("Female Sex (+1)")

    stroke_rates = {
        0: "0.2%", 1: "0.6%", 2: "2.2%", 3: "3.2%", 4: "4.8%",
        5: "7.2%", 6: "9.7%", 7: "11.2%", 8: "12.5%", 9: "15.2%"
    }
    annual_rate = stroke_rates.get(min(9, score), ">15.2%")

    # Anticoagulation threshold: Men >= 2, Women >= 3 (or Men = 1, Women = 2 consider)
    adjusted_score = score - (1 if is_female else 0)
    if adjusted_score == 0:
        tier = "LOW"
        tier_label = "🟢 Low Risk (Score 0 in Men, 1 in Women)"
        anticoag_rec = "No antithrombotic therapy recommended (clinical benefit of anticoagulation does not outweigh bleeding risk)."
    elif adjusted_score == 1:
        tier = "MODERATE"
        tier_label = "🟡 Moderate Risk (Score 1 in Men, 2 in Women)"
        anticoag_rec = "Oral anticoagulation (DOAC preferred over Warfarin) should be considered based on individual bleeding risk (HAS-BLED) and patient preference."
    else:
        tier = "HIGH"
        tier_label = f"🔴 High Risk (Score ≥2 in Men, ≥3 in Women)"
        anticoag_rec = "Oral anticoagulation strongly recommended (DOACs: Apixaban, Rivaroxaban, Dabigatran, or Edoxaban preferred over Warfarin) to reduce ischemic stroke risk."

    return {
        "calculator_id": "chads_vasc",
        "calculator_title": "CHA₂DS₂-VASc AFib Stroke Risk Score",
        "score": score,
        "score_unit": "points",
        "annual_stroke_rate": annual_rate,
        "tier": tier,
        "tier_label": tier_label,
        "anticoagulation_recommendation": anticoag_rec,
        "breakdown": breakdown,
        "citations": "2020 ESC Guidelines for the diagnosis and management of atrial fibrillation"
    }


# =============================================================================
# 3. eGFR (CKD-EPI 2021 Race-Free Creatinine Equation)
# =============================================================================

def calculate_egfr_ckdepi(
    serum_creatinine: float,
    age: float,
    is_female: bool
) -> Dict[str, Any]:
    """
    Computes estimated Glomerular Filtration Rate (eGFR) using the 2021 CKD-EPI Race-Free Creatinine Equation.
    eGFR = 142 * min(Scr/kappa, 1)^alpha * max(Scr/kappa, 1)^(-1.200) * 0.9938^Age * (1.012 if female)
    """
    scr = max(0.2, min(20.0, float(serum_creatinine)))
    age = max(18.0, min(110.0, float(age)))

    kappa = 0.7 if is_female else 0.9
    alpha = -0.241 if is_female else -0.302
    gender_mult = 1.012 if is_female else 1.0

    scr_k = scr / kappa
    min_term = min(scr_k, 1.0) ** alpha
    max_term = max(scr_k, 1.0) ** (-1.200)
    age_term = 0.9938 ** age

    egfr_val = 142.0 * min_term * max_term * age_term * gender_mult
    egfr_rounded = round(egfr_val, 1)

    if egfr_rounded >= 90.0:
        stage = "G1"
        stage_desc = "Normal or High Kidney Function"
        tier = "NORMAL"
        tier_label = "🟢 G1: Normal or Elevated (≥90 mL/min/1.73m²)"
        advice = "Kidney function is within optimal reference range. Maintain normal hydration and routine annual screening."
    elif egfr_rounded >= 60.0:
        stage = "G2"
        stage_desc = "Mildly Decreased Kidney Function"
        tier = "MILD"
        tier_label = "🟡 G2: Mildly Decreased (60-89 mL/min/1.73m²)"
        advice = "Mild functional decline. Check for persistent albuminuria / proteinuria. Optimize blood pressure (<130/80 mmHg) and glycemic control."
    elif egfr_rounded >= 45.0:
        stage = "G3a"
        stage_desc = "Mild-to-Moderately Decreased"
        tier = "MODERATE"
        tier_label = "🟠 G3a: Mild-to-Moderate CKD (45-59 mL/min/1.73m²)"
        advice = "Early CKD Stage 3. Review medications (adjust Metformin if eGFR <45, avoid frequent NSAIDs). Screen for anemia and bone-mineral markers every 6–12 months."
    elif egfr_rounded >= 30.0:
        stage = "G3b"
        stage_desc = "Moderately-to-Severely Decreased"
        tier = "MODERATE_SEVERE"
        tier_label = "🟠 G3b: Moderate-to-Severe CKD (30-44 mL/min/1.73m²)"
        advice = "Moderate-to-Severe CKD. Metformin dose must be reduced (max 1000 mg/day; discontinue if <30). Discontinue NSAIDs. Strict dietary potassium and sodium monitoring."
    elif egfr_rounded >= 15.0:
        stage = "G4"
        stage_desc = "Severely Decreased (Approaching Kidney Failure)"
        tier = "SEVERE"
        tier_label = "🔴 G4: Severe CKD (15-29 mL/min/1.73m²)"
        advice = "Severe kidney impairment. Nephrology referral essential. Prepare for kidney replacement therapy / vascular access planning. Metformin contraindicated."
    else:
        stage = "G5"
        stage_desc = "Kidney Failure / End-Stage Renal Disease"
        tier = "CRITICAL"
        tier_label = "🔴 G5: Kidney Failure (<15 mL/min/1.73m²)"
        advice = "End-stage renal disease. Immediate nephrology evaluation for hemodialysis, peritoneal dialysis, or renal transplant evaluation."

    return {
        "calculator_id": "egfr",
        "calculator_title": "eGFR (CKD-EPI 2021 Race-Free Equation)",
        "score": egfr_rounded,
        "score_unit": "mL/min/1.73m²",
        "stage": stage,
        "stage_desc": stage_desc,
        "tier": tier,
        "tier_label": tier_label,
        "clinical_advice": advice,
        "parameters": {
            "Serum Creatinine": f"{scr} mg/dL",
            "Age": f"{int(age)} years",
            "Gender": "Female" if is_female else "Male"
        },
        "citations": "Inker LA, et al. New Creatinine- and Cystatin C–Based Equations to Estimate GFR without Race. NEJM 2021; 385:1737-1749"
    }


# =============================================================================
# 4. FIB-4 Index for Hepatic Fibrosis (AASLD/EASL)
# =============================================================================

def calculate_fib4(
    age: float,
    ast: float,
    alt: float,
    platelets: float
) -> Dict[str, Any]:
    """
    Computes FIB-4 Index for non-invasive liver fibrosis screening in NAFLD / Viral Hepatitis.
    FIB-4 = (Age * AST) / (Platelets * sqrt(ALT))
    where Platelets are in 10^9 / L (e.g. 200).
    """
    age = max(18.0, min(100.0, float(age)))
    ast = max(5.0, min(1000.0, float(ast)))
    alt = max(5.0, min(1000.0, float(alt)))
    plt = max(10.0, min(1000.0, float(platelets)))

    fib4_val = (age * ast) / (plt * math.sqrt(alt))
    fib4_rounded = round(fib4_val, 2)

    if fib4_rounded < 1.30:
        tier = "LOW"
        tier_label = "🟢 Low Risk of Advanced Fibrosis (<1.30)"
        rec = "High negative predictive value (>90%) for ruling out advanced fibrosis (F3-F4). Lifestyle modification, weight management, and repeat non-invasive screening in 2–3 years."
    elif fib4_rounded <= 2.67:
        tier = "INDETERMINATE"
        tier_label = "🟡 Indeterminate Risk (1.30 - 2.67)"
        rec = "Intermediate zone. Second-line non-invasive assessment recommended (Vibration-Controlled Transient Elastography / FibroScan or ELF test) to clarify fibrosis stage."
    else:
        tier = "HIGH"
        tier_label = "🔴 High Risk of Advanced Fibrosis / Cirrhosis (>2.67)"
        rec = "High probability of bridging fibrosis or cirrhosis (F3-F4). Prompt Hepatology / Gastroenterology referral recommended for comprehensive staging and portal hypertension screening."

    return {
        "calculator_id": "fib4",
        "calculator_title": "FIB-4 Index for Liver Fibrosis",
        "score": fib4_rounded,
        "score_unit": "index",
        "tier": tier,
        "tier_label": tier_label,
        "recommendation": rec,
        "parameters": {
            "Age": f"{int(age)} years",
            "AST": f"{ast} U/L",
            "ALT": f"{alt} U/L",
            "Platelets": f"{plt} × 10⁹/L"
        },
        "citations": "Sterling RK, et al. Development of a simple noninvasive index to predict significant fibrosis in patients with HIV/HCV coinfection. Hepatology 2006; 43:1317-1325"
    }


# =============================================================================
# 5. CURB-65 Pneumonia Severity Score (BTS Guidelines)
# =============================================================================

def calculate_curb65(
    confusion: bool,
    bun_mg_dl: float,
    respiratory_rate: int,
    systolic_bp: int,
    diastolic_bp: int,
    age: int
) -> Dict[str, Any]:
    """
    Computes CURB-65 score for community-acquired pneumonia 30-day mortality risk and triage site.
    """
    score = 0
    breakdown = []

    if confusion:
        score += 1
        breakdown.append("Confusion (AMTS ≤8 or new mental disorientation) (+1)")
    if bun_mg_dl > 19.0:
        score += 1
        breakdown.append(f"Urea / BUN >19 mg/dL ({bun_mg_dl} mg/dL) (+1)")
    if respiratory_rate >= 30:
        score += 1
        breakdown.append(f"Respiratory Rate ≥30 breaths/min ({respiratory_rate}/min) (+1)")
    if systolic_bp < 90 or diastolic_bp <= 60:
        score += 1
        breakdown.append(f"Hypotension (SBP <90 or DBP ≤60 mmHg) ({systolic_bp}/{diastolic_bp} mmHg) (+1)")
    if age >= 65:
        score += 1
        breakdown.append(f"Age ≥65 ({age} yrs) (+1)")

    if score <= 1:
        tier = "LOW"
        mortality = "0.7% - 2.1%"
        tier_label = f"🟢 Low Risk (Score {score}/5, Mortality {mortality})"
        triage = "Suitable for Outpatient / Home Treatment with oral empirical antimicrobial therapy (e.g. Amoxicillin or Macrolide) and close primary care follow-up."
    elif score == 2:
        tier = "MODERATE"
        mortality = "9.2%"
        tier_label = f"🟡 Moderate Risk (Score 2/5, Mortality {mortality})"
        triage = "Short Inpatient Hospital Admission or closely monitored Hospital-at-Home care recommended. Perform blood cultures and CXR."
    else:
        tier = "HIGH"
        mortality = "15% - 40%"
        tier_label = f"🔴 Severe / High Risk (Score {score}/5, Mortality {mortality})"
        triage = "Severe Community-Acquired Pneumonia. Urgent Inpatient Hospital Admission required; evaluate for immediate Intensive Care Unit (ICU) admission if score 4-5 or septic shock."

    return {
        "calculator_id": "curb65",
        "calculator_title": "CURB-65 Pneumonia Severity Score",
        "score": score,
        "score_unit": "points (max 5)",
        "mortality_risk": mortality,
        "tier": tier,
        "tier_label": tier_label,
        "triage_recommendation": triage,
        "breakdown": breakdown,
        "citations": "Lim WS, et al. Defining community acquired pneumonia severity on presentation to hospital: an international derivation and validation study. Thorax 2003; 58:377-382"
    }


# =============================================================================
# 6. Wells' Criteria for Deep Vein Thrombosis (DVT)
# =============================================================================

def calculate_wells_dvt(
    active_cancer: bool = False,
    paralysis_or_plaster: bool = False,
    bedridden_or_major_surgery: bool = False,
    localized_tenderness: bool = False,
    entire_leg_swollen: bool = False,
    calf_swelling_over_3cm: bool = False,
    pitting_edema: bool = False,
    collateral_superficial_veins: bool = False,
    previous_dvt: bool = False,
    alternative_diagnosis_likely: bool = False
) -> Dict[str, Any]:
    """
    Computes Wells' Score for Deep Vein Thrombosis (DVT) pre-test probability.
    """
    score = 0
    breakdown = []

    if active_cancer:
        score += 1
        breakdown.append("Active cancer (treatment ongoing or within 6 months) (+1)")
    if paralysis_or_plaster:
        score += 1
        breakdown.append("Paralysis, paresis, or recent plaster cast of lower extremity (+1)")
    if bedridden_or_major_surgery:
        score += 1
        breakdown.append("Recently bedridden ≥3 days or major surgery within 12 weeks (+1)")
    if localized_tenderness:
        score += 1
        breakdown.append("Localized tenderness along deep venous system (+1)")
    if entire_leg_swollen:
        score += 1
        breakdown.append("Entire leg swollen (+1)")
    if calf_swelling_over_3cm:
        score += 1
        breakdown.append("Calf swelling >3 cm compared with asymptomatic leg (+1)")
    if pitting_edema:
        score += 1
        breakdown.append("Pitting edema confined to symptomatic leg (+1)")
    if collateral_superficial_veins:
        score += 1
        breakdown.append("Collateral superficial non-varicose veins (+1)")
    if previous_dvt:
        score += 1
        breakdown.append("Previously documented DVT (+1)")
    if alternative_diagnosis_likely:
        score -= 2
        breakdown.append("Alternative diagnosis at least as likely as DVT (-2)")

    if score <= 0:
        tier = "LOW"
        tier_label = "🟢 DVT Unlikely / Low Probability (Score ≤0, ~3% Risk)"
        rec = "Order high-sensitivity D-Dimer test. If D-Dimer is negative (<500 ng/mL or age-adjusted cutoff), DVT is safely ruled out without ultrasound."
    elif score <= 2:
        tier = "MODERATE"
        tier_label = "🟡 Moderate Probability (Score 1-2, ~17% Risk)"
        rec = "Order high-sensitivity D-Dimer test and arrange Compression Duplex Ultrasonography if D-Dimer is elevated."
    else:
        tier = "HIGH"
        tier_label = "🔴 DVT Likely / High Probability (Score ≥3, ~75% Risk)"
        rec = "Immediate Compression Duplex Ultrasonography of the lower extremity indicated. Consider empiric anticoagulation if ultrasound is delayed >4 hours and no contraindications."

    return {
        "calculator_id": "wells_dvt",
        "calculator_title": "Wells' Criteria for Deep Vein Thrombosis",
        "score": score,
        "score_unit": "points",
        "tier": tier,
        "tier_label": tier_label,
        "diagnostic_pathway": rec,
        "breakdown": breakdown,
        "citations": "Wells PS, et al. Evaluation of D-dimer in the diagnosis of suspected deep-vein thrombosis. NEJM 2003; 349:1227-1235"
    }


# =============================================================================
# 7. qSOFA Quick Bedside Sepsis Screener (Sepsis-3)
# =============================================================================

def calculate_qsofa(
    respiratory_rate: int,
    altered_mentation: bool,
    systolic_bp: int
) -> Dict[str, Any]:
    """
    Computes quick Sepsis-related Organ Failure Assessment (qSOFA) score for bedside sepsis risk.
    """
    score = 0
    breakdown = []

    if respiratory_rate >= 22:
        score += 1
        breakdown.append(f"Tachypnea: Respiratory Rate ≥22 breaths/min ({respiratory_rate}/min) (+1)")
    if altered_mentation:
        score += 1
        breakdown.append("Altered Mentation: Glasgow Coma Scale <15 (+1)")
    if systolic_bp <= 100:
        score += 1
        breakdown.append(f"Hypotension: Systolic Blood Pressure ≤100 mmHg ({systolic_bp} mmHg) (+1)")

    if score >= 2:
        tier = "CRITICAL"
        tier_label = f"🔴 High Risk of Sepsis / In-Hospital Mortality (Score {score}/3)"
        rec = "CRITICAL SEPSIS ALERT: High probability of poor outcome. Initiate Sepsis Bundle immediately: Obtain blood cultures, serum lactate level, IV broad-spectrum antibiotics within 1 hr, and 30 mL/kg crystalloid fluid bolus for hypotension/lactate ≥4 mmol/L."
    else:
        tier = "LOW"
        tier_label = f"🟢 Low Risk Bedside Sepsis (Score {score}/3)"
        rec = "qSOFA criteria not met (<2). Continue monitoring vital signs and clinical trajectory. If clinical suspicion of infection remains high, monitor full SOFA score and laboratory biomarkers."

    return {
        "calculator_id": "qsofa",
        "calculator_title": "qSOFA Quick Sepsis-Related Organ Failure Screener",
        "score": score,
        "score_unit": "points (max 3)",
        "tier": tier,
        "tier_label": tier_label,
        "clinical_action": rec,
        "breakdown": breakdown,
        "citations": "Singer M, et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA 2016; 315:801-810"
    }


# =============================================================================
# 8. FINDRISC 10-Year Type 2 Diabetes Risk Score
# =============================================================================

def calculate_findrisc(
    age: int,
    bmi: float,
    waist_cm: float,
    is_female: bool,
    physical_activity_daily: bool,
    vegetables_daily: bool,
    on_bp_medication: bool,
    history_high_blood_glucose: bool,
    family_history_diabetes: str  # "none", "second_degree", "first_degree"
) -> Dict[str, Any]:
    """
    Computes Finnish Diabetes Risk Score (FINDRISC) for predicting 10-year risk of Type 2 Diabetes.
    """
    score = 0
    breakdown = []

    # 1. Age
    if age < 45:
        breakdown.append("Age <45 (+0)")
    elif age <= 54:
        score += 2
        breakdown.append("Age 45-54 (+2)")
    elif age <= 64:
        score += 3
        breakdown.append("Age 55-64 (+3)")
    else:
        score += 4
        breakdown.append("Age ≥65 (+4)")

    # 2. BMI
    if bmi < 25.0:
        breakdown.append(f"BMI <25 ({bmi:.1f}) (+0)")
    elif bmi <= 30.0:
        score += 1
        breakdown.append(f"BMI 25-30 ({bmi:.1f}) (+1)")
    else:
        score += 3
        breakdown.append(f"BMI >30 ({bmi:.1f}) (+3)")

    # 3. Waist Circumference
    if is_female:
        if waist_cm < 80:
            breakdown.append("Waist <80 cm (+0)")
        elif waist_cm <= 88:
            score += 3
            breakdown.append("Waist 80-88 cm (+3)")
        else:
            score += 4
            breakdown.append("Waist >88 cm (+4)")
    else:
        if waist_cm < 94:
            breakdown.append("Waist <94 cm (+0)")
        elif waist_cm <= 102:
            score += 3
            breakdown.append("Waist 94-102 cm (+3)")
        else:
            score += 4
            breakdown.append("Waist >102 cm (+4)")

    # 4. Physical Activity (≥30 min daily)
    if not physical_activity_daily:
        score += 2
        breakdown.append("Physical activity <30 min/day (+2)")
    else:
        breakdown.append("Daily physical activity ≥30 min (+0)")

    # 5. Daily Vegetables / Fruits
    if not vegetables_daily:
        score += 1
        breakdown.append("Does not eat vegetables/berries/fruit daily (+1)")
    else:
        breakdown.append("Eats vegetables/berries/fruit daily (+0)")

    # 6. Blood Pressure Medication
    if on_bp_medication:
        score += 2
        breakdown.append("Has taken medication for high blood pressure (+2)")

    # 7. History of High Blood Glucose
    if history_high_blood_glucose:
        score += 5
        breakdown.append("History of elevated blood glucose / gestational diabetes (+5)")

    # 8. Family History of Diabetes
    if family_history_diabetes == "second_degree":
        score += 3
        breakdown.append("Family history: Grandparent, aunt, uncle, or cousin (+3)")
    elif family_history_diabetes == "first_degree":
        score += 5
        breakdown.append("Family history: Parent, sibling, or child (+5)")
    else:
        breakdown.append("No family history (+0)")

    if score < 7:
        tier = "LOW"
        risk_pct = "1% (1 in 100)"
        tier_label = f"🟢 Low Risk (Score {score}/26, 10-Yr Risk: {risk_pct})"
        rec = "Maintain current healthy diet and physical activity habits. Re-evaluate in 3–5 years."
    elif score <= 11:
        tier = "SLIGHT"
        risk_pct = "4% (1 in 25)"
        tier_label = f"🟡 Slightly Elevated (Score {score}/26, 10-Yr Risk: {risk_pct})"
        rec = "Emphasize low-glycemic dietary choices, maintain 150 min aerobic exercise weekly, and aim for 5% weight loss if BMI > 25."
    elif score <= 14:
        tier = "MODERATE"
        risk_pct = "17% (1 in 6)"
        tier_label = f"🟠 Moderate Risk (Score {score}/26, 10-Yr Risk: {risk_pct})"
        rec = "Screening Fasting Plasma Glucose or HbA1c test recommended. Structured lifestyle intervention (Diabetes Prevention Program guidelines)."
    elif score <= 20:
        tier = "HIGH"
        risk_pct = "33% (1 in 3)"
        tier_label = f"🔴 High Risk (Score {score}/26, 10-Yr Risk: {risk_pct})"
        rec = "High risk of undiagnosed diabetes or prediabetes. Order diagnostic Fasting Glucose, HbA1c, or 2-hr OGTT promptly. Comprehensive nutrition consultation."
    else:
        tier = "VERY_HIGH"
        risk_pct = "50% (1 in 2)"
        tier_label = f"🔴 Very High Risk (Score {score}/26, 10-Yr Risk: {risk_pct})"
        rec = "50% 10-year diabetes probability. Formal diagnostic evaluation with primary physician immediately. Intensive lifestyle modification and consideration of Metformin if prediabetic."

    return {
        "calculator_id": "findrisc",
        "calculator_title": "FINDRISC 10-Year Type 2 Diabetes Risk Score",
        "score": score,
        "score_unit": "points (max 26)",
        "ten_year_risk": risk_pct,
        "tier": tier,
        "tier_label": tier_label,
        "prevention_guideline": rec,
        "breakdown": breakdown,
        "citations": "Lindström J, Tuomilehto J. The diabetes risk score: a practical tool to predict type 2 diabetes risk. Diabetes Care 2003; 26:725-731"
    }


# =============================================================================
# 9. PHQ-9 Depression Severity & GAD-7 Anxiety Scales
# =============================================================================

def calculate_phq9(answers: List[int]) -> Dict[str, Any]:
    """
    Computes PHQ-9 (Patient Health Questionnaire 9) score for depression severity.
    Answers: list of 9 integers from 0 to 3.
    Includes critical safety flag if Question 9 (self-harm/suicidal ideation) > 0.
    """
    if not answers or len(answers) != 9:
        answers = [0] * 9
    clean_answers = [max(0, min(3, int(a))) for a in answers]
    score = sum(clean_answers)

    has_suicide_flag = clean_answers[8] > 0

    if score <= 4:
        tier = "MINIMAL"
        tier_label = f"🟢 None-Minimal Depression (Score {score}/27)"
        rec = "Depressive symptoms absent or minimal. No formal pharmacotherapy or psychotherapeutic intervention required."
    elif score <= 9:
        tier = "MILD"
        tier_label = f"🟡 Mild Depression (Score {score}/27)"
        rec = "Watchful waiting, psychoeducation, regular exercise, sleep hygiene, and re-evaluation in 4–8 weeks."
    elif score <= 14:
        tier = "MODERATE"
        tier_label = f"🟠 Moderate Depression (Score {score}/27)"
        rec = "Consider evidence-based psychotherapy (Cognitive Behavioral Therapy / Interpersonal Therapy) or first-line SSRI/SNRI pharmacotherapy."
    elif score <= 19:
        tier = "MODERATELY_SEVERE"
        tier_label = f"🔴 Moderately Severe Depression (Score {score}/27)"
        rec = "Active treatment with combination psychotherapy and antidepressant pharmacotherapy strongly recommended. Psychiatric consultation."
    else:
        tier = "SEVERE"
        tier_label = f"🔴 Severe Depression (Score {score}/27)"
        rec = "Immediate clinical management with pharmacotherapy and mental health specialist referral. Assess functional impairment and safety."

    safety_warning = ""
    if has_suicide_flag:
        safety_warning = "🚨 CRITICAL SAFETY ALERT: Patient endorsed thoughts of self-harm or suicidal ideation (Question 9 > 0). Immediate clinical suicide risk assessment required. National Suicide & Crisis Lifeline: Call or text 988 (US), 111 (UK), 112 (EU/India)."

    return {
        "calculator_id": "phq9",
        "calculator_title": "PHQ-9 Depression Severity Scale",
        "score": score,
        "score_unit": "points (max 27)",
        "tier": tier,
        "tier_label": tier_label,
        "has_suicide_flag": has_suicide_flag,
        "safety_warning": safety_warning,
        "treatment_recommendation": rec,
        "citations": "Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med 2001; 16:606-613"
    }


def calculate_gad7(answers: List[int]) -> Dict[str, Any]:
    """
    Computes GAD-7 (Generalized Anxiety Disorder 7-item Scale) score.
    Answers: list of 7 integers from 0 to 3.
    """
    if not answers or len(answers) != 7:
        answers = [0] * 7
    clean_answers = [max(0, min(3, int(a))) for a in answers]
    score = sum(clean_answers)

    if score <= 4:
        tier = "MINIMAL"
        tier_label = f"🟢 Minimal Anxiety (Score {score}/21)"
        rec = "Anxiety symptoms minimal. Routine stress management and wellness practices."
    elif score <= 9:
        tier = "MILD"
        tier_label = f"🟡 Mild Anxiety (Score {score}/21)"
        rec = "Watchful waiting, mindfulness-based stress reduction, sleep optimization, and monitoring."
    elif score <= 14:
        tier = "MODERATE"
        tier_label = f"🟠 Moderate Anxiety (Score {score}/21)"
        rec = "Probable Generalized Anxiety Disorder. Consider Cognitive Behavioral Therapy (CBT) and/or first-line SSRI/SNRI medication."
    else:
        tier = "SEVERE"
        tier_label = f"🔴 Severe Anxiety (Score {score}/21)"
        rec = "Active treatment with specialist psychological intervention and pharmacotherapy indicated. Evaluate for comorbid panic or depressive disorders."

    return {
        "calculator_id": "gad7",
        "calculator_title": "GAD-7 Generalized Anxiety Disorder Scale",
        "score": score,
        "score_unit": "points (max 21)",
        "tier": tier,
        "tier_label": tier_label,
        "treatment_recommendation": rec,
        "citations": "Spitzer RL, Kroenke K, Williams JB, Löwe B. A brief measure for assessing generalized anxiety disorder: the GAD-7. Arch Intern Med 2006; 166:1092-1097"
    }


# =============================================================================
# 10. Anthropometric & Metabolic Vital Suite (BMI, IBW, BSA, BMR/TDEE)
# =============================================================================

def calculate_anthropometrics(
    weight_kg: float,
    height_cm: float,
    age: int,
    is_female: bool,
    activity_level: str = "moderate"  # "sedentary", "light", "moderate", "active", "very_active"
) -> Dict[str, Any]:
    """
    Computes comprehensive anthropometric and metabolic parameters:
    - BMI & WHO Weight Classification
    - Devine Ideal Body Weight (IBW) & Adjusted Body Weight (AdjBW)
    - Mosteller Body Surface Area (BSA)
    - Mifflin-St Jeor Basal Metabolic Rate (BMR) & Total Daily Energy Expenditure (TDEE)
    """
    wt = max(20.0, min(350.0, float(weight_kg)))
    ht = max(80.0, min(250.0, float(height_cm)))
    age = max(10, min(110, int(age)))

    # 1. BMI
    ht_m = ht / 100.0
    bmi = wt / (ht_m ** 2)
    bmi_rounded = round(bmi, 1)

    if bmi_rounded < 18.5:
        bmi_tier = "UNDERWEIGHT"
        bmi_label = "🟡 Underweight (<18.5 kg/m²)"
    elif bmi_rounded <= 24.9:
        bmi_tier = "NORMAL"
        bmi_label = "🟢 Normal Weight (18.5 - 24.9 kg/m²)"
    elif bmi_rounded <= 29.9:
        bmi_tier = "OVERWEIGHT"
        bmi_label = "🟡 Overweight (25.0 - 29.9 kg/m²)"
    elif bmi_rounded <= 34.9:
        bmi_tier = "OBESE_1"
        bmi_label = "🟠 Class I Obesity (30.0 - 34.9 kg/m²)"
    elif bmi_rounded <= 39.9:
        bmi_tier = "OBESE_2"
        bmi_label = "🔴 Class II Obesity (35.0 - 39.9 kg/m²)"
    else:
        bmi_tier = "OBESE_3"
        bmi_label = "🔴 Class III Severe Obesity (≥40.0 kg/m²)"

    # 2. Devine Ideal Body Weight (IBW)
    ht_inches = ht / 2.54
    inches_over_5ft = max(0.0, ht_inches - 60.0)
    if is_female:
        ibw = 45.5 + (2.3 * inches_over_5ft)
    else:
        ibw = 50.0 + (2.3 * inches_over_5ft)
    ibw_rounded = round(ibw, 1)

    # Adjusted Body Weight for obese patients (AdjBW = IBW + 0.4*(Actual - IBW))
    adj_bw = round(ibw + 0.4 * (wt - ibw), 1) if wt > ibw else wt

    # 3. Mosteller Body Surface Area (BSA) in m^2
    bsa = math.sqrt((ht * wt) / 3600.0)
    bsa_rounded = round(bsa, 2)

    # 4. Mifflin-St Jeor Basal Metabolic Rate (BMR)
    if is_female:
        bmr = (10.0 * wt) + (6.25 * ht) - (5.0 * age) - 161.0
    else:
        bmr = (10.0 * wt) + (6.25 * ht) - (5.0 * age) + 5.0
    bmr_rounded = int(round(bmr))

    # Total Daily Energy Expenditure (TDEE)
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    af = activity_factors.get(activity_level.lower(), 1.55)
    tdee = int(round(bmr * af))

    return {
        "calculator_id": "anthropometrics",
        "calculator_title": "Anthropometric & Metabolic Vital Suite",
        "bmi": bmi_rounded,
        "bmi_tier": bmi_tier,
        "bmi_label": bmi_label,
        "ideal_body_weight_kg": ibw_rounded,
        "adjusted_body_weight_kg": adj_bw,
        "body_surface_area_m2": bsa_rounded,
        "bmr_kcal_day": bmr_rounded,
        "tdee_kcal_day": tdee,
        "activity_level": activity_level.capitalize(),
        "parameters": {
            "Weight": f"{wt} kg ({round(wt * 2.20462, 1)} lbs)",
            "Height": f"{ht} cm ({int(ht // 30.48)}' {int(round((ht % 30.48) / 2.54))}\")",
            "Age": f"{age} years",
            "Gender": "Female" if is_female else "Male"
        },
        "citations": "Devine BJ (1974), Mosteller RD (1987), Mifflin MD et al. (1990)"
    }


# =============================================================================
# Catalog & Evaluation Registry
# =============================================================================

CALCULATORS_CATALOG = {
    "ascvd": {
        "id": "ascvd",
        "title": "ASCVD 10-Year Heart Disease Risk",
        "category": "cardiovascular",
        "category_label": "🫀 Cardiovascular",
        "icon": "🫀",
        "badge": "AHA/ACC 2018",
        "description": "Calculates 10-year risk of first fatal/nonfatal heart attack or stroke to guide statin and lifestyle therapy.",
        "citations": "AHA/ACC Guideline on the Management of Blood Cholesterol"
    },
    "chads_vasc": {
        "id": "chads_vasc",
        "title": "CHA₂DS₂-VASc AFib Stroke Risk",
        "category": "cardiovascular",
        "category_label": "🫀 Cardiovascular",
        "icon": "❤️",
        "badge": "ESC 2020",
        "description": "Predicts annual thromboembolic stroke risk in non-valvular atrial fibrillation to guide oral anticoagulation.",
        "citations": "ESC Guidelines for the Diagnosis and Management of Atrial Fibrillation"
    },
    "egfr": {
        "id": "egfr",
        "title": "eGFR (CKD-EPI 2021 Race-Free)",
        "category": "renal_hepatic",
        "category_label": "🫘 Renal & Hepatic",
        "icon": "🫘",
        "badge": "KDIGO 2021",
        "description": "Estimates Glomerular Filtration Rate using 2021 race-free equation for chronic kidney disease staging.",
        "citations": "NEJM 2021 Race-Free CKD-EPI Equation"
    },
    "fib4": {
        "id": "fib4",
        "title": "FIB-4 Index for Liver Fibrosis",
        "category": "renal_hepatic",
        "category_label": "🫘 Renal & Hepatic",
        "icon": "🧪",
        "badge": "AASLD/EASL",
        "description": "Non-invasive biomarker score to rule out advanced hepatic fibrosis and cirrhosis in NAFLD/NASH and hepatitis.",
        "citations": "Hepatology 2006 FIB-4 Index"
    },
    "curb65": {
        "id": "curb65",
        "title": "CURB-65 Pneumonia Severity",
        "category": "pulmonary_sepsis",
        "category_label": "🫁 Pulmonary & Sepsis",
        "icon": "🫁",
        "badge": "BTS Guideline",
        "description": "Stratifies 30-day pneumonia mortality risk and guides Outpatient vs Inpatient vs ICU admission.",
        "citations": "British Thoracic Society Pneumonia Guidelines"
    },
    "wells_dvt": {
        "id": "wells_dvt",
        "title": "Wells' Criteria for DVT",
        "category": "pulmonary_sepsis",
        "category_label": "🫁 Pulmonary & Sepsis",
        "icon": "🩸",
        "badge": "Validated Rule",
        "description": "Calculates pre-test probability of Deep Vein Thrombosis to guide D-Dimer vs compression Doppler ultrasound.",
        "citations": "NEJM 2003 Wells Criteria for DVT"
    },
    "qsofa": {
        "id": "qsofa",
        "title": "qSOFA Bedside Sepsis Screener",
        "category": "pulmonary_sepsis",
        "category_label": "🫁 Pulmonary & Sepsis",
        "icon": "⚡",
        "badge": "Sepsis-3",
        "description": "Identifies infected patients at high risk of in-hospital mortality and prolonged ICU stay.",
        "citations": "JAMA 2016 Sepsis-3 Consensus"
    },
    "findrisc": {
        "id": "findrisc",
        "title": "FINDRISC Diabetes Risk (10-Yr)",
        "category": "metabolic_vitals",
        "category_label": "⚖️ Metabolic & Vitals",
        "icon": "🍬",
        "badge": "Diabetes Care",
        "description": "Evaluates 10-year probability of developing Type 2 Diabetes to guide early preventive lifestyle interventions.",
        "citations": "Finnish Diabetes Risk Score (FINDRISC)"
    },
    "anthropometrics": {
        "id": "anthropometrics",
        "title": "BMI, IBW, BSA & BMR Suite",
        "category": "metabolic_vitals",
        "category_label": "⚖️ Metabolic & Vitals",
        "icon": "⚖️",
        "badge": "Clinical Vitals",
        "description": "Calculates BMI, Devine Ideal Body Weight, Mosteller Body Surface Area, and Mifflin-St Jeor BMR/TDEE.",
        "citations": "Devine (1974), Mosteller (1987), Mifflin-St Jeor (1990)"
    },
    "phq9": {
        "id": "phq9",
        "title": "PHQ-9 Depression Severity Scale",
        "category": "mental_health",
        "category_label": "🧠 Mental Health",
        "icon": "🧠",
        "badge": "DSM-5 Scale",
        "description": "Standard 9-item clinical screening scale measuring depression severity with suicide safety monitoring.",
        "citations": "Journal of General Internal Medicine (PHQ-9)"
    },
    "gad7": {
        "id": "gad7",
        "title": "GAD-7 Anxiety Screening Scale",
        "category": "mental_health",
        "category_label": "🧠 Mental Health",
        "icon": "🧘",
        "badge": "Anxiety Scale",
        "description": "Validated 7-item clinical tool for assessing Generalized Anxiety Disorder severity.",
        "citations": "Archives of Internal Medicine (GAD-7)"
    }
}


def get_all_calculators_catalog() -> Dict[str, Any]:
    """Returns all clinical risk calculators grouped by medical category."""
    categories = {
        "all": {"title": "All Tools", "icon": "🧮", "count": len(CALCULATORS_CATALOG)},
        "cardiovascular": {"title": "🫀 Cardiovascular", "icon": "🫀", "calculators": []},
        "renal_hepatic": {"title": "🫘 Renal & Hepatic", "icon": "🫘", "calculators": []},
        "pulmonary_sepsis": {"title": "🫁 Pulmonary & Sepsis", "icon": "🫁", "calculators": []},
        "metabolic_vitals": {"title": "⚖️ Metabolic & Vitals", "icon": "⚖️", "calculators": []},
        "mental_health": {"title": "🧠 Mental Health", "icon": "🧠", "calculators": []}
    }

    calc_list = []
    for cid, cdata in CALCULATORS_CATALOG.items():
        calc_list.append(cdata)
        cat_key = cdata["category"]
        if cat_key in categories:
            categories[cat_key]["calculators"].append(cdata)

    return {
        "success": True,
        "total_calculators": len(CALCULATORS_CATALOG),
        "categories": categories,
        "calculators": calc_list
    }


def evaluate_clinical_calculator(calc_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates any supported clinical calculator with input validation and returns formatted clinical output.
    """
    if not calc_id:
        return {"success": False, "error": "Missing calculator ID."}
    
    cid = calc_id.lower().strip()
    inputs = inputs or {}

    try:
        if cid == "ascvd":
            res = calculate_ascvd(
                age=float(inputs.get("age", 55)),
                sex=str(inputs.get("sex", "male")),
                race=str(inputs.get("race", "white_other")),
                systolic_bp=float(inputs.get("systolic_bp", 130)),
                total_cholesterol=float(inputs.get("total_cholesterol", 200)),
                hdl_cholesterol=float(inputs.get("hdl_cholesterol", 50)),
                is_diabetic=bool(inputs.get("is_diabetic", False)),
                is_smoker=bool(inputs.get("is_smoker", False)),
                on_hypertension_treatment=bool(inputs.get("on_hypertension_treatment", False))
            )
        elif cid == "chads_vasc":
            res = calculate_chads_vasc(
                age=int(inputs.get("age", 65)),
                is_female=bool(inputs.get("is_female", False)),
                congestive_heart_failure=bool(inputs.get("congestive_heart_failure", False)),
                hypertension=bool(inputs.get("hypertension", False)),
                diabetes=bool(inputs.get("diabetes", False)),
                stroke_or_tia=bool(inputs.get("stroke_or_tia", False)),
                vascular_disease=bool(inputs.get("vascular_disease", False))
            )
        elif cid == "egfr":
            res = calculate_egfr_ckdepi(
                serum_creatinine=float(inputs.get("serum_creatinine", 1.0)),
                age=float(inputs.get("age", 50)),
                is_female=bool(inputs.get("is_female", False))
            )
        elif cid == "fib4":
            res = calculate_fib4(
                age=float(inputs.get("age", 50)),
                ast=float(inputs.get("ast", 35)),
                alt=float(inputs.get("alt", 40)),
                platelets=float(inputs.get("platelets", 200))
            )
        elif cid == "curb65":
            res = calculate_curb65(
                confusion=bool(inputs.get("confusion", False)),
                bun_mg_dl=float(inputs.get("bun_mg_dl", 15.0)),
                respiratory_rate=int(inputs.get("respiratory_rate", 20)),
                systolic_bp=int(inputs.get("systolic_bp", 120)),
                diastolic_bp=int(inputs.get("diastolic_bp", 80)),
                age=int(inputs.get("age", 60))
            )
        elif cid == "wells_dvt":
            res = calculate_wells_dvt(
                active_cancer=bool(inputs.get("active_cancer", False)),
                paralysis_or_plaster=bool(inputs.get("paralysis_or_plaster", False)),
                bedridden_or_major_surgery=bool(inputs.get("bedridden_or_major_surgery", False)),
                localized_tenderness=bool(inputs.get("localized_tenderness", False)),
                entire_leg_swollen=bool(inputs.get("entire_leg_swollen", False)),
                calf_swelling_over_3cm=bool(inputs.get("calf_swelling_over_3cm", False)),
                pitting_edema=bool(inputs.get("pitting_edema", False)),
                collateral_superficial_veins=bool(inputs.get("collateral_superficial_veins", False)),
                previous_dvt=bool(inputs.get("previous_dvt", False)),
                alternative_diagnosis_likely=bool(inputs.get("alternative_diagnosis_likely", False))
            )
        elif cid == "qsofa":
            res = calculate_qsofa(
                respiratory_rate=int(inputs.get("respiratory_rate", 18)),
                altered_mentation=bool(inputs.get("altered_mentation", False)),
                systolic_bp=int(inputs.get("systolic_bp", 120))
            )
        elif cid == "findrisc":
            res = calculate_findrisc(
                age=int(inputs.get("age", 45)),
                bmi=float(inputs.get("bmi", 26.0)),
                waist_cm=float(inputs.get("waist_cm", 88.0)),
                is_female=bool(inputs.get("is_female", False)),
                physical_activity_daily=bool(inputs.get("physical_activity_daily", True)),
                vegetables_daily=bool(inputs.get("vegetables_daily", True)),
                on_bp_medication=bool(inputs.get("on_bp_medication", False)),
                history_high_blood_glucose=bool(inputs.get("history_high_blood_glucose", False)),
                family_history_diabetes=str(inputs.get("family_history_diabetes", "none"))
            )
        elif cid == "phq9":
            res = calculate_phq9(inputs.get("answers", [0] * 9))
        elif cid == "gad7":
            res = calculate_gad7(inputs.get("answers", [0] * 7))
        elif cid == "anthropometrics":
            res = calculate_anthropometrics(
                weight_kg=float(inputs.get("weight_kg", 70.0)),
                height_cm=float(inputs.get("height_cm", 170.0)),
                age=int(inputs.get("age", 35)),
                is_female=bool(inputs.get("is_female", False)),
                activity_level=str(inputs.get("activity_level", "moderate"))
            )
        else:
            return {"success": False, "error": f"Unknown clinical calculator ID: '{calc_id}'."}

        return {
            "success": True,
            "calculator_id": cid,
            "data": res
        }
    except Exception as e:
        return {"success": False, "error": f"Calculation error: {str(e)}"}


def detect_calculator_in_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Detects if user query has clinical calculation intent (e.g. 'calculate ASCVD', 'eGFR score', 'BMI calculation').
    """
    if not text:
        return None
    lower_q = text.lower()

    calc_patterns = {
        "ascvd": [r'\bascvd\b', r'cardiovascular risk', r'10-year heart risk', r'framingham risk', r'heart attack risk calculator'],
        "chads_vasc": [r'chads', r'cha2ds2', r'afib stroke risk', r'atrial fibrillation stroke', r'anticoagulation score'],
        "egfr": [r'\begfr\b', r'kidney function score', r'ckd-epi', r'creatinine clearance', r'gfr calculator'],
        "fib4": [r'fib-4', r'fib4', r'liver fibrosis score', r'fibrosis index'],
        "curb65": [r'curb-65', r'curb65', r'pneumonia severity', r'pneumonia score'],
        "wells_dvt": [r'wells criteria', r'wells dvt', r'deep vein thrombosis score', r'dvt probability'],
        "qsofa": [r'qsofa', r'quick sofa', r'sepsis score', r'sepsis screener'],
        "findrisc": [r'findrisc', r'diabetes risk score', r'diabetes risk calculator', r'type 2 diabetes risk'],
        "phq9": [r'phq-9', r'phq9', r'depression score', r'depression test', r'depression scale'],
        "gad7": [r'gad-7', r'gad7', r'anxiety scale', r'anxiety test', r'anxiety score'],
        "anthropometrics": [r'\bbmi\b', r'body mass index', r'ideal body weight', r'bmr calculator', r'tdee calculator', r'body surface area']
    }

    for cid, patterns in calc_patterns.items():
        for pat in patterns:
            if re.search(pat, lower_q):
                return {
                    "calculator_id": cid,
                    "info": CALCULATORS_CATALOG.get(cid, {})
                }
    return None
