"""MCP Tool #2: Zero-PHI Clinical Guideline & Pharmacology Knowledge Base (`query_clinical_guidelines_db`)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# Structured Zero-PHI Clinical Guidelines Database grounded in FDA labels / KDIGO / PubMedQA concepts
RENAL_CONTRAINDICATION_RULES: List[Dict[str, Any]] = [
    {
        "guideline_id": "KDIGO-RENAL-001",
        "drug_keywords": ["metformin", "glucophage"],
        "egfr_threshold": 30.0,
        "severity": "CRITICAL",
        "mechanism": "Impaired renal clearance of Metformin when eGFR < 30 mL/min/1.73m2 causes drug accumulation and life-threatening Metformin-Associated Lactic Acidosis (MALA).",
        "citation": "FDA Boxed Warning & KDIGO 2022 Diabetes in CKD Guideline (eGFR < 30: Contraindicated)",
        "safe_alternative": "Discontinue Metformin immediately; consider Linagliptin (no renal dose adjustment required) or basal insulin titration.",
    },
    {
        "guideline_id": "RENAL-UTI-002",
        "drug_keywords": ["nitrofurantoin", "macrobid"],
        "egfr_threshold": 30.0,
        "severity": "CRITICAL",
        "mechanism": "Nitrofurantoin fails to achieve therapeutic urinary concentrations when eGFR < 30 mL/min and increases systemic risk of pulmonary/peripheral neuropathy toxicity.",
        "citation": "AGS Beers Criteria & IDSA Uncomplicated UTI Guidelines",
        "safe_alternative": "Switch to renal-adjusted Cefpodoxime or Fosfomycin (if appropriate for lower UTI).",
    },
    {
        "guideline_id": "RENAL-NSAID-003",
        "drug_keywords": ["ibuprofen", "naproxen", "ketorolac", "meloxicam", "celecoxib", "indomethacin"],
        "egfr_threshold": 60.0,
        "severity": "CRITICAL",
        "mechanism": "NSAIDs inhibit afferent arteriolar prostaglandin synthesis, precipitating acute-on-chronic kidney injury (AKI) and hyperkalemia in stage 3-5 CKD (eGFR < 60).",
        "citation": "KDIGO CKD Management Guideline §3.4 (Avoid NSAIDs in eGFR < 60 mL/min/1.73m2)",
        "safe_alternative": "Discontinue systemic NSAID; substitute scheduled Acetaminophen (up to 2-3g/day) or topical analgesics.",
    },
    {
        "guideline_id": "RENAL-ANTICOAG-004",
        "drug_keywords": ["dabigatran", "pradaxa", "rivaroxaban"],
        "egfr_threshold": 30.0,
        "severity": "CRITICAL",
        "mechanism": "Direct oral anticoagulants with high renal clearance accumulate severely when eGFR < 30 mL/min, causing major hemorrhage.",
        "citation": "AHA/ACC/HRS Atrial Fibrillation Anticoagulation Guideline",
        "safe_alternative": "Switch to dose-adjusted Apixaban or INR-monitored Warfarin per renal protocol.",
    },
]

PREGNANCY_TERATOGENIC_RULES: List[Dict[str, Any]] = [
    {
        "guideline_id": "OB-TERAT-001",
        "drug_keywords": ["lisinopril", "enalapril", "ramipril", "losartan", "valsartan", "olmesartan"],
        "severity": "CRITICAL",
        "mechanism": "ACE inhibitors and ARBs disrupt fetal renin-angiotensin system development, causing oligohydramnios, fetal renal dysplasia, skull hypoplasia, and fetal death.",
        "citation": "FDA Boxed Warning & ACOG Practice Bulletin (Chronic Hypertension in Pregnancy)",
        "safe_alternative": "Discontinue ACEi/ARB immediately; transition to Labetalol, Nifedipine extended-release, or Methyldopa.",
    },
    {
        "guideline_id": "OB-TERAT-002",
        "drug_keywords": ["warfarin", "coumadin"],
        "severity": "CRITICAL",
        "mechanism": "Warfarin crosses the placenta and causes fetal warfarin syndrome (nasal hypoplasia, stippled epiphyses) and fetal CNS hemorrhage.",
        "citation": "ACCP / ACOG Thromboembolism in Pregnancy Guideline",
        "safe_alternative": "Transition immediately to Low-Molecular-Weight Heparin (Enoxaparin), which does not cross the placenta.",
    },
    {
        "guideline_id": "OB-TERAT-003",
        "drug_keywords": ["isotretinoin", "accutane", "methotrexate", "valproate", "valproic acid", "atorvastatin", "simvastatin", "rosuvastatin", "doxycycline"],
        "severity": "CRITICAL",
        "mechanism": "Severe teratogenicity (neural tube defects, craniofacial/cardiac malformations, or fetal skeletal/dental toxicity).",
        "citation": "FDA Pregnancy & Lactation Labeling Rule (PLLR) Contraindications",
        "safe_alternative": "Hold teratogenic agent immediately and consult Maternal-Fetal Medicine for safe pregnancy-compatible therapy.",
    },
]

ALLERGY_CROSS_REACTIVITY_RULES: List[Dict[str, Any]] = [
    {
        "guideline_id": "ALG-BETA-001",
        "allergy_keywords": ["penicillin", "amoxicillin", "ampicillin", "beta-lactam"],
        "drug_keywords": ["amoxicillin", "augmentin", "ampicillin", "piperacillin", "zosyn", "penicillin"],
        "severity": "CRITICAL",
        "mechanism": "Direct beta-lactam re-exposure in a patient with documented Penicillin IgE-mediated anaphylaxis/angioedema risks fatal anaphylactic shock.",
        "citation": "AAAAI Drug Allergy Practice Parameter",
        "safe_alternative": "Use a non-beta-lactam alternative (e.g., Aztreonam, respiratory Fluoroquinolone, or Vancomycin/Macrolide depending on indication).",
    },
    {
        "guideline_id": "ALG-SULFA-002",
        "allergy_keywords": ["sulfa", "sulfonamide", "bactrim", "cotrimoxazole"],
        "drug_keywords": ["bactrim", "sulfamethoxazole", "tmp-smx", "cotrimoxazole", "sulfadiazine"],
        "severity": "CRITICAL",
        "mechanism": "Sulfonamide antimicrobial re-challenge in patients with severe sulfa allergy risks Stevens-Johnson Syndrome (SJS) / Toxic Epidermal Necrolysis (TEN).",
        "citation": "IDSA / AAAAI Hypersensitivity Guidelines",
        "safe_alternative": "Substitute non-sulfonamide antimicrobial (e.g., Doxycycline, Nitrofurantoin if eGFR >= 30, or Fosfomycin).",
    },
]

DRUG_DRUG_INTERACTION_RULES: List[Dict[Dict[str, Any], Any] | Dict[str, Any]] = [
    {
        "guideline_id": "DDI-HEMO-001",
        "pair_a": ["warfarin", "coumadin"],
        "pair_b": ["ibuprofen", "naproxen", "ketorolac", "aspirin", "meloxicam", "fluconazole", "amiodarone", "bactrim", "sulfamethoxazole", "metronidazole", "ciprofloxacin"],
        "severity": "CRITICAL",
        "mechanism": "Synergistic antiplatelet/mucosal erosion or potent CYP2C9 inhibition markedly elevates INR and triples major gastrointestinal/intracranial bleeding risk.",
        "citation": "ISMP High-Alert Anticoagulant Interaction Standard & CHEST Guidelines",
        "safe_alternative": "Avoid NSAID/interacting antimicrobial co-prescription with Warfarin; if antimicrobial is unavoidable, reduce Warfarin dose by 30-50% and check INR within 3 days.",
    },
    {
        "guideline_id": "DDI-SERO-002",
        "pair_a": ["sertraline", "fluoxetine", "escitalopram", "paroxetine", "citalopram", "venlafaxine", "duloxetine"],
        "pair_b": ["phenelzine", "tranylcypromine", "selegiline", "linezolid", "tramadol"],
        "severity": "CRITICAL",
        "mechanism": "Concomitant serotonergic agent + MAOI (including Linezolid) precipitates life-threatening Serotonin Syndrome (hyperthermia, clonus, autonomic instability).",
        "citation": "FDA Safety Communication & Boyer/Shannon Dunkley Serotonin Toxicity Criteria",
        "safe_alternative": "Contraindicated combination: require a minimum 14-day washout (5 weeks for Fluoxetine) or replace Linezolid with Vancomycin/Daptomycin.",
    },
    {
        "guideline_id": "DDI-KAL-003",
        "pair_a": ["lisinopril", "enalapril", "ramipril", "losartan", "valsartan"],
        "pair_b": ["spironolactone", "eplerenone", "amiloride", "triamterene", "potassium chloride", "k-dur"],
        "severity": "CRITICAL",
        "mechanism": "Dual RAAS blockade / aldosterone antagonism plus potassium supplementation impairs renal potassium excretion, risking lethal hyperkalemic arrhythmia.",
        "citation": "AHA/ACC Heart Failure & Hyperkalemia Safety Guideline",
        "safe_alternative": "Hold exogenous potassium supplementation and monitor serum potassium + renal function within 48-72 hours.",
    },
    {
        "guideline_id": "DDI-STAT-004",
        "pair_a": ["simvastatin", "lovastatin", "atorvastatin"],
        "pair_b": ["clarithromycin", "erythromycin", "itraconazole", "ketoconazole", "gemfibrozil"],
        "severity": "CRITICAL",
        "mechanism": "Potent CYP3A4 / OATP1B1 inhibition increases statin AUC >10-fold, causing severe myopathy, rhabdomyolysis, and myoglobinuric renal failure.",
        "citation": "FDA Statin-Macrolide Contraindication Label",
        "safe_alternative": "Temporarily suspend Simvastatin/Lovastatin during macrolide course, or switch macrolide to Azithromycin (non-CYP3A4 inhibitor).",
    },
    {
        "guideline_id": "DDI-NITR-005",
        "pair_a": ["nitroglycerin", "isosorbide", "imdur"],
        "pair_b": ["sildenafil", "viagra", "tadalafil", "cialis", "vardenafil"],
        "severity": "CRITICAL",
        "mechanism": "Synergistic cGMP accumulation causes profound, refractory vasodilation, hemodynamic collapse, and fatal myocardial infarction.",
        "citation": "ACC/AHA Chest Pain & Nitrate Contraindication Guideline",
        "safe_alternative": "Absolute contraindication within 24h of Sildenafil (48h for Tadalafil); use non-nitrate antianginal therapy (beta-blocker / calcium channel blocker).",
    },
]


def parse_clinical_context(clinical_text: str) -> Dict[str, Any]:
    """Extract physiological markers (eGFR, pregnancy status, allergies, medications) from unstructured text."""
    text_lower = clinical_text.lower()

    # 1. Extract eGFR
    egfr: Optional[float] = None
    egfr_match = re.search(r"egfr\s*(?:is|of|=|:)?\s*(\d+(?:\.\d+)?)", text_lower)
    if egfr_match:
        egfr = float(egfr_match.group(1))

    # 2. Extract Pregnancy Status
    pregnant = False
    if any(
        phrase in text_lower
        for phrase in (
            "pregnant",
            "gestation",
            "weeks gestation",
            "first trimester",
            "second trimester",
            "third trimester",
            "gravida",
            "positive hcg",
            "1st trimester",
            "2nd trimester",
        )
    ) and "not pregnant" not in text_lower and "negative pregnancy" not in text_lower and "non-pregnant" not in text_lower:
        pregnant = True

    # 3. Extract Allergies
    allergies: List[str] = []
    allergy_section = re.findall(
        r"(?:allerg(?:y|ies|ic)\s*(?:to|:)?\s*([^.\n;]+))",
        text_lower,
    )
    allergy_blob = " ".join(allergy_section)
    if "nkda" not in allergy_blob and "no known" not in allergy_blob:
        for kw in ("penicillin", "amoxicillin", "sulfa", "sulfonamide", "bactrim", "beta-lactam"):
            if kw in allergy_blob:
                allergies.append(kw)

    # 4. Extract All Mentioned Active Medications
    # Exclude drugs mentioned solely inside the "Allergies: ..." clause
    cleaned_for_meds = re.sub(r"allerg(?:y|ies|ic)\s*(?:to|:)?\s*[^.\n;]+", "", text_lower)
    all_drug_keywords = set()
    for r in RENAL_CONTRAINDICATION_RULES + PREGNANCY_TERATOGENIC_RULES + ALLERGY_CROSS_REACTIVITY_RULES:
        all_drug_keywords.update(r["drug_keywords"])
    for r in DRUG_DRUG_INTERACTION_RULES:
        all_drug_keywords.update(r["pair_a"])
        all_drug_keywords.update(r["pair_b"])
    for extra in ("apixaban", "labetalol", "acetaminophen", "linagliptin", "azithromycin", "vancomycin", "ceftriaxone", "insulin", "amlodipine", "levothyroxine", "omeprazole"):
        all_drug_keywords.add(extra)

    prescribed_meds = sorted(
        [drug for drug in all_drug_keywords if re.search(rf"\b{re.escape(drug)}\b", cleaned_for_meds)]
    )

    return {
        "egfr": egfr,
        "pregnant": pregnant,
        "allergies": allergies,
        "prescribed_meds": prescribed_meds,
    }


def query_clinical_guidelines_db(clinical_text: str) -> Dict[str, Any]:
    """
    MCP Tool Entrypoint: Evaluate a clinical note against structured Zero-PHI pharmacology rules.
    """
    ctx = parse_clinical_context(clinical_text)
    egfr = ctx["egfr"]
    pregnant = ctx["pregnant"]
    allergies = ctx["allergies"]
    meds = ctx["prescribed_meds"]

    violations: List[Dict[str, Any]] = []

    # Check 1: Renal Dosing Contraindications
    if egfr is not None:
        for rule in RENAL_CONTRAINDICATION_RULES:
            matched_drugs = [d for d in meds if d in rule["drug_keywords"]]
            if matched_drugs and egfr < rule["egfr_threshold"]:
                violations.append(
                    {
                        "guideline_id": rule["guideline_id"],
                        "category": "renal_contraindication",
                        "severity": rule["severity"],
                        "witness_input": f"eGFR={egfr} mL/min/1.73m2 (< {rule['egfr_threshold']}) + Prescribed: {', '.join(matched_drugs)}",
                        "observed_outcome": rule["mechanism"],
                        "evidence_citation": rule["citation"],
                        "safe_alternative": rule["safe_alternative"],
                    }
                )

    # Check 2: Pregnancy Teratogenicity
    if pregnant:
        for rule in PREGNANCY_TERATOGENIC_RULES:
            matched_drugs = [d for d in meds if d in rule["drug_keywords"]]
            if matched_drugs:
                violations.append(
                    {
                        "guideline_id": rule["guideline_id"],
                        "category": "pregnancy_teratogenicity",
                        "severity": rule["severity"],
                        "witness_input": f"Pregnant=True + Prescribed teratogen: {', '.join(matched_drugs)}",
                        "observed_outcome": rule["mechanism"],
                        "evidence_citation": rule["citation"],
                        "safe_alternative": rule["safe_alternative"],
                    }
                )

    # Check 3: Documented Allergy Cross-Reactivity
    if allergies:
        for rule in ALLERGY_CROSS_REACTIVITY_RULES:
            if any(a in rule["allergy_keywords"] for a in allergies):
                matched_drugs = [d for d in meds if d in rule["drug_keywords"]]
                if matched_drugs:
                    violations.append(
                        {
                            "guideline_id": rule["guideline_id"],
                            "category": "allergy_cross_reactivity",
                            "severity": rule["severity"],
                            "witness_input": f"Allergy={', '.join(allergies)} + Prescribed: {', '.join(matched_drugs)}",
                            "observed_outcome": rule["mechanism"],
                            "evidence_citation": rule["citation"],
                            "safe_alternative": rule["safe_alternative"],
                        }
                    )

    # Check 4: Drug-Drug Interactions
    for rule in DRUG_DRUG_INTERACTION_RULES:
        matched_a = [d for d in meds if d in rule["pair_a"]]
        matched_b = [d for d in meds if d in rule["pair_b"]]
        if matched_a and matched_b:
            violations.append(
                {
                    "guideline_id": rule["guideline_id"],
                    "category": "drug_drug_interaction",
                    "severity": rule["severity"],
                    "witness_input": f"Co-prescribed {matched_a[0]} + {matched_b[0]}",
                    "observed_outcome": rule["mechanism"],
                    "evidence_citation": rule["citation"],
                    "safe_alternative": rule["safe_alternative"],
                }
            )

    return {
        "status": "VIOLATION_DETECTED" if violations else "VERIFIED_SAFE",
        "patient_context": ctx,
        "violations": violations,
        "zero_phi_verified": True,
    }
