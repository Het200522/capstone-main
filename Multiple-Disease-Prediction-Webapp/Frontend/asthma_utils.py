import joblib
import pandas as pd
import re
import os

# --------------------------------------------------
# Compatibility patch for sklearn 1.8.0
# --------------------------------------------------
# Fix for SimpleImputer compatibility with older models
from sklearn.impute import SimpleImputer

# Patch SimpleImputer to add missing _fill_dtype attribute if needed
original_getstate = SimpleImputer.__getstate__ if hasattr(SimpleImputer, '__getstate__') else None

def patched_getattribute(self, name):
    if name == '_fill_dtype':
        # Return a default value for the missing attribute
        if not hasattr(self, '_fill_dtype_internal'):
            import numpy as np
            self._fill_dtype_internal = np.dtype('float64')
        return self._fill_dtype_internal
    return object.__getattribute__(self, name)

# Apply the patch
SimpleImputer.__getattribute__ = patched_getattribute

# --------------------------------------------------
# Load Asthma model pipeline (Random Forest pipeline)
# --------------------------------------------------
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "models", "asthma_rf_pipeline.pkl")

asthma_model = None
if os.path.exists(model_path):
    try:
        asthma_model = joblib.load(model_path)
        # Silent load - don't print during import
    except Exception as e:
        asthma_model = "unavailable"
else:
    asthma_model = "unavailable"

# --------------------------------------------------
# Extract asthma parameters from OCR text
# --------------------------------------------------
def extract_asthma_features(text: str):
    """
    Extract required asthma features from OCR-extracted lab report text
    """
    
    def safe_extract_float(pattern, text, default):
        """Safely extract float value from text with regex"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the last captured group that is a number
                for group in match.groups()[::-1]:
                    if group:
                        val = float(group)
                        return val
            return default
        except (ValueError, TypeError, AttributeError):
            return default

    # Enhanced patterns for better extraction
    # Try multiple patterns for each value
    
    # FEV1 - try different formats
    fev1_value = safe_extract_float(r'FEV1\s*[:\-]?\s*([\d.]+)', text, None)
    if fev1_value is None:
        fev1_value = safe_extract_float(r'Forced\s*Expiratory\s*Volume.*?(\d+\.?\d*)', text, 2.5)
    else:
        fev1_value = fev1_value if fev1_value else 2.5
    
    # Peak Flow - improved pattern
    peak_flow_value = safe_extract_float(r'Peak\s*(?:Expiratory\s*)?Flow\s*[:\-]?\s*([\d.]+)', text, None)
    if peak_flow_value is None:
        peak_flow_value = safe_extract_float(r'PEF\s*[:\-]?\s*([\d.]+)', text, 450.0)
    else:
        peak_flow_value = peak_flow_value if peak_flow_value else 450.0
    
    # FeNO - improved pattern
    feno_value = safe_extract_float(r'FeNO\s*(?:Level)?\s*[:\-]?\s*([\d.]+)', text, None)
    if feno_value is None:
        feno_value = safe_extract_float(r'Fractional\s*exhaled\s*NO.*?(\d+\.?\d*)', text, 20.0)
    else:
        feno_value = feno_value if feno_value else 20.0
    
    # Extract age
    age_value = safe_extract_float(r'Age\s*[:\-]?\s*(\d+)', text, 35)
    age_value = int(age_value) if age_value else 35
    
    # Extract BMI
    bmi_value = safe_extract_float(r'BMI\s*[:\-]?\s*([\d.]+)', text, 24.0)
    bmi_value = bmi_value if bmi_value else 24.0
    
    # Extract gender
    gender_match = re.search(r'(?:Gender|Sex)\s*[:\-]?\s*(\w+)', text, re.IGNORECASE)
    sex_value = "Male" if gender_match and 'male' in gender_match.group(1).lower() else "Female"
    
    # Extract smoking status
    smoking_status = "Never"
    if re.search(r'Smoking\s*[:\-]?\s*(?:Current|Yes)', text, re.IGNORECASE):
        smoking_status = "Current"
    elif re.search(r'Smoking\s*[:\-]?\s*Former', text, re.IGNORECASE):
        smoking_status = "Former"
    
    # Extract family history
    family_history = 1 if re.search(r'Family\s*History\s*[:\-]?\s*(?:Yes|Positive|True)', text, re.IGNORECASE) else 0
    
    # Extract allergies
    allergies = "None"
    if re.search(r'Allergies\s*[:\-]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE):
        match = re.search(r'Allergies\s*[:\-]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        allergy_text = match.group(1).strip().lower()
        if allergy_text and allergy_text not in ['none', 'no', 'n/a']:
            allergies = match.group(1).strip()
    
    # Extract air pollution level
    air_pollution = "Moderate"
    if re.search(r'Air\s*Pollution\s*Level\s*[:\-]?\s*High', text, re.IGNORECASE):
        air_pollution = "High"
    elif re.search(r'Air\s*Pollution\s*Level\s*[:\-]?\s*Low', text, re.IGNORECASE):
        air_pollution = "Low"
    
    # Extract physical activity level
    physical_activity = "Moderate"
    if re.search(r'Physical\s*Activity\s*Level\s*[:\-]?\s*High', text, re.IGNORECASE):
        physical_activity = "High"
    elif re.search(r'Physical\s*Activity\s*Level\s*[:\-]?\s*Low', text, re.IGNORECASE):
        physical_activity = "Low"
    
    # Extract ER visits
    er_visits = 0
    er_match = re.search(r'(?:Number\s*of\s*)?ER\s*Visits\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if er_match:
        er_visits = int(er_match.group(1))
    
    # Extract medication adherence
    medication_adherence = safe_extract_float(r'Medication\s*Adherence\s*[:\-]?\s*([\d.]+)', text, 0.8)
    medication_adherence = medication_adherence if medication_adherence else 0.8
    
    # Check for positive risk indicators
    has_positive_risk = re.search(r'(?:Asthma\s*Risk|Risk\s*Level)\s*[:\-]?\s*(?:POSITIVE|High|Yes)', text, re.IGNORECASE)

    data = {
        "FEV1": fev1_value,
        "Peak_Expiratory_Flow": peak_flow_value,
        "FeNO_Level": feno_value,
        "Age": age_value,
        "Sex": sex_value,
        "Family_History": family_history,
        "Allergies": allergies,
        "Air_Pollution_Level": air_pollution,
        "Smoking_Status": smoking_status,
        "BMI": bmi_value,
        "Physical_Activity_Level": physical_activity,
        "Number_of_ER_Visits": er_visits,
        "Medication_Adherence": medication_adherence,
        "Indoor_Smoke_Exposure": 0,
        "Pets_at_Home": 0,
        "has_positive_risk": has_positive_risk is not None
    }

    return pd.DataFrame([data]), None


# --------------------------------------------------
# Create prediction function with custom parameters
# --------------------------------------------------
def predict_asthma_with_params(fev1, peak_flow, feno, age, sex, family_history, 
                               allergies, air_pollution, smoking_status, bmi, 
                               physical_activity, er_visits, medication_adherence, 
                               indoor_smoke, pets_at_home):
    """
    Predict asthma with comprehensive parameters using the trained ML model
    """
    
    # Check if model is available
    if asthma_model == "unavailable":
        return "❌ Asthma model not available. Please check model file."
    
    # Encode categorical variables
    sex_encoded = 1 if sex == "Male" else 0
    family_history_encoded = 1 if family_history else 0
    allergies_encoded = 0 if allergies == "None" else 1
    
    # Air pollution level encoding
    air_pollution_map = {"Low": 0, "Moderate": 1, "High": 2}
    air_pollution_encoded = air_pollution_map.get(air_pollution, 1)
    
    # Smoking status encoding
    smoking_map = {"Never": 0, "Former": 1, "Current": 2}
    smoking_encoded = smoking_map.get(smoking_status, 0)
    
    # Physical activity encoding
    activity_map = {"Low": 0, "Moderate": 1, "High": 2}
    activity_encoded = activity_map.get(physical_activity, 1)
    
    # Create dataframe with all parameters - ensure all values are numeric
    data = {
        "FEV1": float(fev1),
        "Peak_Expiratory_Flow": float(peak_flow),
        "FeNO_Level": float(feno),
        "Age": int(age),
        "Sex": sex_encoded,
        "Family_History": int(family_history_encoded),
        "Allergies": int(allergies_encoded),
        "Air_Pollution_Level": int(air_pollution_encoded),
        "Smoking_Status": int(smoking_encoded),
        "BMI": float(bmi),
        "Physical_Activity_Level": int(activity_encoded),
        "Number_of_ER_Visits": int(er_visits),
        "Medication_Adherence": float(medication_adherence),
        "Indoor_Smoke_Exposure": int(1 if indoor_smoke else 0),
        "Pets_at_Home": int(1 if pets_at_home else 0)
    }
    
    input_df = pd.DataFrame([data])
    
    # Use the trained model for prediction
    try:
        pred = asthma_model.predict(input_df)[0]
        prob = asthma_model.predict_proba(input_df)[0]
        asthma_prob = prob[list(asthma_model.classes_).index(1)]

        if pred == 1:
            return f"🟥 Asthma Detected (Risk: {asthma_prob*100:.1f}%)"
        else:
            return f"🟩 Normal (Asthma Risk: {asthma_prob*100:.1f}%)"

    except Exception as e:
        return f"❌ Asthma Prediction Error: {str(e)}"


# --------------------------------------------------
# Main prediction function (USED BY app.py for text)
# --------------------------------------------------
def predict_asthma_from_text(text: str):
    """
    Takes OCR text → extracts features → predicts asthma risk using trained ML model
    """

    input_df, error = extract_asthma_features(text)
    if error:
        return f"❌ Asthma Prediction Failed: {error}"

    # Check if model is available
    if asthma_model == "unavailable":
        return "❌ Asthma model not available. Please check model file."

    # Encode categorical variables in the extracted dataframe
    try:
        # Sex encoding
        sex_map = {"Male": 1, "Female": 0}
        if "Sex" in input_df.columns:
            input_df["Sex"] = input_df["Sex"].map(sex_map).fillna(0).astype(int)
        
        # Allergies encoding
        allergies_map = {"None": 0}
        if "Allergies" in input_df.columns:
            input_df["Allergies"] = input_df["Allergies"].apply(lambda x: 1 if x != "None" else 0).astype(int)
        
        # Air pollution encoding
        air_pollution_map = {"Low": 0, "Moderate": 1, "High": 2}
        if "Air_Pollution_Level" in input_df.columns:
            input_df["Air_Pollution_Level"] = input_df["Air_Pollution_Level"].map(air_pollution_map).fillna(1).astype(int)
        
        # Smoking status encoding
        smoking_map = {"Never": 0, "Former": 1, "Current": 2}
        if "Smoking_Status" in input_df.columns:
            input_df["Smoking_Status"] = input_df["Smoking_Status"].map(smoking_map).fillna(0).astype(int)
        
        # Physical activity encoding
        activity_map = {"Low": 0, "Moderate": 1, "High": 2}
        if "Physical_Activity_Level" in input_df.columns:
            input_df["Physical_Activity_Level"] = input_df["Physical_Activity_Level"].map(activity_map).fillna(1).astype(int)
        
        # Store the positive risk flag before dropping it
        has_positive_risk = input_df.get('has_positive_risk', pd.Series([False]))[0] if 'has_positive_risk' in input_df.columns else False
        
        # Remove non-model features
        if 'has_positive_risk' in input_df.columns:
            input_df = input_df.drop('has_positive_risk', axis=1)
        
        # Ensure all columns are numeric
        input_df = input_df.astype({col: float if col in ["FEV1", "Peak_Expiratory_Flow", "FeNO_Level", "BMI", "Medication_Adherence"] else int 
                                    for col in input_df.columns})
    except Exception as e:
        return f"❌ Feature Encoding Error: {str(e)}"

    # Use the trained model for prediction
    try:
        pred = asthma_model.predict(input_df)[0]
        prob = asthma_model.predict_proba(input_df)[0]

        asthma_prob = prob[list(asthma_model.classes_).index(1)]

        if pred == 1:
            return f"🟥 Asthma Detected (Risk: {asthma_prob*100:.1f}%)"
        else:
            return f"🟩 Normal (Asthma Risk: {asthma_prob*100:.1f}%)"

    except Exception as e:
        # Fallback: Rule-based prediction if model fails
        try:
            fev1 = input_df['FEV1'].values[0]
            feno = input_df['FeNO_Level'].values[0]
            peak_flow = input_df['Peak_Expiratory_Flow'].values[0]
            family_history = input_df['Family_History'].values[0]
            smoking_status = input_df['Smoking_Status'].values[0]
            er_visits = input_df['Number_of_ER_Visits'].values[0]
            air_pollution = input_df['Air_Pollution_Level'].values[0]
            physical_activity = input_df['Physical_Activity_Level'].values[0]
            
            risk = 0.0
            signals = []
            
            # Check for explicit positive risk marker
            if input_df.get('has_positive_risk', pd.Series([False]))[0]:
                return f"🟥 Asthma Detected - Positive risk assessment from report (100.0%)"
            
            # FeNO > 25 ppb indicates eosinophilic inflammation (STRONG indicator)
            if feno > 25:
                risk += 0.4
                signals.append(f"High FeNO ({feno})")
            
            # Peak flow < 350 indicates significant obstruction (STRONG indicator)
            if peak_flow < 350:
                risk += 0.35
                signals.append(f"Low Peak Flow ({peak_flow})")
            
            # FEV1 < 2.0 indicates airway obstruction
            if fev1 < 2.0:
                risk += 0.2
                signals.append(f"Low FEV1 ({fev1})")
            
            # Multiple ER visits suggests chronic disease
            if er_visits >= 4:
                risk += 0.15
                signals.append(f"Multiple ER visits ({er_visits})")
            elif er_visits >= 2:
                risk += 0.1
                signals.append(f"ER visits ({er_visits})")
            
            # Family history
            if family_history == 1:
                risk += 0.1
                signals.append("Family History positive")
            
            # Smoking (current smoker)
            if smoking_status == 2:
                risk += 0.1
                signals.append("Current Smoker")
            elif smoking_status == 1:
                risk += 0.05
                signals.append("Former Smoker")
            
            # High air pollution exposure
            if air_pollution == 2:  # High
                risk += 0.1
                signals.append("High Air Pollution")
            
            # Low physical activity
            if physical_activity == 0:  # Low
                risk += 0.05
                signals.append("Low Physical Activity")
            
            risk = min(risk, 1.0)
            
            if risk >= 0.5:
                return f"🟥 Asthma Detected (Risk: {risk*100:.1f}%) - {', '.join(signals)}"
            else:
                return f"🟩 Normal (Asthma Risk: {risk*100:.1f}%)"
        except Exception as e2:
            return f"❌ Asthma Prediction Error: {str(e)}"

