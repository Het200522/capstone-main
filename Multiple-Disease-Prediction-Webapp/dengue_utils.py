import re
import joblib
import os

def extract_cbc_values(text):
    """Extract Platelets and WBC from CBC report text"""
    platelets = 150
    wbc = 7
    
    if not text or text.strip() == "":
        return platelets, wbc
    
    try:
        # Look for platelet values
        for line in text.split('\n'):
            if 'platelet' in line.lower() or 'plt' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    platelets = int(numbers[0])
                    break
        
        # Look for WBC values  
        for line in text.split('\n'):
            if 'wbc' in line.lower() or 'white' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    wbc = int(numbers[0])
                    break
    except:
        pass
    
    return platelets, wbc

def predict_dengue(text):
    """Predict Dengue based on CBC values"""
    if not text or text.strip() == "":
        return "Please provide CBC lab report text or values"
    
    try:
        platelets, wbc = extract_cbc_values(text)

        # Try to load model
        model_path = os.path.join(os.path.dirname(__file__), "models", "best_dengue_model.pkl")
        scaler_path = os.path.join(os.path.dirname(__file__), "models", "scaler.pkl")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                X = scaler.transform([[platelets, wbc]])
                pred = model.predict(X)[0]
                return "✅ Normal - Negative for Dengue" if pred == 0 else "⚠️ Positive for Dengue"
            except Exception as e:
                pass
        
        # Fallback heuristic if model not available
        if platelets < 100 and wbc > 10:
            return "⚠️ High Risk - Low platelets + High WBC (Possible Dengue)"
        elif platelets < 100:
            return "⚠️ Warning - Low platelets detected (Normal: 150-400)"
        elif wbc > 11:
            return "⚠️ Warning - High WBC detected (Normal: 4-11)"
        else:
            return "✅ Normal - CBC values within normal range"
                
    except Exception as e:
        return f"Prediction Error: {str(e)}"


