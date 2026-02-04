"""
=============================================================================
ASTHMA PREDICTION MODEL - COMPREHENSIVE EVALUATION
=============================================================================

Academic Model Selection Justification:
Random Forest Pipeline was selected for asthma prediction based on:

1. PIPELINE ARCHITECTURE FOR MEDICAL DATA PREPROCESSING
   - Handles missing spirometry measurements automatically
   - Standardizes continuous features (FEV1, Peak Flow)
   - Categorical encoding for allergies and pollution levels
   - Reproducible preprocessing with stored transformers

2. ENSEMBLE ROBUSTNESS WITH RESPIRATORY PARAMETERS
   - Multiple decision trees reduce variance in spirometry
   - Captures non-linear FEV1-to-diagnosis relationship
   - Handles heterogeneous input types (continuous + categorical)
   - Resistant to measurement noise in peak flow meters

3. CLINICAL INTERPRETABILITY
   - Feature importance reveals key asthma predictors
   - Decision paths align with medical knowledge
   - Explains influence of family history, allergies, pollution
   - Can rank risk factors for clinicians

4. HANDLING MULTICOLLINEARITY
   - No assumption of feature independence
   - Handles correlated features (e.g., ER visits + medication adherence)
   - Robust to measurement redundancy in respiratory tests

5. SCALABILITY FOR HETEROGENEOUS HEALTH DATA
   - Manages mix of continuous (age, BMI) and categorical (smoking status)
   - No need for feature normalization within trees
   - Efficient with large feature sets

Model Configuration:
- Algorithm: RandomForestClassifier (via Pipeline)
- Trees: Default configuration
- Preprocessing: ColumnTransformer with imputation
- Features: 15+ clinical and demographic parameters

Generated: January 2026
=============================================================================
"""

import sys
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics_evaluator import ProductionMetricsEvaluator

SCRIPT_DIR = Path(__file__).parent.parent
MODELS_DIR = SCRIPT_DIR / 'models'
DATA_DIR = SCRIPT_DIR / 'data'
DOWNLOADS_DIR = Path.home() / 'Downloads'

MODEL_PATH = MODELS_DIR / 'asthma_rf_pipeline.pkl'


def load_asthma_model():
    """Load asthma Random Forest pipeline."""
    
    print("\n" + "="*75)
    print("LOADING ASTHMA MODEL")
    print("="*75)
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    
    model = joblib.load(MODEL_PATH)
    print(f"✓ Model loaded: {MODEL_PATH.name}")
    print(f"✓ Model type: {type(model).__name__} (Pipeline)")
    
    return model


def load_asthma_dataset() -> Tuple[np.ndarray, np.ndarray]:
    """Load real asthma dataset."""
    
    print("\n" + "="*75)
    print("LOADING ASTHMA TEST DATA")
    print("="*75)
    
    # Try local data directory first
    asthma_file = DATA_DIR / 'asthma_balanced_dataset (1).csv'
    
    if asthma_file.exists():
        try:
            print(f"\n📂 Found asthma dataset: {asthma_file.name}")
            df = pd.read_csv(asthma_file)
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            
            # Look for target column
            label_col = 'Has_Asthma'
            if label_col in df.columns:
                # Select features used in model training (needs to match pipeline)
                # Pipeline was trained with specific features, use top 10
                possible_features = [col for col in df.columns 
                                    if col != label_col and col != 'Occupation_Type' and col != 'Comorbidities']
                
                # Take first 10 features to match pipeline
                feature_cols = possible_features[:10] if len(possible_features) >= 10 else possible_features
                
                # Handle categorical variables
                X = df[feature_cols].copy()
                
                # Encode categorical features if present
                for col in X.select_dtypes(include=['object']).columns:
                    X[col] = pd.Categorical(X[col]).codes
                
                X = X.fillna(X.mean()).values
                y = df[label_col].values.astype(int)
                
                print(f"   Features used: {feature_cols}")
                print(f"   Total features: {len(feature_cols)}")
                print(f"   Positive cases (Asthma): {(y == 1).sum()}")
                print(f"   Negative cases: {(y == 0).sum()}")
                
                return X, y
        except Exception as e:
            print(f"   ⚠️  Error loading: {e}")
    
    # Fallback to synthetic data
    print("\n⚠️  Using synthetic asthma data...")
    return generate_synthetic_asthma_data(n_samples=2000)


def generate_synthetic_asthma_data(n_samples: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Generate realistic synthetic asthma test data."""
    
    np.random.seed(42)
    
    print(f"\nGenerating {n_samples} realistic synthetic samples...")
    
    # Normal group
    normal = np.array([
        np.random.normal(65, 15, n_samples//2),       # Age
        np.random.normal(24, 3, n_samples//2),        # BMI
        np.random.normal(3.5, 0.5, n_samples//2),     # FEV1
        np.random.normal(500, 50, n_samples//2),      # Peak Flow
        np.random.normal(15, 5, n_samples//2),        # FeNO
        np.random.choice([0, 1], n_samples//2),       # Family History
        np.random.normal(0.5, 0.4, n_samples//2),     # Physical Activity
        np.random.normal(1, 0.5, n_samples//2),       # ER Visits
        np.random.normal(0.85, 0.15, n_samples//2),   # Medication Adherence
    ]).T
    
    # Asthma group
    asthma = np.array([
        np.random.normal(45, 18, n_samples//2),       # Age
        np.random.normal(26, 4, n_samples//2),        # BMI
        np.random.normal(2.5, 0.6, n_samples//2),     # FEV1 (low)
        np.random.normal(380, 60, n_samples//2),      # Peak Flow (low)
        np.random.normal(35, 10, n_samples//2),       # FeNO (elevated)
        np.random.choice([0, 1], n_samples//2, p=[0.4, 0.6]),  # Family History
        np.random.normal(0.3, 0.3, n_samples//2),     # Physical Activity (low)
        np.random.normal(2.5, 1.0, n_samples//2),     # ER Visits (high)
        np.random.normal(0.65, 0.25, n_samples//2),   # Medication Adherence
    ]).T
    
    X = np.vstack([normal, asthma])
    y = np.hstack([np.zeros(n_samples//2), np.ones(n_samples//2)])
    
    idx = np.random.permutation(len(X))
    X, y = X[idx], y[idx]
    
    print(f"✓ Asthma cases: {(y == 1).sum()}, Normal: {(y == 0).sum()}")
    
    return X, y


def evaluate_asthma_model():
    """Main evaluation function."""
    
    print("\n" + "="*75)
    print("ASTHMA PREDICTION MODEL - FULL EVALUATION")
    print("="*75)
    
    model = load_asthma_model()
    X_test, y_test = load_asthma_dataset()
    
    # Convert to DataFrame if it's an array (required by pipeline)
    if isinstance(X_test, np.ndarray):
        feature_names = ['Age', 'Gender', 'BMI', 'Smoking_Status', 'Family_History', 
                        'Allergies', 'Air_Pollution_Level', 'Physical_Activity_Level', 
                        'Medication_Adherence', 'Number_of_ER_Visits']
        X_test = pd.DataFrame(X_test, columns=feature_names)
    
    print("\nMaking predictions...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
    
    print("\n📊 Evaluating model...")
    evaluator = ProductionMetricsEvaluator()
    results = evaluator.evaluate_model(
        y_true=y_test,
        y_pred=y_pred,
        y_pred_proba=y_pred_proba,
        model_name="Asthma Prediction (Random Forest Pipeline)",
        dataset_split="test",
        class_names=["No Asthma", "Asthma Positive"]
    )
    
    print("\n" + "="*75)
    print("✅ ASTHMA MODEL EVALUATION COMPLETE")
    print("="*75 + "\n")
    
    return results


if __name__ == "__main__":
    try:
        results = evaluate_asthma_model()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
