import joblib
import pandas as pd
import re
import os

# --------------------------------------------------
# Load Asthma model pipeline (Random Forest pipeline)
# --------------------------------------------------
ASTHMA_MODEL_PATH = "models/asthma_rf_pipeline.pkl"

if not os.path.exists(ASTHMA_MODEL_PATH):
    raise FileNotFoundError("Asthma model file not found. Check model path.")

asthma_model = joblib.load(ASTHMA_MODEL_PATH)


# --------------------------------------------------
# Extract asthma parameters from OCR text
# --------------------------------------------------
def extract_asthma_features(text: str):
    """
    Extract required asthma features from OCR-extracted lab report text
    (basic version for integration with Dengue-style OCR flow)
    """

    # Try to extract common spirometry values
    fev1 = re.search(r'FEV1\s*[:\-]?\s*([\d.]+)', text, re.IGNORECASE)
    feno = re.search(r'FeNO\s*[:\-]?\s*([\d.]+)', text, re.IGNORECASE)
    peak_flow = re.search(r'Peak\s*Expiratory\s*Flow\s*[:\-]?\s*([\d.]+)', text, re.IGNORECASE)

    if not fev1 or not peak_flow:
        return None, "Unable to extract required asthma values from report"

    # Fallback values if some fields are missing
    data = {
        "Peak_Expiratory_Flow": float(peak_flow.group(1)),
        "FeNO_Level": float(feno.group(1)) if feno else 20.0,
        "Age": 35,
        "Sex": "Female",
        "Family_History": 0,
        "Allergies": "None",
        "Air_Pollution_Level": "Moderate",
        "Smoking_Status": "Never",
        "BMI": 24.0,
        "Physical_Activity_Level": "Moderate",
        "Number_of_ER_Visits": 0,
        "Medication_Adherence": 0.8,
        "Indoor_Smoke_Exposure": 0,
        "Pets_at_Home": 0
    }

    return pd.DataFrame([data]), None


# --------------------------------------------------
# Main prediction function (USED BY app.py)
# --------------------------------------------------
def predict_asthma_from_text(text: str):
    """
    Takes OCR text → extracts features → predicts asthma risk
    """

    input_df, error = extract_asthma_features(text)
    if error:
        return f"❌ Asthma Prediction Failed: {error}"

    try:
        pred = asthma_model.predict(input_df)[0]
        prob = asthma_model.predict_proba(input_df)[0]

        asthma_prob = prob[list(asthma_model.classes_).index(1)]

        if pred == 1:
            return f"🟥 Asthma Detected (Risk: {asthma_prob*100:.1f}%)"
        else:
            return f"🟩 Normal (Asthma Risk: {asthma_prob*100:.1f}%)"

    except Exception as e:
        return f"❌ Asthma Prediction Error: {e}"
