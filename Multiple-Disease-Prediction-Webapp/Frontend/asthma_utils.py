import joblib
import pandas as pd
import numpy as np
import re
import os
from sklearn.impute import SimpleImputer

# --------------------------------------------------
# Compatibility Patch for sklearn 1.8.0
# --------------------------------------------------
def patch_simple_imputer():
    """Fix SimpleImputer compatibility issue with older pickled models"""
    if not hasattr(SimpleImputer, '_fill_dtype'):
        SimpleImputer._fill_dtype = np.dtype('float64')

patch_simple_imputer()

# --------------------------------------------------
# Load Asthma Model
# --------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "models", "asthma_rf_pipeline.pkl")

asthma_model = None

if os.path.exists(model_path):
    try:
        asthma_model = joblib.load(model_path)
    except Exception:
        asthma_model = None


# --------------------------------------------------
# Encoding helpers
# --------------------------------------------------

def encode_sex(sex):
    return 1 if str(sex).lower() == "male" else 0


def encode_allergies(val):
    """
    Robust allergy encoding
    Prevents 'Dust' float conversion errors
    """
    text = str(val).lower().strip()

    none_values = ["none", "no", "n/a", "na", ""]
    if text in none_values:
        return 0

    allergy_keywords = [
        "dust",
        "pollen",
        "pet",
        "dander",
        "mold",
        "mite",
        "mites"
    ]

    for word in allergy_keywords:
        if word in text:
            return 1

    return 0


def encode_pollution(val):
    mapping = {
        "low": 0,
        "moderate": 1,
        "high": 2
    }
    return mapping.get(str(val).lower(), 1)


def encode_smoking(val):
    mapping = {
        "never": 0,
        "former": 1,
        "current": 2
    }
    return mapping.get(str(val).lower(), 0)


def encode_activity(val):
    mapping = {
        "low": 0,
        "moderate": 1,
        "high": 2
    }
    return mapping.get(str(val).lower(), 1)


# --------------------------------------------------
# Prediction using manual parameters
# --------------------------------------------------

def predict_asthma_with_params(
    fev1,
    peak_flow,
    feno,
    age,
    sex,
    family_history,
    allergies,
    air_pollution,
    smoking_status,
    bmi,
    physical_activity,
    er_visits,
    medication_adherence,
    indoor_smoke,
    pets_at_home
):

    if asthma_model is None:
        return "❌ Asthma model not available"

    try:
        # Pre-encode all categorical values BEFORE creating DataFrame
        sex_encoded = int(encode_sex(sex))
        family_encoded = int(family_history)
        allergies_encoded = int(encode_allergies(allergies))
        pollution_encoded = int(encode_pollution(air_pollution))
        smoking_encoded = int(encode_smoking(smoking_status))
        activity_encoded = int(encode_activity(physical_activity))
        
        # Convert numeric inputs
        fev1_num = float(fev1)
        peak_flow_num = float(peak_flow)
        feno_num = float(feno)
        age_num = int(age)
        bmi_num = float(bmi)
        er_visits_num = int(er_visits)
        med_adh_num = float(medication_adherence)
        indoor_smoke_num = int(indoor_smoke)
        pets_num = int(pets_at_home)

        # Create DataFrame with ONLY numeric values (no strings)
        data = {
            "FEV1": [fev1_num],
            "Peak_Expiratory_Flow": [peak_flow_num],
            "FeNO_Level": [feno_num],
            "Age": [age_num],
            "Sex": [sex_encoded],
            "Family_History": [family_encoded],
            "Allergies": [allergies_encoded],
            "Air_Pollution_Level": [pollution_encoded],
            "Smoking_Status": [smoking_encoded],
            "BMI": [bmi_num],
            "Physical_Activity_Level": [activity_encoded],
            "Number_of_ER_Visits": [er_visits_num],
            "Medication_Adherence": [med_adh_num],
            "Indoor_Smoke_Exposure": [indoor_smoke_num],
            "Pets_at_Home": [pets_num]
        }

        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Ensure ALL columns are numeric types
        for col in df.columns:
            df[col] = df[col].astype(float, errors='ignore')
        
        # Fill any NaN values with 0
        df = df.fillna(0)
        
        # Convert to appropriate types
        float_cols = ["FEV1", "Peak_Expiratory_Flow", "FeNO_Level", "BMI", "Medication_Adherence"]
        for col in df.columns:
            try:
                if col in float_cols:
                    df[col] = df[col].astype(float)
                else:
                    df[col] = df[col].astype(int)
            except:
                df[col] = df[col].astype(float)

        # Try to predict
        try:
            pred = asthma_model.predict(df)[0]
            prob = asthma_model.predict_proba(df)[0]
            asthma_prob = prob[list(asthma_model.classes_).index(1)]
            
            # Calculate risk from abnormal parameters
            # This ensures we ALWAYS show risk if abnormal parameters exist
            abnormal_count = 0
            
            if fev1_num < 2.0:
                abnormal_count += 1
            if peak_flow_num < 350:
                abnormal_count += 1
            if feno_num > 25:
                abnormal_count += 1
            if er_visits_num >= 2:
                abnormal_count += 1
            if med_adh_num < 0.8:
                abnormal_count += 1
            if bmi_num >= 25:
                abnormal_count += 1
            if family_encoded == 1:
                abnormal_count += 1
            if smoking_encoded >= 1:  # Former or Current smoker
                abnormal_count += 1
            if pollution_encoded >= 1:  # Moderate or High pollution
                abnormal_count += 1
            if allergies_encoded == 1:
                abnormal_count += 1
            if activity_encoded == 0:  # Low activity
                abnormal_count += 1
            
            # ALWAYS apply minimum risk if abnormal parameters exist
            # This fixes the issue of 0.0% showing when there are abnormal params
            if abnormal_count > 0:
                # Calculate minimum risk: 3% per abnormal parameter (up to 20%)
                min_risk = min(0.03 * abnormal_count, 0.20)
                # Use the higher of model probability or calculated minimum
                asthma_prob = max(asthma_prob, min_risk)

            if pred == 1:
                return f"🟥 Asthma Detected (Risk: {asthma_prob*100:.1f}%)"
            else:
                # Ensure minimum 1% risk display for Normal predictions (never show 0.0%)
                if asthma_prob < 0.01:
                    asthma_prob = 0.01
                return f"🟩 Normal (Asthma Risk: {asthma_prob*100:.1f}%)"
        except Exception as model_err:
            # If model fails, use simple rule-based approach
            return rule_based_prediction(fev1_num, peak_flow_num, feno_num, family_encoded, 
                                        smoking_encoded, er_visits_num, pollution_encoded, 
                                        activity_encoded, allergies_encoded, med_adh_num, bmi_num)

    except Exception as e:
        return f"❌ Asthma Prediction Error: {str(e)}"


def rule_based_prediction(fev1, peak_flow, feno, family_history, smoking, er_visits, pollution, activity, allergies, medication_adherence=0.8, bmi=25):
    """Fallback rule-based prediction when model fails"""
    risk = 0.0
    signals = []
    
    # FeNO > 25 ppb indicates inflammation
    if feno > 25:
        risk += 0.35
        signals.append(f"High FeNO ({feno})")
    
    # Peak flow < 350 indicates obstruction
    if peak_flow < 350:
        risk += 0.30
        signals.append(f"Low Peak Flow ({peak_flow})")
    
    # FEV1 < 2.0
    if fev1 < 2.0:
        risk += 0.15
        signals.append(f"Low FEV1 ({fev1})")
    
    # Multiple ER visits - STRONG INDICATOR
    if er_visits >= 4:
        risk += 0.25  # Increased from 0.10
        signals.append(f"Multiple ER visits ({er_visits})")
    elif er_visits >= 2:
        risk += 0.12  # Increased from 0.05
        signals.append(f"ER visits ({er_visits})")
    
    # Poor medication adherence - CRITICAL
    if medication_adherence < 0.5:
        risk += 0.20  # New: High impact for poor adherence
        signals.append(f"Low Medication Adherence ({medication_adherence*100:.0f}%)")
    elif medication_adherence < 0.8:
        risk += 0.10  # New: Moderate impact for moderate adherence
        signals.append(f"Inadequate Medication Adherence ({medication_adherence*100:.0f}%)")
    
    # BMI - overweight/obese increases asthma risk
    if bmi >= 30:
        risk += 0.08
        signals.append(f"Obesity (BMI: {bmi:.1f})")
    elif bmi >= 25:
        risk += 0.05
        signals.append(f"Overweight (BMI: {bmi:.1f})")
    
    # Family history
    if family_history == 1:
        risk += 0.10  # Increased from 0.08
        signals.append("Family History")
    
    # Current smoker
    if smoking == 2:
        risk += 0.12  # Increased from 0.08
        signals.append("Current Smoker")
    elif smoking == 1:
        risk += 0.08  # Increased from 0.04
        signals.append("Former Smoker")
    
    # High air pollution
    if pollution == 2:
        risk += 0.10  # Increased from 0.08
        signals.append("High Air Pollution")
    elif pollution == 1:
        risk += 0.05
        signals.append("Moderate Air Pollution")
    
    # Allergies
    if allergies == 1:
        risk += 0.08  # Increased from 0.05
        signals.append("Known Allergies")
    
    # Low activity
    if activity == 0:
        risk += 0.05  # Increased from 0.03
        signals.append("Low Activity")
    
    risk = min(risk, 0.99)
    
    # LOWER threshold to 0.35 for better detection with multiple abnormal parameters
    if risk >= 0.35:
        return f"🟥 Asthma Detected (Risk: {risk*100:.1f}%) - {', '.join(signals) if signals else 'Rule-based'}"
    else:
        return f"🟩 Normal (Asthma Risk: {risk*100:.1f}%)"


# --------------------------------------------------
# OCR Text Feature Extraction
# --------------------------------------------------

def extract_value(pattern, text, default):
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    except:
        pass
    return default


def extract_asthma_parameters_from_text(text):
    """
    Extract all asthma assessment parameters from OCR text
    Returns a dict with all parameters for table display
    """
    params = {
        'fev1': extract_value(r'FEV1\s*[:\-]?\s*([\d.]+)', text, 2.5),
        'peak_flow': extract_value(r'(?:Peak Flow|PEF)\s*[:\-]?\s*([\d.]+)', text, 450),
        'feno': extract_value(r'FeNO\s*[:\-]?\s*([\d.]+)', text, 20),
        'age': int(extract_value(r'Age\s*[:\-]?\s*(\d+)', text, 35)),
        'bmi': extract_value(r'BMI\s*[:\-]?\s*([\d.]+)', text, 24),
        'er_visits': int(extract_value(r'ER\s+Visits\s*[:\-]?\s*(\d+)', text, 0)),
        'medication_adherence': extract_value(r'Medication\s+Adherence\s*[:\-]?\s*([\d.]+)', text, 0.8),
    }
    
    # Convert medication adherence if it's in percentage format
    if params['medication_adherence'] > 1:
        params['medication_adherence'] = params['medication_adherence'] / 100.0
    
    # Extract categorical values
    sex_match = re.search(r'(?:Sex|Gender)\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    params['sex'] = sex_match.group(1) if sex_match else "Male"
    
    family_match = re.search(r'Family\s+History\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    params['family_history'] = 1 if family_match and family_match.group(1).lower() in ['yes', 'positive', '1'] else 0
    
    allergy_match = re.search(r'Allergies\s*[:\-]?\s*([^\n\r]+)', text, re.IGNORECASE)
    params['allergies'] = allergy_match.group(1).strip() if allergy_match else "None"
    
    smoking_match = re.search(r'Smoking\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    if smoking_match:
        smoking_text = smoking_match.group(1).lower()
        if 'current' in smoking_text:
            params['smoking_status'] = "Current"
        elif 'former' in smoking_text:
            params['smoking_status'] = "Former"
        else:
            params['smoking_status'] = "Never"
    else:
        params['smoking_status'] = "Never"
    
    pollution_match = re.search(r'Air\s+Pollution\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    if pollution_match:
        pollution_text = pollution_match.group(1).lower()
        if 'high' in pollution_text:
            params['air_pollution'] = "High"
        elif 'low' in pollution_text:
            params['air_pollution'] = "Low"
        else:
            params['air_pollution'] = "Moderate"
    else:
        params['air_pollution'] = "Moderate"
    
    activity_match = re.search(r'Physical\s+Activity\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    if activity_match:
        activity_text = activity_match.group(1).lower()
        if 'high' in activity_text:
            params['physical_activity'] = "High"
        elif 'low' in activity_text:
            params['physical_activity'] = "Low"
        else:
            params['physical_activity'] = "Moderate"
    else:
        params['physical_activity'] = "Moderate"
    
    # Indoor smoke and pets (assume false if not found)
    indoor_smoke_match = re.search(r'Indoor\s+Smoke|Second[- ]?hand\s+Smoke', text, re.IGNORECASE)
    params['indoor_smoke'] = 1 if indoor_smoke_match else 0
    
    pets_match = re.search(r'Pets|Animals', text, re.IGNORECASE)
    params['pets_at_home'] = 1 if pets_match else 0
    
    return params


def predict_asthma_from_text(text):

    if asthma_model is None:
        return "❌ Asthma model not available"

    try:

        fev1 = extract_value(r'FEV1\s*[:\-]?\s*([\d.]+)', text, 2.5)
        peak_flow = extract_value(r'(?:Peak Flow|PEF)\s*[:\-]?\s*([\d.]+)', text, 450)
        feno = extract_value(r'FeNO\s*[:\-]?\s*([\d.]+)', text, 20)

        age = extract_value(r'Age\s*[:\-]?\s*(\d+)', text, 35)
        bmi = extract_value(r'BMI\s*[:\-]?\s*([\d.]+)', text, 24)

        sex_match = re.search(r'(Sex|Gender)\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
        sex = sex_match.group(2) if sex_match else "Male"

        allergy_match = re.search(r'Allergies\s*[:\-]?\s*([^\n\r]+)', text, re.IGNORECASE)
        allergies = allergy_match.group(1) if allergy_match else "None"

        smoking = "Never"
        if re.search(r'Smoking.*Current', text, re.IGNORECASE):
            smoking = "Current"
        elif re.search(r'Smoking.*Former', text, re.IGNORECASE):
            smoking = "Former"

        pollution = "Moderate"
        if re.search(r'Air.*High', text, re.IGNORECASE):
            pollution = "High"
        elif re.search(r'Air.*Low', text, re.IGNORECASE):
            pollution = "Low"

        activity = "Moderate"
        if re.search(r'Physical.*High', text, re.IGNORECASE):
            activity = "High"
        elif re.search(r'Physical.*Low', text, re.IGNORECASE):
            activity = "Low"

        family = 1 if re.search(r'Family.*Yes', text, re.IGNORECASE) else 0
        er_visits = int(extract_value(r'ER\s*Visits\s*[:\-]?\s*(\d+)', text, 0))
        
        # Extract medication adherence - handle both percentage and decimal formats
        medication = extract_value(r'Medication\s*Adherence\s*[:\-]?\s*([\d.]+)', text, 0.8)
        # If value > 1, assume it's a percentage and convert to decimal
        if medication > 1:
            medication = medication / 100.0

        # Call with proper encoding
        return predict_asthma_with_params(
            float(fev1),
            float(peak_flow),
            float(feno),
            int(age),
            sex,
            family,
            allergies,  # Pass as string, will be encoded in predict_asthma_with_params
            pollution,
            smoking,
            float(bmi),
            activity,
            er_visits,
            float(medication),
            0,
            0
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Asthma Prediction Error: {str(e)}"


# --------------------------------------------------
# Assessment Parameters for Table Display
# --------------------------------------------------

def get_asthma_assessment_data(
    fev1, peak_flow, feno, age, sex, family_history, 
    allergies, air_pollution, smoking_status, bmi, 
    physical_activity, er_visits, medication_adherence,
    indoor_smoke, pets_at_home
):
    """
    Generate detailed assessment data for table display
    Similar to lab report formatter - returns DataFrame with TEST, VALUE, UNIT, REFERENCE RANGE, STATUS
    """
    
    assessment_data = []
    
    # ===== Pulmonary Function Tests =====
    # FEV1 (L)
    fev1_ref = "1.5-4.0"
    fev1_status = "Normal" if 1.5 <= fev1 <= 4.0 else "Abnormal"
    assessment_data.append({
        "Test": "FEV1 (Forced Expiratory Volume)",
        "Value": f"{fev1:.2f}",
        "Unit": "L",
        "Reference Range": fev1_ref,
        "Status": fev1_status
    })
    
    # Peak Flow (L/min)
    peak_ref = "350-700"
    peak_status = "Normal" if 350 <= peak_flow <= 700 else "Abnormal"
    assessment_data.append({
        "Test": "Peak Expiratory Flow",
        "Value": f"{peak_flow:.0f}",
        "Unit": "L/min",
        "Reference Range": peak_ref,
        "Status": peak_status
    })
    
    # FeNO (ppb)
    feno_ref = "5-25"
    feno_status = "Normal" if 5 <= feno <= 25 else "Abnormal"
    assessment_data.append({
        "Test": "FeNO Level (Fractional Exhaled NO)",
        "Value": f"{feno:.1f}",
        "Unit": "ppb",
        "Reference Range": feno_ref,
        "Status": feno_status
    })
    
    # ===== Demographics =====
    assessment_data.append({
        "Test": "Age",
        "Value": f"{int(age)}",
        "Unit": "years",
        "Reference Range": "5-80",
        "Status": "Normal"
    })
    
    assessment_data.append({
        "Test": "Sex",
        "Value": sex,
        "Unit": "-",
        "Reference Range": "-",
        "Status": "Normal"
    })
    
    # BMI
    bmi_ref = "18.5-24.9"
    if bmi < 18.5:
        bmi_status = "Abnormal (Underweight)"
    elif 18.5 <= bmi < 25:
        bmi_status = "Normal"
    elif 25 <= bmi < 30:
        bmi_status = "Abnormal (Overweight)"
    else:
        bmi_status = "Abnormal (Obese)"
    
    assessment_data.append({
        "Test": "BMI (Body Mass Index)",
        "Value": f"{bmi:.1f}",
        "Unit": "kg/m²",
        "Reference Range": bmi_ref,
        "Status": bmi_status
    })
    
    # ===== Medical History =====
    assessment_data.append({
        "Test": "Family History of Asthma",
        "Value": "Yes" if family_history else "No",
        "Unit": "-",
        "Reference Range": "No",
        "Status": "Abnormal" if family_history else "Normal"
    })
    
    assessment_data.append({
        "Test": "ER Visits (past year)",
        "Value": f"{int(er_visits)}",
        "Unit": "visits",
        "Reference Range": "0-1",
        "Status": "Abnormal" if er_visits > 1 else "Normal"
    })
    
    assessment_data.append({
        "Test": "Medication Adherence",
        "Value": f"{medication_adherence*100:.0f}%",
        "Unit": "%",
        "Reference Range": ">80%",
        "Status": "Normal" if medication_adherence >= 0.8 else "Abnormal"
    })
    
    # ===== Environmental & Lifestyle Factors =====
    assessment_data.append({
        "Test": "Known Allergies",
        "Value": allergies if allergies != "None" else "None",
        "Unit": "-",
        "Reference Range": "None",
        "Status": "Abnormal" if allergies != "None" else "Normal"
    })
    
    assessment_data.append({
        "Test": "Smoking Status",
        "Value": smoking_status,
        "Unit": "-",
        "Reference Range": "Never",
        "Status": "Abnormal" if smoking_status != "Never" else "Normal"
    })
    
    assessment_data.append({
        "Test": "Air Pollution Level",
        "Value": air_pollution,
        "Unit": "-",
        "Reference Range": "Low",
        "Status": "Abnormal" if air_pollution != "Low" else "Normal"
    })
    
    # ===== Additional Risk Factors =====
    assessment_data.append({
        "Test": "Physical Activity Level",
        "Value": physical_activity,
        "Unit": "-",
        "Reference Range": "Moderate-High",
        "Status": "Abnormal" if physical_activity == "Low" else "Normal"
    })
    
    assessment_data.append({
        "Test": "Indoor Smoke Exposure",
        "Value": "Yes" if indoor_smoke else "No",
        "Unit": "-",
        "Reference Range": "No",
        "Status": "Abnormal" if indoor_smoke else "Normal"
    })
    
    assessment_data.append({
        "Test": "Pets at Home",
        "Value": "Yes" if pets_at_home else "No",
        "Unit": "-",
        "Reference Range": "No Allergen Source",
        "Status": "Abnormal" if pets_at_home else "Normal"
    })
    
    return pd.DataFrame(assessment_data)