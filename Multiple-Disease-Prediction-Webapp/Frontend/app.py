import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import re
from PIL import Image
from streamlit_option_menu import option_menu

# ---------------- OCR imports ----------------
import pytesseract
from pdf2image import convert_from_path
import tempfile

# ---------------- UTILS IMPORTS ----------------
from dengue_utils import predict_dengue
from asthma_utils import predict_asthma_from_text, predict_asthma_with_params
from pneumonia_utils import predict_pneumonia
from lab_report_formatter import format_report_for_display, CBCReportFormatter

# ---------------- PATH SETUP ----------------
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ---------------- HELPER FUNCTIONS ----------------
def get_positive_risk(model, features, default_high=0.8, default_low=0.2, positive_pred=True):
    risk = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            risk = float(proba[1]) if len(proba) == 2 else float(np.max(proba))
    except Exception:
        risk = None

    if risk is None:
        risk = default_high if positive_pred else default_low

    return risk


def show_risk(message, risk_score):
    if risk_score is None:
        st.info(message)
        return

    msg = f"{message} | Estimated risk: {risk_score * 100:.1f}%"

    if risk_score >= 0.7:
        st.error(msg)
    elif risk_score >= 0.4:
        st.warning(msg)
    else:
        st.success(msg)


# ---------------- LOAD MODELS ----------------
def load_model(path):
    try:
        return joblib.load(path)
    except Exception:
        return None




# ---------------- SIDEBAR ----------------
with st.sidebar:
    selected = option_menu(
        "Multiple Disease Prediction",
        [
            "Disease Prediction",
            "Dengue Prediction",
            "Asthma Prediction",
            "Pneumonia Prediction"
        ],
        icons=["activity", "bug", "wind", "image"],
        default_index=0
    )

# ---------------- HOME ----------------
if selected == "Disease Prediction":
    st.title("🩺 Multiple Disease Prediction System")
    st.write("""
    This system predicts multiple diseases using:
    • Machine Learning  
    • OCR-based Lab Report Analysis  
    • Medical Rule-based Screening  
    • CNN-based X-ray Image Classification  
    """)

# ---------------- DENGUE ----------------
if selected == "Dengue Prediction":
    st.title("🦟 Dengue Prediction (CBC Analysis)")

    mode = st.radio("Select Input Mode", ["Upload PDF (OCR)", "Manual Input"])

    # ---- PDF MODE ----
    if mode == "Upload PDF (OCR)":
        uploaded_file = st.file_uploader("Upload CBC Report (PDF)", type=["pdf"])

        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name

            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            images = convert_from_path(pdf_path)
            text = "".join(pytesseract.image_to_string(img) for img in images)

            # Debug: Show OCR text length
            st.write(f"DEBUG: OCR extracted {len(text)} characters")
            
            # Display extracted values in simple table format
            try:
                # Extract patient info
                patient_info = CBCReportFormatter.extract_patient_info(text)
                cbc_values = CBCReportFormatter.parse_cbc_report(text)
                st.write(f"DEBUG: Extracted {len([v for v in cbc_values.values() if v is not None])}/18 values")
                
                # Display lab and patient info
                st.subheader("🏥 Report Information")
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Lab**: {patient_info.get('Lab', 'N/A')}")
                col2.write(f"**Branch**: {patient_info.get('Branch', 'N/A')}")
                col3.write(f"**Contact**: {patient_info.get('Contact', 'N/A')}")
                
                st.subheader("👤 Patient Information")
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1.5, 1.5])
                with col1:
                    st.write(f"**Name**: {patient_info.get('Name', 'N/A')}")
                col2.metric("Gender", patient_info.get("Gender", "N/A"))
                col3.metric("Age", patient_info.get("Age", "N/A"))
                col4.metric("Sample ID", patient_info.get("Sample ID", "N/A"))
                col5.metric("Date", patient_info.get("Date", "N/A"))
                
                # Display CBC values with units and reference ranges
                st.subheader("📊 CBC Test Results")
                cbc_with_ranges = CBCReportFormatter.get_cbc_report_with_ranges(text)
                
                # Debug: Show extracted text
                with st.expander("📄 View OCR Extracted Text"):
                    st.text_area("Raw OCR Text", text, height=300)
                
                if cbc_with_ranges:
                    data = []
                    for test_name, info in cbc_with_ranges.items():
                        data.append({
                            "Test": test_name,
                            "Value": info["Value"],
                            "Unit": info["Unit"],
                            "Reference Range": info["Reference Range"],
                            "Status": info["Status"]
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # Create HTML table with conditional coloring
                    html = '<table style="width:100%; border-collapse: collapse; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                    html += '<tr style="background-color: #2c3e50; color: white; font-weight: bold; text-align: left; padding: 12px;">'
                    for col in df.columns:
                        html += f'<th style="padding: 12px; border: 1px solid #34495e; text-align: left;">{col}</th>'
                    html += '</tr>'
                    
                    # Add rows with conditional styling
                    for idx, row in df.iterrows():
                        status = row['Status']
                        if status == "Abnormal":
                            row_style = 'background-color: #fadbd8; color: #7b241c;'  # Light red with dark red text
                        else:
                            row_style = 'background-color: #d5f4e6; color: #0b5345;'  # Light green with dark green text
                        
                        html += f'<tr style="{row_style} border-bottom: 1px solid #bdc3c7;">'
                        for col in df.columns:
                            value = row[col]
                            # Format numeric values to 2 decimal places
                            if isinstance(value, float):
                                value = f"{value:.2f}"
                            html += f'<td style="padding: 10px; border: 1px solid #ecf0f1;">{value}</td>'
                        html += '</tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.warning("No values extracted from report")
                    
            except Exception as e:
                st.warning(f"Could not extract values: {str(e)}")

            if st.button("Predict Dengue (PDF)"):
                message, risk = predict_dengue(text)
                show_risk(message, risk)

    # ---- MANUAL MODE (FIXED) ----
    else:
        st.subheader("Manual Input - CBC Values")

        col1, col2 = st.columns(2)
        with col1:
            platelets = st.number_input("Platelets (×10³ / µL)", value=300.0, min_value=1.0)
        with col2:
            wbc = st.number_input("WBC (×10³ / µL)", value=7.0, min_value=0.1)

        if st.button("Predict Dengue (Manual)"):
            platelets_val = platelets * 1000 if platelets < 10000 else platelets
            wbc_val = wbc * 1000 if wbc < 100 else wbc

            fake_text = f"Platelet Count : {platelets_val}\nWBC : {wbc_val}"
            message, risk = predict_dengue(fake_text)
            show_risk(message, risk)

# ---------------- ASTHMA ----------------
if selected == "Asthma Prediction":
    st.title("🫁 Asthma Prediction")

    mode = st.radio("Select Mode", ["Upload PDF (OCR)", "Manual Input"])

    if mode == "Upload PDF (OCR)":
        uploaded_file = st.file_uploader("Upload Asthma Report (PDF)", type=["pdf"])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name

            images = convert_from_path(pdf_path)
            text = "".join(pytesseract.image_to_string(img) for img in images)
            st.text_area("Extracted Text", text, height=250)

            if st.button("Predict Asthma"):
                result = predict_asthma_from_text(text)
                risk = 0.8 if "Detected" in result else 0.2
                show_risk(result, risk)

    elif mode == "Manual Input":
        fev1 = st.number_input("FEV1 (L)", value=2.5)
        peak_flow = st.number_input("Peak Flow (L/min)", value=450.0)
        feno = st.number_input("FeNO", value=20.0)
        age = st.slider("Age", 5, 80, 35)
        sex = st.selectbox("Sex", ["Male", "Female"])
        bmi = st.number_input("BMI", value=24.0)
        family_history = st.checkbox("Family History")

        if st.button("Predict Asthma"):
            result = predict_asthma_with_params(
                float(fev1), float(peak_flow), float(feno), int(age), sex, family_history,
                "None", "Moderate", "Never", float(bmi), "Moderate",
                0, 0.8, False, False
            )
            risk = 0.8 if "Detected" in result else 0.2
            show_risk(result, risk)

# ---------------- PNEUMONIA ----------------
if selected == "Pneumonia Prediction":
    st.title("🩻 Pneumonia Detection")

    uploaded_file = st.file_uploader("Upload Chest X-ray", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original X-ray")
            st.image(image, width=300)

        if st.button("🔍 Detect Pneumonia", key="pneumonia_detect"):
            with st.spinner("Analyzing X-ray..."):
                result, confidence, pneumonia_type, annotated_image = predict_pneumonia(image)
            
            with col2:
                st.subheader("Analysis Result")
                
                # Display annotated image with pneumonia areas highlighted
                st.image(annotated_image, width=300, caption="Highlighted Analysis")
                
                # Display results
                st.markdown("---")
                if confidence >= 0.48:
                    st.error(f"**⚠️ PNEUMONIA DETECTED**")
                    st.metric("Confidence", f"{confidence*100:.1f}%")
                    
                    # Show pneumonia type
                    type_colors = {
                        "COVID-19": "🔴",
                        "Bacterial": "🟠", 
                        "Viral": "🟡",
                        "Unknown": "⚪"
                    }
                    
                    color = type_colors.get(pneumonia_type, "⚪")
                    st.markdown(f"**Type:** {color} {pneumonia_type}")
                    
                    # Show description
                    type_descriptions = {
                        "COVID-19": "Ground-glass opacities, often bilateral with peripheral distribution",
                        "Bacterial": "Lobar consolidation with clear margins and air bronchograms",
                        "Viral": "Diffuse bilateral interstitial infiltrates with peribronchial thickening",
                        "Unknown": "Abnormal opacities detected but type classification uncertain"
                    }
                    st.info(f"📋 {type_descriptions.get(pneumonia_type, 'Abnormal patterns detected')}")
                else:
                    st.success(f"**✓ NO PNEUMONIA DETECTED**")
                    st.metric("Confidence", f"{(1-confidence)*100:.1f}%")
                    st.info("Chest X-ray appears normal")
