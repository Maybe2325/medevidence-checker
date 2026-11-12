"""Synthetic Zero-PHI Clinical Vignette Presets for MedEvidence-Checker (`apps/med-evidence-checker`)."""

from __future__ import annotations
from typing import Any, Dict, List


MED_EVIDENCE_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "MED-PRESET-01",
        "title": "Stage 4 CKD Discharge Note (Metformin + Ibuprofen Renal Contraindication)",
        "subtitle": "eGFR 22 mL/min/1.73m2 with unadjusted Metformin & NSAID order",
        "clinical_text": (
            "Synthetic Vignette #1 (Zero-PHI): 68-year-old patient admitted for glycemic control and osteoarthritis flare. "
            "Labs today show serum creatinine 2.6 mg/dL, eGFR 22 mL/min/1.73m2. "
            "Allergies: NKDA. "
            "AI-Drafted Discharge Plan: Continue Metformin 1000 mg PO BID and start Ibuprofen 600 mg PO TID PRN knee pain."
        ),
    },
    {
        "id": "MED-PRESET-02",
        "title": "First-Trimester Hypertension & Anticoagulation (Teratogenic Regimen)",
        "subtitle": "8 weeks gestation prescribed Lisinopril and Warfarin",
        "clinical_text": (
            "Synthetic Vignette #2 (Zero-PHI): 29-year-old female at 8 weeks gestation (positive hCG, 1st trimester) "
            "presenting for chronic hypertension and history of DVT. eGFR 98 mL/min/1.73m2. Allergies: NKDA. "
            "AI-Drafted Plan: Continue Lisinopril 20 mg PO daily and Warfarin 5 mg PO daily."
        ),
    },
    {
        "id": "MED-PRESET-03",
        "title": "Hidden Beta-Lactam Cross-Reactivity (Penicillin Anaphylaxis + Zosyn)",
        "subtitle": "Documented IgE Penicillin anaphylaxis prescribed Piperacillin-Tazobactam",
        "clinical_text": (
            "Synthetic Vignette #3 (Zero-PHI): 54-year-old patient with severe community-acquired pneumonia. "
            "eGFR 75 mL/min/1.73m2. Allergies: Penicillin (severe anaphylaxis and airway angioedema). "
            "AI-Drafted Order: Initiate Piperacillin / Zosyn 4.5 g IV q6h immediately."
        ),
    },
    {
        "id": "MED-PRESET-04",
        "title": "Lethal Serotonergic + MRSA Antimicrobial Clash (Sertraline + Linezolid)",
        "subtitle": "MAOI properties of Linezolid trigger Serotonin Syndrome with SSRI",
        "clinical_text": (
            "Synthetic Vignette #4 (Zero-PHI): 46-year-old non-pregnant patient with MRSA skin infection and major depression. "
            "eGFR 82 mL/min/1.73m2. Allergies: NKDA. "
            "AI-Drafted Medication Reconciliation: Continue home Sertraline 150 mg PO daily and start Linezolid 600 mg PO BID."
        ),
    },
    {
        "id": "MED-PRESET-05",
        "title": "Verified Safe Control: Renal-Adjusted CKD Diabetes & Pain Regimen",
        "subtitle": "Linagliptin + Acetaminophen in Stage 4 CKD (eGFR 24)",
        "clinical_text": (
            "Synthetic Vignette #5 (Zero-PHI): 71-year-old non-pregnant patient with Type 2 diabetes and knee osteoarthritis. "
            "Labs: eGFR 24 mL/min/1.73m2. Allergies: NKDA. "
            "Plan: Linagliptin 5 mg PO daily and Acetaminophen 500 mg PO TID PRN pain."
        ),
    },
]
