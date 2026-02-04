# Dengue Prediction Report (OCR Extraction)

## Laboratory Report Details
**Laboratory:** CITYCARE DIAGNOSTICS  
**Branch:** South Jessicaport  
**Contact:** +91 9212767649  
**Report Release:** 15-11-2025 13:36:12  

---

## Patient Information
| Field | Value |
|-------|-------|
| **Name** | Eric Black |
| **Gender** | Female |
| **Age** | 9 years |
| **Sample ID** | 3479834 |
| **Date of Test** | 08-01-2025 |

---

## OCR Extracted CBC Values

| Test | Result | Unit | Reference Range | Status |
|------|--------|------|-----------------|--------|
| **Hemoglobin** | 10.4 | g/dL | 10.0-17.0 g/dL | ✅ Normal |
| **Total R.B.C. Count** | 3.75 | million/cumm | 4.45-8.55 million | ⚠️ Low |
| **Hematocrit (PCV/HCT)** | 35.4 | % | 40.0-50.0 % | ⚠️ Low |
| **Mean Corpuscular Volume (M.C.V.)** | 95.2 | fl | 83.0-95.0 fl | ⚠️ Slightly High |
| **Mean Corpuscular Hb (M.C.H.)** | 29.8 | Pg | 27.0-32.0 Pg | ✅ Normal |
| **Total W.B.C. Count** | 3,625 | /uL | 4,000-10,000 /uL | ⚠️ LOW |
| **Neutrophils** | 48.3 | % | 40-70 % | ✅ Normal |
| **Lymphocytes** | 25.1 | % | 20-40 % | ✅ Normal |
| **Eosinophils** | 4.6 | % | 1-6 % | ✅ Normal |
| **Monocytes** | 1.8 | % | 2-10 % | ⚠️ Low |
| **Basophils** | 0.9 | % | 0-1 % | ✅ Normal |
| **Platelet Count** | 113,274 | /uL | 150-450 /uL | ⚠️ LOW |
| **MPV** | 11.2 | fL | 6.76-13.45 fL | ✅ Normal |

---

## Dengue Prediction Analysis

### Input Values for Model
- **Platelet Count:** 113,274 /uL
- **WBC Count:** 3,625 /uL

### Model Prediction Output
```
⚠️ RESULT: POSSIBLE DENGUE - Combined Abnormalities Detected

Risk Level: MODERATE
Confidence: HIGH
Status: Low Platelets + Low WBC
```

### Clinical Interpretation

**Dengue Status:** ⚠️ **POSSIBLE DENGUE - CONSULT A DOCTOR**

#### Findings:
- ⚠️ **Platelet Count (113,274 /uL):** **BELOW NORMAL** (Reference: 150-450 /uL)
  - 🚨 Shows mild thrombocytopenia
  - Common in dengue fever (especially 3-5 days into illness)
  
- ⚠️ **WBC Count (3,625 /uL):** **BELOW NORMAL** (Reference: 4,000-10,000 /uL)
  - 🚨 Shows leukopenia
  - Also common in dengue infection

- ⚠️ **Combined Pattern:** Low platelets + Low WBC = **Strong dengue indicator**

#### Other Supporting Observations:
- Low RBC (3.75) and Low Hematocrit (35.4%) suggest possible hemoconcentration
- This combination is classic for dengue viral infection

---

## Dengue-Specific Risk Assessment

| Indicator | Status | Dengue Risk |
|-----------|--------|-------------|
| **Thrombocytopenia (<150k)** | Present (113,274) | 🚨 HIGH |
| **Leukopenia (<4k)** | Present (3,625) | 🚨 HIGH |
| **Hemoconcentration (High HCT)** | Absent (Low HCT) | ✅ LOW |
| **Combined Abnormalities** | Yes (Both present) | 🚨 **VERY HIGH** |

---

## Recommendation

### ⚠️ **CLINICAL ACTION REQUIRED**

Based on the CBC analysis, this patient shows **moderate-to-high risk indicators for dengue fever**:

1. **Immediate Actions:**
   - ✅ Consult with a qualified healthcare professional
   - ✅ Get serology tests (NS1, IgM, IgG)
   - ✅ Monitor for dengue symptoms (fever, rash, joint pain, headache)
   - ✅ Maintain hydration and rest

2. **Monitoring:**
   - ⚠️ Watch for platelet count trend (critical if < 100,000)
   - ⚠️ Monitor for warning signs (bleeding, severe abdominal pain)
   - ⚠️ Retest CBC after 2-3 days for comparison

3. **Prevention:**
   - Use mosquito protection (dengue is mosquito-borne)
   - Avoid NSAIDs (use paracetamol for fever)
   - Ensure adequate rest and hydration

---

## Report Summary
- **Date Analyzed:** January 9, 2026
- **Prediction Model:** Multiple Disease Prediction System (Clinical + ML)
- **Disease:** Dengue Fever
- **Status:** ⚠️ **POSSIBLE DENGUE** (Requires Medical Confirmation)
- **Confidence Level:** High
- **Recommendation:** Seek immediate medical consultation

---

**Important Disclaimer:** This is an automated analysis based on CBC parameters and clinical indicators. **Clinical diagnosis must be confirmed by a qualified healthcare professional with serology tests and clinical assessment.**

Last Updated: January 9, 2026 | Report ID: OCR-2025-0108
