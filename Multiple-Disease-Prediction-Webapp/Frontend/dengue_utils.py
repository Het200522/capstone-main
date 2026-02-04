import os
import re
import numpy as np
import joblib
from lab_report_formatter import CBCReportFormatter

# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "best_dengue_model.pkl")

model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
except:
    model = None


# ================= UTILITIES =================
def extract(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return np.nan
    for g in m.groups()[::-1]:
        try:
            return float(g)
        except:
            continue
    return np.nan


def normalize(val):
    if not np.isnan(val) and val > 1000:
        return val / 1000
    return val


# ================= PARSER =================
def parse_cbc(text):
    """Parse CBC values using the improved formatter that handles all formats"""
    try:
        # Use the improved CBCReportFormatter which handles columnar and other formats
        cbc_values = CBCReportFormatter.parse_cbc_report(text)
        
        return {
            "platelets": cbc_values.get("Platelet Count", np.nan),
            "wbc": cbc_values.get("Total W.B.C. Count", np.nan),
            "lymph": cbc_values.get("Lymphocytes", np.nan),
            "neut": cbc_values.get("Neutrophils", np.nan),
        }
    except:
        # Fallback to old regex-based extraction if formatter fails
        t = text.replace(",", "").lower()
        return {
            "platelets": extract(r"platelet\s*count\s*[:\-]?\s*([\d]+)", t),
            "wbc": extract(r"(?:total\s*)?w\.?b\.?c\.?.*?([\d]+)", t),
            "lymph": extract(r"lymphocytes\s*[:\-]?\s*([\d\.]+)", t),
            "neut": extract(r"neutrophils\s*[:\-]?\s*([\d\.]+)", t),
        }


# ================= MAIN LOGIC =================
def predict_dengue(text):
    data = parse_cbc(text)

    platelets = normalize(data["platelets"])
    wbc = normalize(data["wbc"])
    lymph = data["lymph"]
    neut = data["neut"]

    dengue_signals = []
    abnormal_signals = []

    # ---------- SIGNAL DETECTION ----------
    if not np.isnan(platelets):
        if platelets < 150:
            dengue_signals.append("Low platelets")
        if platelets < 150 or platelets > 450:
            abnormal_signals.append("abnormal platelets")

    if not np.isnan(wbc):
        if wbc < 4.5:
            dengue_signals.append("Low WBC")
        if wbc < 4 or wbc > 10:
            abnormal_signals.append("abnormal WBC")

    if not np.isnan(lymph) and lymph > 40:
        dengue_signals.append("High lymphocytes")
        abnormal_signals.append("high lymphocytes")

    if not np.isnan(neut) and neut < 45:
        dengue_signals.append("Low neutrophils")
        abnormal_signals.append("low neutrophils")

    if re.search(r"dengue|viral\s*fever|thrombocytopenia", text, re.I):
        dengue_signals.append("Report mentions dengue")

    # ---------- ABSOLUTE RULE ----------
    if dengue_signals:
        severity = "Mild"
        risk = 0.65

        if (
            (not np.isnan(platelets) and platelets < 100) or
            (not np.isnan(wbc) and wbc < 3.5)
        ):
            severity = "High"
            risk = 0.90

        return (
            f"⚠️ Dengue Detected ({severity}) – "
            + ", ".join(dengue_signals),
            risk
        )

    # ---------- NORMAL vs ABNORMAL CBC ----------
    if abnormal_signals:
        # CBC has abnormal values but not dengue-specific
        return f"✅ Dengue Not Detected (CBC Abnormal) – {', '.join(abnormal_signals)}", 0.15
    
    # Both CBC and dengue checks are normal
    return "✅ Dengue Not Detected (CBC Normal)", 0.15
