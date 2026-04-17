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
from asthma_utils import predict_asthma_from_text, predict_asthma_with_params, get_asthma_assessment_data, extract_asthma_parameters_from_text
from pneumonia_utils import predict_pneumonia
from lab_report_formatter import format_report_for_display, CBCReportFormatter

# ================ MEDICAL THEME STYLING WITH ADVANCED ANIMATIONS ================
# Medical Color Scheme: Soft Teal, Light Cyan, White, Gray, Black
MEDICAL_COLORS = {
    "light_green": "#E8F5E9",      # Very light green (background)
    "green": "#4CAF50",             # Medical green
    "dark_green": "#2E7D32",        # Dark green (accents)
    "light_blue": "#E3F2FD",        # Light blue
    "blue": "#1976D2",              # Medical blue
    "dark_blue": "#0D47A1",         # Dark blue
    "white": "#FFFFFF",             # White
    "light_gray": "#F5F5F5",        # Light gray
    "gray": "#757575",              # Gray
    "dark_gray": "#424242",         # Dark gray
    "black": "#212121",             # Black
    "error": "#D32F2F",             # Error red
    "warning": "#F57C00",           # Warning orange
    "success": "#388E3C",           # Success green
    # Modern Medical Theme Colors
    "teal": "#2EC4B6",              # Soft teal (primary)
    "light_cyan": "#E8F8F7",        # Light cyan (background)
    "dark_teal": "#1A9A8E",         # Dark teal (accents)
}

# Apply advanced modern medical theme with glassmorphism
def apply_medical_theme():
    st.set_page_config(
        page_title="Medical Disease Prediction System",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    custom_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        /* Modern Medical Dashboard Background */
        .main {{
            background: linear-gradient(-45deg, #f0f9ff, #e8f5e9, #f3e5f5, #fce4ec);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: {MEDICAL_COLORS['black']};
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* Typography enhancements */
        h1 {{
            color: {MEDICAL_COLORS['dark_blue']};
            font-weight: 700;
            font-size: 2.5em;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }}
        
        h2 {{
            color: {MEDICAL_COLORS['dark_blue']};
            font-weight: 700;
            font-size: 2em;
            letter-spacing: -0.3px;
        }}
        
        h3 {{
            color: {MEDICAL_COLORS['dark_blue']};
            font-weight: 600;
            font-size: 1.3em;
            letter-spacing: -0.2px;
        }}
        
        h4 {{
            color: {MEDICAL_COLORS['dark_blue']};
            font-weight: 600;
            font-size: 1.1em;
        }}
        
        p {{
            font-size: 15px;
            line-height: 1.6;
            color: {MEDICAL_COLORS['dark_gray']};
        }}
        
        /* Subtitle styling */
        .subtitle {{
            color: {MEDICAL_COLORS['gray']};
            font-size: 16px;
            font-weight: 400;
            margin-top: -5px;
            letter-spacing: 0.5px;
        }}
        
        /* ========== MODERN SIDEBAR STYLING ========== */
        
        /* Sidebar container with smooth animations */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0D7C6C 0%, #149B7E 45%, #1DAAA0 100%);
            backdrop-filter: blur(15px);
            color: white;
            border-right: 4px solid #26C4B6;
            animation: slideInFromLeft 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: inset -2px 0 rgba(255,255,255,0.2), 0 12px 40px rgba(0, 0, 0, 0.25);
            position: relative;
            overflow: hidden;
        }}
        
        /* Sidebar smooth sliding animation on load */
        @keyframes slideInFromLeft {{
            from {{
                transform: translateX(-100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        /* Enhanced sidebar text styling */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: #D4F5F1 !important;
        }}
        
        [data-testid="stSidebar"] p {{
            color: #D4F5F1 !important;
        }}
        
        [data-testid="stSidebar"] h2 {{
            color: #E8F8F7 !important;
            font-weight: 800 !important;
        }}
        
        [data-testid="stSidebar"] h3 {{
            color: #D4F5F1 !important;
        }}
        
        [data-testid="stSidebar"] h4 {{
            color: #D4F5F1 !important;
        }}
        
        /* Sidebar divider enhancement */
        [data-testid="stSidebar"] hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
            margin: 15px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }}
        
        /* ========== NAVIGATION MENU STYLING ========== */
        
        /* Navigation icon styling */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] svg {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        /* Menu items container */
        [data-testid="stSidebar"] [role="region"] {{
            animation: fadeInUp 0.5s ease-out 0.2s backwards;
        }}
        
        /* Navigation menu items */
        [data-testid="stSidebar"] button {{
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 12px;
            margin: 8px 10px;
            padding: 14px 16px !important;
            position: relative;
            overflow: hidden;
            background: rgba(0, 0, 0, 0.15) !important;
            border: 2px solid rgba(212, 245, 241, 0.25) !important;
            color: #D4F5F1 !important;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.4px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        /* Menu item hover effect - Scale and Glow */
        [data-testid="stSidebar"] button:hover {{
            background: rgba(0, 0, 0, 0.25) !important;
            border: 2px solid #D4F5F1 !important;
            color: #E8F8F7 !important;
            transform: translateX(8px) scale(1.04);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3), 
                        inset 0 1px 3px rgba(212, 245, 241, 0.3);
        }}
        
        /* Menu item active state */
        [data-testid="stSidebar"] button[aria-selected="true"] {{
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.2)) !important;
            border: 2.5px solid #E8F8F7 !important;
            color: #E8F8F7 !important;
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4),
                        inset 0 1px 3px rgba(212, 245, 241, 0.4);
            transform: translateX(6px) scale(1.05);
            font-weight: 800;
            position: relative;
        }}
        
        /* Active menu item glow effect */
        [data-testid="stSidebar"] button[aria-selected="true"]::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(232, 248, 247, 0.3), transparent);
            animation: pulse-glow 2s ease-in-out infinite;
            border-radius: 12px;
            pointer-events: none;
        }}
        
        /* Glow pulse animation */
        @keyframes pulse-glow {{
            0%, 100% {{
                box-shadow: 0 0 20px rgba(46, 196, 182, 0.4);
            }}
            50% {{
                box-shadow: 0 0 40px rgba(46, 196, 182, 0.6);
            }}
        }}
        
        /* Icon color enhancement */
        [data-testid="stSidebar"] button svg {{
            color: #D4F5F1 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.3));
        }}
        
        [data-testid="stSidebar"] button:hover svg {{
            color: #E8F8F7 !important;
            transform: scale(1.25) rotate(5deg);
            filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.4));
        }}
        
        [data-testid="stSidebar"] button[aria-selected="true"] svg {{
            color: #E8F8F7 !important;
            filter: drop-shadow(0 0 10px rgba(212, 245, 241, 0.6));
            animation: iconBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        
        /* Icon bounce animation */
        @keyframes iconBounce {{
            0% {{ transform: scale(0.8) rotate(-10deg); }}
            50% {{ transform: scale(1.2) rotate(0deg); }}
            100% {{ transform: scale(1) rotate(0deg); }}
        }}
        
        /* Glassmorphism card styling */
        .glass-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin: 15px 0;
        }}
        
        .glass-card:hover {{
            background: rgba(255, 255, 255, 0.85);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(31, 38, 135, 0.3);
        }}
        
        /* Animated dashboard cards */
        .dashboard-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 25px;
            color: white;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transform: translateZ(0);
            width: 100%;
            min-height: 200px;
        }}
        
        .dashboard-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }}
        
        .dashboard-card:hover::before {{
            left: 100%;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-12px) scale(1.02);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .dashboard-card:active {{
            transform: translateY(-6px) scale(0.98);
        }}
        
        /* Card-specific gradients */
        .dengue-card {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        }}
        
        .asthma-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .pneumonia-card {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .lab-card {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}
        
        /* Make cards clickable */
        .dashboard-card {{
            cursor: pointer !important;
        }}
        
        .dashboard-card:hover {{
            opacity: 0.95 !important;
        }}
        
        /* Icon animation */
        .animated-icon {{
            display: inline-block;
            font-size: 48px;
            margin-bottom: 10px;
            animation: float 3s ease-in-out infinite;
        }}
        
        .animated-icon:hover {{
            animation: bounce 0.6s ease-in-out !important;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            25% {{ transform: translateY(-15px); }}
            50% {{ transform: translateY(0); }}
            75% {{ transform: translateY(-8px); }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in {{
            animation: fadeInUp 0.6s ease-out forwards;
        }}
        
        .fade-in-1 {{ animation-delay: 0.1s; }}
        .fade-in-2 {{ animation-delay: 0.2s; }}
        .fade-in-3 {{ animation-delay: 0.3s; }}
        .fade-in-4 {{ animation-delay: 0.4s; }}
        
        /* Modern button styling with ripple effect */
        .modern-button {{
            background: linear-gradient(135deg, {MEDICAL_COLORS['green']}, {MEDICAL_COLORS['dark_green']});
            color: {MEDICAL_COLORS['white']};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .modern-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.5);
        }}
        
        .modern-button:active {{
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }}
        
        /* Ripple effect */
        .ripple {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
            pointer-events: none;
        }}
        
        @keyframes ripple-animation {{
            to {{
                transform: scale(4);
                opacity: 0;
            }}
        }}
        
        /* Responsive grid */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        @media (max-width: 768px) {{
            .card-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
            
            h2 {{
                font-size: 1.5em;
            }}
        }}
        
        /* Enhanced input fields */
        input, select, textarea {{
            border: 2px solid rgba(76, 175, 80, 0.2) !important;
            border-radius: 10px;
            padding: 12px;
            font-size: 15px;
            background: rgba(255, 255, 255, 0.8) !important;
            transition: all 0.3s ease !important;
        }}
        
        input:focus, select:focus, textarea:focus {{
            border-color: {MEDICAL_COLORS['blue']} !important;
            box-shadow: 0 0 0 4px rgba(25, 118, 210, 0.1) !important;
            background: {MEDICAL_COLORS['white']} !important;
        }}
        
        /* Enhanced tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            border-radius: 12px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }}
        
        th {{
            background: linear-gradient(135deg, {MEDICAL_COLORS['dark_blue']}, {MEDICAL_COLORS['blue']});
            color: {MEDICAL_COLORS['white']};
            font-weight: 700;
            padding: 15px;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 12px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(76, 175, 80, 0.1);
            transition: all 0.2s ease;
        }}
        
        tr:hover td {{
            background-color: rgba(76, 175, 80, 0.05);
            transform: scale(1.01);
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-normal {{
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            color: {MEDICAL_COLORS['dark_green']};
        }}
        
        .status-abnormal {{
            background: linear-gradient(135deg, rgba(211, 47, 47, 0.2), rgba(211, 47, 47, 0.1));
            color: {MEDICAL_COLORS['error']};
        }}
        
        /* Progress indicator animation */
        .progress-ring {{
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }}
        
        .progress-ring-circle {{
            transition: stroke-dashoffset 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: 50% 50%;
        }}
        
        /* Divider styling */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.3), transparent);
            margin: 20px 0;
        }}
        
        /* Alert boxes with glassmorphism */
        .stAlert {{
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Initialize theme
apply_medical_theme()

# Custom component functions for medical UI with animations
def medical_card(title, content, icon="🏥", card_type="default"):
    """Create an animated medical-themed card with glassmorphism"""
    st.markdown(f"""
    <div class="glass-card fade-in" style='border-left: 5px solid {MEDICAL_COLORS["green"]};'>
        <div style='display: flex; align-items: flex-start; justify-content: space-between;'>
            <div style='flex: 1;'>
                <h3 style='color: {MEDICAL_COLORS["dark_blue"]}; margin: 0 0 10px 0; font-weight: 700;'>{icon} {title}</h3>
                <p style='color: {MEDICAL_COLORS["gray"]}; margin: 0; line-height: 1.6;'>{content}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def medical_header(title, subtitle="", icon="🏥"):
    """Create an animated medical header with advanced styling"""
    st.markdown(f"""
    <div style='margin-bottom: 30px; animation: fadeInUp 0.6s ease-out;'>
        <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 15px;'>
            <div class="animated-icon" style='font-size: 50px;'>{icon}</div>
            <div style='flex: 1;'>
                <h1 style='margin: 0; color: {MEDICAL_COLORS["dark_blue"]}; font-weight: 800; letter-spacing: -1px;'>{title}</h1>
                {f'<p class="subtitle" style="margin: 5px 0 0 0;">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        <div style='height: 3px; background: linear-gradient(90deg, {MEDICAL_COLORS["green"]}, {MEDICAL_COLORS["blue"]}, transparent); border-radius: 2px;'></div>
    </div>
    """, unsafe_allow_html=True)

def animated_dashboard_card(title, icon, gradient_class, description=""):
    """Create an animated, clickable dashboard card"""
    return f"""
    <div class='dashboard-card {gradient_class} fade-in' style='
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 200px;
        cursor: pointer;
        position: relative;
    '>
        <div class='animated-icon' style='color: white; font-size: 60px;'>{icon}</div>
        <h3 style='color: white; margin: 15px 0 8px 0; font-weight: 700;'>{title}</h3>
        <p style='color: rgba(255,255,255,0.9); font-size: 13px; margin: 0;'>{description}</p>
    </div>
    """

def risk_badge(risk_score):
    """Create an animated risk level badge with glassmorphism"""
    if risk_score >= 0.7:
        color = MEDICAL_COLORS['error']
        level = "HIGH RISK"
        bg_color = "rgba(211, 47, 47, 0.1)"
    elif risk_score >= 0.4:
        color = MEDICAL_COLORS['warning']
        level = "MEDIUM RISK"
        bg_color = "rgba(245, 127, 0, 0.1)"
    else:
        color = MEDICAL_COLORS['success']
        level = "LOW RISK"
        bg_color = "rgba(76, 175, 80, 0.1)"
    
    return f"""
    <div style='
        background: {bg_color};
        backdrop-filter: blur(10px);
        color: {color};
        padding: 12px 24px;
        border-radius: 25px;
        display: inline-block;
        font-weight: 700;
        font-size: 14px;
        border: 2px solid {color};
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        animation: float 3s ease-in-out infinite;
    '>
        {level}: {risk_score * 100:.1f}%
    </div>
    """

def show_risk(message, risk_score, title="Risk Assessment"):
    """Display risk score with medical styling and animations"""
    col1, col2 = st.columns([0.65, 0.35])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid {MEDICAL_COLORS["green"]};
            animation: fadeInUp 0.5s ease-out;
        '>
            <h4 style='color: {MEDICAL_COLORS["dark_blue"]}; margin: 0 0 10px 0;'>📊 {title}</h4>
            <p style='color: {MEDICAL_COLORS["gray"]}; font-size: 15px; margin: 0; line-height: 1.6;'>{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(risk_badge(risk_score), unsafe_allow_html=True)
    
    st.divider()

def create_info_grid(data_dict):
    """Create responsive animated info grid"""
    cols = st.columns(len(data_dict))
    for idx, (col, (key, value)) in enumerate(zip(cols, data_dict.items())):
        with col:
            st.markdown(f"""
            <div class='glass-card fade-in fade-in-{idx+1}' style='
                text-align: center;
                border-top: 3px solid {MEDICAL_COLORS["green"]};
                border-left: none;
            '>
                <p style='color: {MEDICAL_COLORS["gray"]}; font-size: 12px; margin: 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;'>{key}</p>
                <p style='color: {MEDICAL_COLORS["dark_blue"]}; font-size: 24px; font-weight: 700; margin: 8px 0 0 0;'>{value}</p>
            </div>
            """, unsafe_allow_html=True)

def load_model(path):
    """Load model from pickle file"""
    try:
        return joblib.load(path)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

def get_positive_risk(model, features, default_high=0.8, default_low=0.2, positive_pred=True):
    """Calculate risk probability from model"""
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

# PATH SETUP
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ===================== CHECK MODEL STATUS AT STARTUP =====================
@st.cache_resource
def check_model_status():
    try:
        from pneumonia_utils import MODEL_LOADED, MODEL_LOAD_ERROR
        dengue_ok = load_model(os.path.join(models_dir, "best_dengue_model.pkl")) is not None
        asthma_ok = load_model(os.path.join(models_dir, "asthma_rf_pipeline.pkl")) is not None
        pneumonia_status = "Loaded" if MODEL_LOADED else f"Using Fallback ({MODEL_LOAD_ERROR or 'Unknown'})"
        
        return {
            'dengue': "✅ Loaded" if dengue_ok else "⚠️ Failed",
            'asthma': "✅ Loaded" if asthma_ok else "⚠️ Failed", 
            'pneumonia': "✅ Loaded" if MODEL_LOADED else "⚠️ " + pneumonia_status
        }
    except Exception as e:
        return {
            'dengue': "⚠️ Error",
            'asthma': "⚠️ Error",
            'pneumonia': "⚠️ Error"
        }

model_status = check_model_status()

with st.sidebar:
    st.markdown(f"""
    <div style='
        margin-bottom: 25px;
        padding: 20px 15px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        border: 2px solid #66D4C6;
        backdrop-filter: blur(10px);
        animation: fadeInDown 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    '>
        <h2 style='
            color: #66D4C6;
            margin: 0 0 8px 0;
            text-align: center;
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 0.8px;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        '>🏥 Medical Portal</h2>
        <p style='
            color: #66D4C6;
            text-align: center;
            margin: 0;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        '>Disease Prediction System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Initialize session state for card navigation
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None
    
    selected = option_menu(
        "Navigation",
        [
            "Dashboard",
            "Dengue Prediction",
            "Asthma Prediction",
            "Pneumonia Detection",
            "About"
        ],
        icons=["house-heart", "bug", "wind", "lungs", "info-circle"],
        default_index=0,
        styles={
            "container": {
                "padding": "8px",
                "background-color": "transparent",
                "border-radius": "12px",
                "background-image": "linear-gradient(135deg, rgba(230, 245, 248, 0.9) 0%, rgba(200, 235, 240, 0.85) 50%, rgba(170, 225, 235, 0.8) 100%)",
                "box-shadow": "inset 0 0 20px rgba(255, 255, 255, 0.1)",
                "position": "relative"
            },
            "icon": {
                "color": "#4AD0BE",
                "font-size": "32px",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                "font-weight": "900",
            },
            "nav-link": {
                "color": "#66D4C6",
                "font-size": "19px",
                "font-weight": "700",
                "text-align": "left",
                "margin": "8px 0",
                "padding": "12px 16px",
                "border-radius": "12px",
                "background": "rgba(255, 255, 255, 0.35)",
                "border": "2px solid rgba(102, 212, 198, 0.5)",
                "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
                "--hover-color": "rgba(255, 255, 255, 0.45)",
                "--hover-text-color": "#4AD0BE",
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.5)",
                "color": "#4AD0BE",
                "font-weight": "900",
                "border": "2.5px solid #66D4C6",
                "padding": "12px 16px",
                "border-radius": "12px",
            }
        }
    )
    
    # Handle card navigation
    if st.session_state.selected_page is not None:
        selected = st.session_state.selected_page
        st.session_state.selected_page = None
    
    st.divider()
    st.markdown("""
    <div style='
        background: rgba(0, 0, 0, 0.2);
        border: 2px solid #D4F5F1;
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) 0.3s backwards;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    '>
        <p style='
            color: #D4F5F1;
            font-size: 12px;
            margin: 0;
            font-weight: 700;
            line-height: 1.6;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        '>
            <strong style="color: #E8F8F7;">⚠️ Disclaimer:</strong> This system is for screening purposes only. 
            Always consult with a healthcare professional for accurate diagnosis.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ================ HOME/DASHBOARD PAGE ================
if selected == "Dashboard":
    medical_header(
        "Medical Disease Prediction System",
        "AI-Powered Health Screening Platform",
        "🏥"
    )
    
    # Main features overview
    st.markdown("""
    <div style='margin-bottom: 30px;'>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern animated dashboard cards as direct buttons
    st.markdown(f"<h3 style='color: {MEDICAL_COLORS['dark_blue']};'>🏥 Disease Screening Services</h3>", unsafe_allow_html=True)
    
    # Add CSS for card button styling
    st.markdown("""
    <style>
    /* Premium Medical Disease Screening Cards */
    .card-button {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border: none;
        border-radius: 20px;
        padding: 35px 30px;
        height: 260px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12), 0 0 0 0 rgba(0, 0, 0, 0.08);
        animation: fadeInUp 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Professional Hover Effect - Medical Theme */
    .card-button:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2), 
                    0 0 40px rgba(132, 250, 176, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.6);
        filter: brightness(1.08);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Active State - Click Effect */
    .card-button:active {
        transform: translateY(-4px) scale(0.98);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
    }
    
    /* Focus State for Accessibility */
    .card-button:focus {
        outline: none;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2), 
                    0 0 40px rgba(132, 250, 176, 0.5);
    }
    
    /* Disabled State */
    .card-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Gradient Backgrounds for Each Disease */
    .card-button.dengue {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        position: relative;
    }
    
    .card-button.dengue:before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .card-button.dengue:hover:before {
        opacity: 1;
    }
    
    .card-button.asthma {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .card-button.asthma:hover {
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.3), 
                    0 0 40px rgba(118, 75, 162, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }
    
    .card-button.pneumonia {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .card-button.pneumonia:hover {
        box-shadow: 0 25px 50px rgba(250, 112, 154, 0.3), 
                    0 0 40px rgba(254, 225, 64, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }
    
    .card-button.lab {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    
    .card-button.lab:hover {
        box-shadow: 0 25px 50px rgba(168, 237, 234, 0.3), 
                    0 0 40px rgba(254, 214, 227, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }
    
    /* Card Icon Styling */
    .card-icon {
        font-size: 70px;
        margin-bottom: 12px;
        display: block;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
    }
    
    .card-button:hover .card-icon {
        animation: float 2s ease-in-out infinite;
        filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.2));
    }
    
    /* Card Title Styling */
    .card-title {
        color: white;
        font-weight: 800;
        font-size: 20px;
        margin: 8px 0 8px 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        letter-spacing: 0.5px;
    }
    
    /* Card Subtitle */
    .card-subtitle {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 12px;
        margin: 0;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        text-decoration: none !important;
    }
    
    /* Remove ALL underlines from card links */
    .card-button {
        text-decoration: none !important;
    }
    
    .card-button * {
        text-decoration: none !important;
    }
    
    .card-button:hover {
        text-decoration: none !important;
    }
    
    .card-button:hover * {
        text-decoration: none !important;
    }
    
    .card-button:focus {
        text-decoration: none !important;
    }
    
    .card-button:focus * {
        text-decoration: none !important;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .card-button {
            padding: 25px 20px;
            height: 220px;
        }
        
        .card-icon {
            font-size: 50px;
        }
        
        .card-title {
            font-size: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render clickable HTML dashboard cards using query parameters - medical card grid
    st.markdown("""<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; margin-top: 20px;">
<a href="?page=dengue" class="card-button dengue" title="Click to detect Dengue">
<span class="card-icon">🦟</span>
<div class="card-title">Dengue<br>Detection</div>
<div class="card-subtitle">CBC Analysis</div>
</a>
<a href="?page=asthma" class="card-button asthma" title="Click to screen Asthma">
<span class="card-icon">🫁</span>
<div class="card-title">Asthma<br>Screening</div>
<div class="card-subtitle">Respiratory Analysis</div>
</a>
<a href="?page=pneumonia" class="card-button pneumonia" title="Click to detect Pneumonia">
<span class="card-icon">🩻</span>
<div class="card-title">Pneumonia<br>Detection</div>
<div class="card-subtitle">X-ray Analysis</div>
</a>
<a href="?page=lab" class="card-button lab" title="Click to view Lab Reports">
<span class="card-icon">📊</span>
<div class="card-title">Lab<br>Reports</div>
<div class="card-subtitle">OCR Extraction</div>
</a>
</div>""", unsafe_allow_html=True)
    
    # Handle navigation from query parameters
    query = st.query_params
    
    if "page" in query:
        if query["page"] == "dengue":
            st.session_state.selected_page = "Dengue Prediction"
            st.rerun()
        elif query["page"] == "asthma":
            st.session_state.selected_page = "Asthma Prediction"
            st.rerun()
        elif query["page"] == "pneumonia":
            st.session_state.selected_page = "Pneumonia Detection"
            st.rerun()
        elif query["page"] == "lab":
            st.session_state.selected_page = "About"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System features
    st.markdown(f"<h3 style='color: {MEDICAL_COLORS['dark_blue']};'>🚀 Key Features & Benefits</h3>", unsafe_allow_html=True)
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']}; margin-bottom: 15px;'>✨ Advanced Technology</h4>", unsafe_allow_html=True)
        features = [
            "✅ AI-Powered Disease Prediction",
            "✅ OCR-Based Lab Report Analysis",
            "✅ CNN X-ray Classification",
            "✅ Medical Rule-Based Screening",
            "✅ Multi-Disease Detection"
        ]
        for idx, feature in enumerate(features):
            st.markdown(f"""
            <div class='glass-card fade-in fade-in-{idx+1}' style='
                border-left: 4px solid {MEDICAL_COLORS['green']};
                margin-bottom: 10px;
                padding: 12px 15px;
            '>
                <p style='color: {MEDICAL_COLORS['dark_green']}; margin: 0; font-weight: 500;'>{feature}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']}; margin-bottom: 15px;'>🔐 Security & Reliability</h4>", unsafe_allow_html=True)
        benefits = [
            "🔒 Privacy-Focused Analysis",
            "⚡ Real-Time Results",
            "📱 Mobile-Friendly",
            "🎯 High Accuracy Models",
            "🏥 Clinical Integration Ready"
        ]
        for idx, benefit in enumerate(benefits):
            st.markdown(f"""
            <div class='glass-card fade-in fade-in-{idx+1}' style='
                border-left: 4px solid {MEDICAL_COLORS['blue']};
                margin-bottom: 10px;
                padding: 12px 15px;
            '>
                <p style='color: {MEDICAL_COLORS['dark_blue']}; margin: 0; font-weight: 500;'>{benefit}</p>
            </div>
            """, unsafe_allow_html=True)


# ================ DENGUE PREDICTION PAGE ================
elif selected == "Dengue Prediction":
    medical_header(
        "Dengue Detection System",
        "Complete Blood Count (CBC) Analysis",
        "🦟"
    )
    
    st.markdown(f"""
    <div class='glass-card' style='
        border-left: 5px solid {MEDICAL_COLORS['green']};
        animation: fadeInUp 0.6s ease-out;
    '>
        <p style='color: {MEDICAL_COLORS['dark_green']}; margin: 0; font-weight: 700;'>
            <strong>ℹ️ About Dengue Detection:</strong>
        </p>
        <p style='color: {MEDICAL_COLORS['gray']}; margin: 10px 0 0 0; line-height: 1.6;'>
            This system analyzes Complete Blood Count (CBC) test results to assess dengue fever probability based on platelet count, WBC levels, and other hematological markers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Select Input Mode", ["📄 Upload PDF (OCR)", "✏️ Manual Input"], horizontal=True)

    # ---- PDF MODE ----
    if mode == "📄 Upload PDF (OCR)":
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>📤 Upload Your CBC Report</h4>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Click to upload PDF file", type=["pdf"], label_visibility="collapsed")

        if uploaded_file:
            # Clear previous results from session state to prevent stale data
            for key in list(st.session_state.keys()):
                if 'dengue' in key.lower():
                    del st.session_state[key]
            with st.spinner("🔄 Processing PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    pdf_path = tmp.name

                # Try to find Tesseract automatically, or use default path
                import shutil
                tesseract_path = shutil.which("tesseract")
                if tesseract_path:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                else:
                    # Try default Windows installation path
                    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                    if os.path.exists(default_path):
                        pytesseract.pytesseract.tesseract_cmd = default_path
                    else:
                        st.error("❌ Tesseract-OCR not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
                        st.stop()
                
                images = convert_from_path(pdf_path)
                text = "".join(pytesseract.image_to_string(img) for img in images)
            
            # Display extracted values in simple table format
            try:
                # Extract patient info
                patient_info = CBCReportFormatter.extract_patient_info(text)
                cbc_values = CBCReportFormatter.parse_cbc_report(text)
                
                # Display lab and patient info
                st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>🏥 Report Information</h4>", unsafe_allow_html=True)
                
                lab_info = {
                    "Laboratory": patient_info.get('Lab', 'N/A'),
                    "Branch": patient_info.get('Branch', 'N/A'),
                    "Contact": patient_info.get('Contact', 'N/A')
                }
                create_info_grid(lab_info)
                
                st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>👤 Patient Information</h4>", unsafe_allow_html=True)
                
                patient_cols = st.columns(5)
                patient_cols[0].metric("👤 Name", patient_info.get('Name', 'N/A'))
                patient_cols[1].metric("⚧ Gender", patient_info.get("Gender", "N/A"))
                patient_cols[2].metric("🎂 Age", patient_info.get("Age", "N/A"))
                patient_cols[3].metric("🔐 Sample ID", patient_info.get("Sample ID", "N/A"))
                patient_cols[4].metric("📅 Date", patient_info.get("Date", "N/A"))
                
                # Display CBC values with units and reference ranges
                st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>📊 CBC Test Results</h4>", unsafe_allow_html=True)
                cbc_with_ranges = CBCReportFormatter.get_cbc_report_with_ranges(text)
                
                # Debug: Show extracted text
                with st.expander("📄 View OCR Extracted Text"):
                    st.text_area("Raw OCR Text", text, height=300, disabled=True)
                
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
                    
                    # Create HTML table with medical styling
                    html = f'<table style="width:100%; border-collapse: collapse; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">'
                    html += f'<tr style="background-color: {MEDICAL_COLORS["dark_blue"]}; color: white; font-weight: bold; text-align: left; padding: 12px;">'
                    for col in df.columns:
                        html += f'<th style="padding: 12px; border: 1px solid {MEDICAL_COLORS["blue"]}; text-align: left;">{col}</th>'
                    html += '</tr>'
                    
                    # Add rows with conditional styling
                    for idx, row in df.iterrows():
                        status = row['Status']
                        if status == "Abnormal":
                            row_style = f'background-color: #FFCDD2; color: #B71C1C;'  # Light red with dark red text
                        else:
                            row_style = f'background-color: {MEDICAL_COLORS["light_green"]}; color: {MEDICAL_COLORS["dark_green"]};'  # Light green with dark green text
                        
                        html += f'<tr style="{row_style} border-bottom: 1px solid {MEDICAL_COLORS["light_gray"]};">'
                        for col in df.columns:
                            value = row[col]
                            # Format numeric values to 2 decimal places
                            if isinstance(value, float):
                                value = f"{value:.2f}"
                            html += f'<td style="padding: 10px; border: 1px solid {MEDICAL_COLORS["light_gray"]};">{value}</td>'
                        html += '</tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.warning("No values extracted from report")
                    
            except Exception as e:
                st.error(f"⚠️ Could not extract values: {str(e)}")

            st.divider()
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("🔍 Analyze Report", use_container_width=True):
                    with st.spinner("⏳ Analyzing..."):
                        message, risk = predict_dengue(text)
                        show_risk(message, risk, "Dengue Risk Assessment")

    # ---- MANUAL MODE ----
    else:
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>Manual CBC Input</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']};'>Enter your CBC values below:</p>", unsafe_allow_html=True)
            platelets = st.number_input(
                "🔴 Platelets (×10³ / µL)", 
                value=300.0, 
                min_value=1.0,
                help="Normal range: 150-400"
            )
        with col2:
            wbc = st.number_input(
                "⚪ WBC (×10³ / µL)", 
                value=7.0, 
                min_value=0.1,
                help="Normal range: 4.5-11.0"
            )

        if st.button("🔍 Predict Dengue Risk", use_container_width=True, key="dengue_manual"):
            platelets_val = platelets * 1000 if platelets < 10000 else platelets
            wbc_val = wbc * 1000 if wbc < 100 else wbc

            fake_text = f"Platelet Count : {platelets_val}\nWBC : {wbc_val}"
            message, risk = predict_dengue(fake_text)
            show_risk(message, risk, "Dengue Risk Assessment")


# ================ ASTHMA PREDICTION PAGE ================
elif selected == "Asthma Prediction":
    medical_header(
        "Asthma Screening & Assessment",
        "Respiratory Function Analysis",
        "🫁"
    )
    
    st.markdown(f"""
    <div class='glass-card' style='
        border-left: 5px solid {MEDICAL_COLORS['blue']};
        animation: fadeInUp 0.6s ease-out;
    '>
        <p style='color: {MEDICAL_COLORS['dark_blue']}; margin: 0; font-weight: 700;'>
            <strong>ℹ️ About Asthma Screening:</strong>
        </p>
        <p style='color: {MEDICAL_COLORS['gray']}; margin: 10px 0 0 0; line-height: 1.6;'>
            This system evaluates respiratory function and risk factors to assess asthma probability based on FEV1, Peak Flow, FeNO levels, and medical history.
        </p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Select Input Mode", ["📄 Upload PDF (OCR)", "✏️ Manual Input"], horizontal=True)

    if mode == "📄 Upload PDF (OCR)":
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>📤 Upload Asthma Report</h4>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Click to upload PDF file", type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            with st.spinner("🔄 Processing PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    pdf_path = tmp.name

                images = convert_from_path(pdf_path)
                text = "".join(pytesseract.image_to_string(img) for img in images)
            
            with st.expander("📄 View Extracted Text"):
                st.text_area("Raw OCR Text", text, height=250, disabled=True)

            if st.button("🔍 Assess Asthma Risk", use_container_width=True):
                with st.spinner("⏳ Analyzing..."):
                    result = predict_asthma_from_text(text)
                    
                    # Extract actual risk percentage from result string
                    risk_match = re.search(r'Risk:\s*([\d.]+)%', result)
                    if risk_match:
                        risk = float(risk_match.group(1)) / 100.0  # Convert percentage to decimal
                    else:
                        risk = 0.5  # Default if parsing fails
                    
                    show_risk(result, risk, "Asthma Risk Assessment")
                    
                    # Extract parameters from OCR text and display table
                    params = extract_asthma_parameters_from_text(text)
                    
                    st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']}; margin-top: 20px;'>📋 Detailed Assessment Results</h4>", unsafe_allow_html=True)
                    
                    # Get assessment data
                    assessment_df = get_asthma_assessment_data(
                        params['fev1'], params['peak_flow'], params['feno'], 
                        params['age'], params['sex'], params['family_history'],
                        params['allergies'], params['air_pollution'], 
                        params['smoking_status'], params['bmi'],
                        params['physical_activity'], params['er_visits'],
                        params['medication_adherence'], params['indoor_smoke'], 
                        params['pets_at_home']
                    )
                    
                    # Display table with better HTML
                    def get_table_html(df):
                        html = '<div style="margin-top: 15px; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"><table style="width: 100%; border-collapse: collapse; font-size: 14px;">'
                        
                        # Header
                        html += '<thead><tr style="background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%); color: white; font-weight: 700;">'
                        html += '<th style="padding: 12px 15px; text-align: left; border: 1px solid #ddd;">TEST</th>'
                        html += '<th style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">VALUE</th>'
                        html += '<th style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">UNIT</th>'
                        html += '<th style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">REFERENCE RANGE</th>'
                        html += '<th style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">STATUS</th>'
                        html += '</tr></thead><tbody>'
                        
                        # Body rows
                        for idx, row in df.iterrows():
                            status = row['Status']
                            if "Abnormal" in status:
                                row_color = "#FFEBEE"
                                status_color = "#D32F2F"
                            elif "Normal" in status:
                                row_color = "#E8F5E9"
                                status_color = "#388E3C"
                            else:
                                row_color = "#FFFFFF"
                                status_color = "#424242"
                            
                            html += f'<tr style="background-color: {row_color}; border-bottom: 1px solid #eeeeee;">'
                            html += f'<td style="padding: 12px 15px; text-align: left; border: 1px solid #ddd; font-weight: 500;">{row["Test"]}</td>'
                            html += f'<td style="padding: 12px 15px; text-align: center; border: 1px solid #ddd; font-weight: 600;">{row["Value"]}</td>'
                            html += f'<td style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">{row["Unit"]}</td>'
                            html += f'<td style="padding: 12px 15px; text-align: center; border: 1px solid #ddd;">{row["Reference Range"]}</td>'
                            html += f'<td style="padding: 12px 15px; text-align: center; border: 1px solid #ddd; font-weight: 600; color: {status_color};">{status}</td>'
                            html += '</tr>'
                        
                        html += '</tbody></table></div>'
                        return html
                    
                    st.markdown(get_table_html(assessment_df), unsafe_allow_html=True)

    elif mode == "✏️ Manual Input":
        st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>Pulmonary Function & Medical History</h4>", unsafe_allow_html=True)
        
        # Section 1: Pulmonary Function Tests
        st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']}; font-size: 14px; font-weight: 600; margin: 15px 0 10px 0;'>📊 Pulmonary Function Tests</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            fev1 = st.number_input("📊 FEV1 (L)", value=2.5, min_value=0.5, max_value=5.0, step=0.1, help="Forced Expiratory Volume in 1 second")
        with col2:
            peak_flow = st.number_input("📈 Peak Flow (L/min)", value=450.0, min_value=100.0, max_value=800.0, step=10.0)
        with col3:
            feno = st.number_input("🔬 FeNO (ppb)", value=20.0, min_value=5.0, max_value=100.0, step=1.0, help="Fractional Exhaled Nitric Oxide")

        # Section 2: Demographics
        st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']}; font-size: 14px; font-weight: 600; margin: 15px 0 10px 0;'>👤 Demographics</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.slider("Age (years)", 5, 80, 35, step=1)
        with col2:
            sex = st.selectbox("Gender", ["Male", "Female"])
        with col3:
            bmi = st.number_input("BMI (kg/m²)", value=24.0, min_value=12.0, max_value=50.0, step=0.1)

        # Section 3: Medical History
        st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']}; font-size: 14px; font-weight: 600; margin: 15px 0 10px 0;'>🏥 Medical History</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            family_history = st.checkbox("🧬 Family History of Asthma", value=False)
        with col2:
            er_visits = st.number_input("ER Visits (past year)", value=0, min_value=0, max_value=20, step=1)
        with col3:
            medication_adherence = st.slider("Medication Adherence %", 0, 100, 80, step=5, help="Percentage of prescribed medication taken") / 100.0

        # Section 4: Environmental & Lifestyle Factors
        st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']}; font-size: 14px; font-weight: 600; margin: 15px 0 10px 0;'>🌍 Environmental & Lifestyle Factors</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            allergies = st.selectbox(
                "🌿 Known Allergies",
                ["None", "Dust", "Pollen", "Pet Dander", "Mold", "Multiple"],
                help="Primary allergen exposure"
            )
        with col2:
            smoking_status = st.selectbox(
                "🚭 Smoking Status",
                ["Never", "Former", "Current"],
                help="Current or past smoking status"
            )
        with col3:
            air_pollution = st.selectbox(
                "🌫️ Air Pollution Level",
                ["Low", "Moderate", "High"],
                help="Environmental air quality"
            )

        # Section 5: Additional Risk Factors
        st.markdown(f"<p style='color: {MEDICAL_COLORS['gray']}; font-size: 14px; font-weight: 600; margin: 15px 0 10px 0;'>⚠️ Additional Risk Factors</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            physical_activity = st.selectbox(
                "🏃 Physical Activity Level",
                ["Low", "Moderate", "High"],
                help="Regular exercise frequency"
            )
        with col2:
            indoor_smoke = st.checkbox("🚬 Indoor Smoke Exposure", value=False, help="Exposed to secondhand smoke indoors")
        with col3:
            pets_at_home = st.checkbox("🐾 Pets at Home", value=False, help="Living with pets")

        # Prediction Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Assess Asthma Risk", use_container_width=True, key="asthma_manual"):
            with st.spinner("⏳ Analyzing your data..."):
                try:
                    result = predict_asthma_with_params(
                        float(fev1), 
                        float(peak_flow), 
                        float(feno), 
                        int(age), 
                        sex, 
                        family_history,
                        allergies,  # Now passing actual allergy type
                        air_pollution,  # Now passing actual air pollution level
                        smoking_status,  # Now passing actual smoking status
                        float(bmi), 
                        physical_activity,  # Now passing actual activity level
                        int(er_visits),  # Now passing actual ER visits count
                        float(medication_adherence),  # Now passing actual adherence
                        indoor_smoke,  # Now passing indoor smoke exposure
                        pets_at_home  # Now passing pets at home
                    )
                    
                    # Extract risk probability from result message
                    risk = 0.8 if "Detected" in result else (0.4 if "Risk: " in result else 0.2)
                    if "Risk: " in result:
                        try:
                            import re as regex
                            match = regex.search(r'Risk: ([\d.]+)%', result)
                            if match:
                                risk = float(match.group(1)) / 100.0
                        except:
                            pass
                    
                    # Display main result
                    show_risk(result, risk, "Asthma Risk Assessment")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please ensure all inputs are valid and try again.")


# ================ PNEUMONIA DETECTION PAGE ================
elif selected == "Pneumonia Detection":
    medical_header(
        "Pneumonia Detection System",
        "Chest X-ray Analysis using AI",
        "🩻"
    )
    
    # Add medical background image
    st.markdown("""
    <style>
    .pneumonia-bg {
        background: linear-gradient(135deg, rgba(255, 167, 38, 0.05) 0%, rgba(255, 112, 67, 0.05) 50%, rgba(244, 67, 54, 0.05) 100%),
                    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><defs><pattern id="medical" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse"><circle cx="100" cy="100" r="3" fill="%23FF7043" opacity="0.1"/><path d="M100,50 Q150,100 100,150 Q50,100 100,50" stroke="%23FF8A65" stroke-width="0.5" fill="none" opacity="0.08"/></pattern></defs><rect width="1200" height="600" fill="%23FFF8F5"/><rect width="1200" height="600" fill="url(%23medical)"/></svg>');
        background-attachment: fixed;
        position: relative;
    }
    </style>
    <div class='pneumonia-bg' style='padding: 20px; border-radius: 12px; margin-bottom: 20px; backdrop-filter: blur(5px);'>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='glass-card' style='
        border-left: 5px solid #FFA726;
        animation: fadeInUp 0.6s ease-out;
    '>
        <p style='color: #E65100; margin: 0; font-weight: 700;'>
            <strong>ℹ️ About Pneumonia Detection:</strong>
        </p>
        <p style='color: {MEDICAL_COLORS['gray']}; margin: 10px 0 0 0; line-height: 1.6;'>
            This system analyzes chest X-ray images using deep learning to detect pneumonia and classify its type (COVID-19, Bacterial, Viral).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>📤 Upload Chest X-ray Image</h4>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Click to upload X-ray image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>Original X-ray</h4>", unsafe_allow_html=True)
            st.image(image, width=350)

        if st.button("🔍 Detect Pneumonia", use_container_width=True, key="pneumonia_detect"):
            with st.spinner("⏳ Analyzing X-ray..."):
                result, confidence, pneumonia_type, annotated_image = predict_pneumonia(image)
            
            with col2:
                st.markdown(f"<h4 style='color: {MEDICAL_COLORS['dark_blue']};'>Analysis Results</h4>", unsafe_allow_html=True)
                
                # Display annotated image with pneumonia areas highlighted
                st.image(annotated_image, width=350, caption="Highlighted Analysis")
                
                # Display results
                st.divider()
                if confidence >= 0.48:
                    st.markdown(f"""
                    <div style='
                        background-color: #FFCDD2;
                        border-left: 4px solid {MEDICAL_COLORS['error']};
                        padding: 15px;
                        border-radius: 8px;
                    '>
                        <h4 style='color: {MEDICAL_COLORS['error']}; margin: 0;'>⚠️ PNEUMONIA DETECTED</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Confidence Level", f"{confidence*100:.1f}%")
                    
                    # Show pneumonia type
                    type_colors = {
                        "COVID-19": "🔴",
                        "Bacterial": "🟠", 
                        "Viral": "🟡",
                        "Unknown": "⚪"
                    }
                    
                    color = type_colors.get(pneumonia_type, "⚪")
                    st.markdown(f"""
                    <div style='
                        background-color: {MEDICAL_COLORS['light_gray']};
                        padding: 12px;
                        border-radius: 8px;
                        margin: 10px 0;
                    '>
                        <p style='color: {MEDICAL_COLORS['dark_gray']}; margin: 0;'><strong>Classification:</strong> {color} {pneumonia_type}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show description
                    type_descriptions = {
                        "COVID-19": "🔴 Ground-glass opacities, often bilateral with peripheral distribution",
                        "Bacterial": "🟠 Lobar consolidation with clear margins and air bronchograms",
                        "Viral": "🟡 Diffuse bilateral interstitial infiltrates with peribronchial thickening",
                        "Unknown": "⚪ Abnormal opacities detected but type classification uncertain"
                    }
                    st.info(f"📋 {type_descriptions.get(pneumonia_type, 'Abnormal patterns detected')}")
                else:
                    st.markdown(f"""
                    <div style='
                        background-color: {MEDICAL_COLORS['light_green']};
                        border-left: 4px solid {MEDICAL_COLORS['green']};
                        padding: 15px;
                        border-radius: 8px;
                    '>
                        <h4 style='color: {MEDICAL_COLORS['dark_green']}; margin: 0;'>✅ NO PNEUMONIA DETECTED</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Confidence Level", f"{(1-confidence)*100:.1f}%")
                    st.info("📋 Chest X-ray appears normal. No abnormal opacities detected.")


# ================ ABOUT PAGE ================
elif selected == "About":
    medical_header(
        "About This System",
        "Medical Disease Prediction Platform",
        "ℹ️"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='glass-card fade-in fade-in-1' style='
            border-top: 5px solid {MEDICAL_COLORS['green']};
            border-left: none;
        '>
            <h3 style='color: {MEDICAL_COLORS['dark_blue']}; margin-top: 0; margin-bottom: 15px;'>🎯 Mission</h3>
            <p style='color: {MEDICAL_COLORS['gray']}; line-height: 1.7;'>
                To provide accessible, accurate, and affordable AI-powered disease screening to support healthcare professionals and patients in early disease detection and management.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='glass-card fade-in fade-in-2' style='
            border-top: 5px solid {MEDICAL_COLORS['blue']};
            border-left: none;
        '>
            <h3 style='color: {MEDICAL_COLORS['dark_blue']}; margin-top: 0; margin-bottom: 15px;'>🏥 Technology</h3>
            <p style='color: {MEDICAL_COLORS['gray']}; line-height: 1.7;'>
                Powered by advanced machine learning models, OCR technology, and deep learning CNNs for comprehensive disease screening across multiple medical domains.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(f"<h3 style='color: {MEDICAL_COLORS['dark_blue']};'>📋 Supported Conditions</h3>", unsafe_allow_html=True)
    
    conditions = [
        ("🦟 Dengue Fever", "Early detection through CBC analysis"),
        ("🫁 Asthma", "Respiratory function assessment"),
        ("🩻 Pneumonia", "X-ray image classification")
    ]
    
    for idx, (condition, description) in enumerate(conditions):
        st.markdown(f"""
        <div class='glass-card fade-in fade-in-{(idx+1) % 4 + 1}' style='
            border-left: 5px solid {MEDICAL_COLORS['green']};
        '>
            <p style='color: {MEDICAL_COLORS['dark_blue']}; margin: 0; font-weight: 700; font-size: 16px;'>{condition}</p>
            <p style='color: {MEDICAL_COLORS['gray']}; margin: 8px 0 0 0; font-size: 14px; line-height: 1.5;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown(f"""
    <div class='glass-card' style='
        border-left: 5px solid {MEDICAL_COLORS['error']};
        animation: fadeInUp 0.8s ease-out;
    '>
        <p style='color: {MEDICAL_COLORS['dark_blue']}; margin: 0; font-weight: 700; font-size: 16px;'>
            ⚕️ Medical Disclaimer
        </p>
        <p style='color: {MEDICAL_COLORS['gray']}; margin: 10px 0 0 0; line-height: 1.7;'>
            This system is designed for screening purposes only and should not replace professional medical evaluation. Always consult with qualified healthcare professionals for accurate diagnosis and treatment recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)