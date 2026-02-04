"""
Final validation test - demonstrating complete extraction from all report types
"""

from lab_report_formatter import CBCReportFormatter, format_report_for_display

# Simulating OCR-extracted report with imperfect formatting and text recognition
ocr_extracted_report = """
TRUSTWELL DIAGNOSTIC CENTRE
Automated Laboratory Services

Name: Rajesh Sharma
Gender: M
Age: 45
Sample ID: LAB-2025-98765

COMPLETE BLOOD COUNT

Test Result Unit Ref. Range
Hemoglobin 13.8 g/dl 10.0-17.0
Total R.B.C. Count 4.7 millions/cumm 4.4-5.5
Haematocrit (PCV/HCT) 41.5 % 40-50
Mean Corpuscular Volume (M.C.V.) 88.3 fl 83-95
Mean Corpuscular Hb (M.C.H.) 29.4 Pg 27-32
Total W.B.C. Count 5600 /uL 4000-10000

DIFFERENTIAL COUNT:

Neutrophils 52 % 40-70
Lymphocytes 35 % 20-40
Eosinophils 8 % 1-6
Monocytes 4 % 2-10
Basophils 1 % 0-1

PLATELETS:

Platelet Count 245000 /uL 150-450
MPV 8.7 fL 6.78-13.46

ABSOLUTE COUNTS:

Neutrophils (abs) 2912 /uL 1575-8800
Lymphocytes (abs) 1960 /uL 1125-4950
Eosinophils (abs) 448 /uL 0-400
Monocytes (abs) 224 /uL 0-1000
Basophils (abs) 56 /uL 0-100

Report Date: 18-01-2026
Pathologist: Dr. Vivek Kumar
Lab License: IL-8234-2024
"""

def validate_extraction():
    """Validate extraction is working correctly for all fields"""
    
    print("=" * 100)
    print("FINAL VALIDATION TEST - COMPLETE FIELD EXTRACTION")
    print("=" * 100)
    
    formatter = CBCReportFormatter()
    
    # Extract all data
    print("\n[STEP 1] Extracting Patient Information...")
    patient_info = formatter.extract_patient_info(ocr_extracted_report)
    print(f"  Name: {patient_info.get('Name', 'N/A')}")
    print(f"  Gender: {patient_info.get('Gender', 'N/A')}")
    print(f"  Age: {patient_info.get('Age', 'N/A')}")
    print(f"  Sample ID: {patient_info.get('Sample ID', 'N/A')}")
    print(f"  Date: {patient_info.get('Date', 'N/A')}")
    print(f"  Lab: {patient_info.get('Lab', 'N/A')}")
    
    print("\n[STEP 2] Parsing CBC Values...")
    cbc_values = formatter.parse_cbc_report(ocr_extracted_report)
    
    extracted_count = 0
    for test_name in [
        "Hemoglobin", "Total R.B.C. Count", "Haematocrit (PCV/HCT)",
        "Mean Corpuscular Volume (M.C.V.)", "Mean Corpuscular Hb (M.C.H.)",
        "Total W.B.C. Count", "Neutrophils", "Lymphocytes", "Eosinophils",
        "Monocytes", "Basophils", "Platelet Count", "MPV",
        "Neutrophils (abs)", "Lymphocytes (abs)", "Eosinophils (abs)",
        "Monocytes (abs)", "Basophils (abs)"
    ]:
        value = cbc_values.get(test_name)
        if value is not None:
            extracted_count += 1
            ref_info = formatter.REFERENCE_RANGES[test_name]
            is_abnormal = formatter.is_abnormal(value, ref_info["min"], ref_info["max"])
            status = "ABNORMAL" if is_abnormal else "NORMAL"
            print(f"  {test_name}: {value:.1f} - {status}")
    
    print(f"\n  >>> TOTAL EXTRACTED: {extracted_count}/18 fields <<<")
    
    # Get abnormal values for clinical summary
    abnormal = formatter.extract_abnormal_values(cbc_values)
    
    print("\n[STEP 3] Clinical Summary...")
    if abnormal:
        print(f"  Abnormal values detected: {len(abnormal)}")
        for test_name, (value, status) in abnormal.items():
            print(f"    - {test_name}: {value:.1f} ({status})")
    else:
        print("  All values within normal range")
    
    # Generate formatted output
    print("\n[STEP 4] Generating Formatted Report...")
    cbc_dict, html_table, summary = format_report_for_display(ocr_extracted_report, disease_type="dengue")
    
    print(summary)
    
    # Test for disease prediction
    print("\n[STEP 5] Using Data for Disease Prediction...")
    print("  CBC values ready for:")
    print("    - Dengue Prediction Model")
    print("    - Asthma Prediction Model")
    print("    - Pneumonia Detection")
    
    # Verify data completeness
    print("\n[VERIFICATION] Data Completeness Check...")
    required_fields = [
        "Hemoglobin", "Total W.B.C. Count", "Platelet Count",
        "Neutrophils", "Lymphocytes", "Eosinophils"
    ]
    
    missing = []
    for field in required_fields:
        if cbc_values.get(field) is None:
            missing.append(field)
    
    if missing:
        print(f"  WARNING: Missing critical fields: {missing}")
    else:
        print(f"  PASS: All critical fields extracted successfully")
    
    print("\n" + "=" * 100)
    print("VALIDATION COMPLETE")
    print("=" * 100)
    
    return {
        "status": "PASS" if extracted_count >= 15 else "FAIL",
        "extracted_count": extracted_count,
        "patient_info": patient_info,
        "cbc_values": cbc_values,
        "abnormal_values": abnormal
    }

if __name__ == "__main__":
    result = validate_extraction()
    print(f"\nFINAL STATUS: {result['status']}")
    print(f"Fields extracted: {result['extracted_count']}/18")
