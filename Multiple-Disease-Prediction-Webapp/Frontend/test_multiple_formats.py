"""
Test script with multiple report formats to ensure robust extraction
"""

from lab_report_formatter import CBCReportFormatter, format_report_for_display

# Test multiple report formats
test_reports = {
    "Format 1: Standard Columnar": """
METRO DIAGNOSTIC CENTRE
Patient: Rajesh Kumar
Gender: Male
Age: 35
Sample ID: 12345

COMPLETE BLOOD COUNT

Parameter               Value       Unit        Reference Range
Hemoglobin              14.2        g/dl        10.0-17.0
Total R.B.C. Count      4.8         millions    4.4-5.5
Haematocrit             45.0        %           40-50
Mean Corpuscular Vol    89.0        fl          83-95
Mean Corpuscular Hb     29.5        Pg          27-32
Total W.B.C. Count      7500        /uL         4000-10000
Neutrophils             55          %           40-70
Lymphocytes             35          %           20-40
Eosinophils             5           %           1-6
Monocytes               3           %           2-10
Basophils               2           %           0-1
Platelet Count          250000      /uL         150-450
MPV                     8.5         fL          6.78-13.46

ABSOLUTE COUNTS
Neutrophils (abs)       4125        /uL         1575-8800
Lymphocytes (abs)       2625        /uL         1125-4950
Eosinophils (abs)       375         /uL         0-400
Monocytes (abs)         225         /uL         0-1000
Basophils (abs)         150         /uL         0-100
""",
    
    "Format 2: Minimal Layout": """
Name: Priya Singh
Age: 28
Sample: XYZ789

CBC RESULTS:
HB 13.5
RBC 4.6
PCV 44
MCV 85
MCH 28.5
WBC 6800
Neut% 45
Lymph% 40
Eos% 8
Mono% 5
Baso% 2
PLT 220000
MPV 9.2
Neut(abs) 3060
Lymph(abs) 2720
Eos(abs) 544
Mono(abs) 340
Baso(abs) 136
""",
    
    "Format 3: Dense Text": """
DIAGNOSTIC REPORT
Patient: Amit Patel, Male, 42 years, ID: A5678

HEMATOLOGY PARAMETERS
Hemoglobin: 15.1 g/dl (Ref: 10.0-17.0)
Total RBC: 4.9 millions (Ref: 4.4-5.5)
PCV/Hematocrit: 46.2 % (Ref: 40-50)
MCV: 88 fl (Ref: 83-95)
MCH: 30.2 Pg (Ref: 27-32)
WBC: 8200 /uL (Ref: 4000-10000)

DIFFERENTIAL:
Neutrophils: 60 % (Range: 40-70)
Lymphocytes: 25 % (Range: 20-40)
Eosinophils: 2 % (Range: 1-6)
Monocytes: 8 % (Range: 2-10)
Basophils: 5 % (Range: 0-1)

PLATELET & INDEX:
Platelet Count: 280 x10^9/L (or 280000 /uL)
MPV: 7.9 fL

ABSOLUTE COUNTS:
Neutrophils absolute: 4920 /uL (1575-8800)
Lymphocytes absolute: 2050 /uL (1125-4950)
Eosinophils absolute: 164 /uL (0-400)
Monocytes absolute: 656 /uL (0-1000)
Basophils absolute: 410 /uL (0-100)
"""
}

def run_comprehensive_tests():
    print("=" * 100)
    print("COMPREHENSIVE LAB REPORT EXTRACTION TEST")
    print("=" * 100)
    
    formatter = CBCReportFormatter()
    
    for format_name, report_text in test_reports.items():
        print(f"\n\n{'='*100}")
        print(f"Testing: {format_name}")
        print(f"{'='*100}\n")
        
        # Extract values
        patient_info = formatter.extract_patient_info(report_text)
        cbc_values = formatter.parse_cbc_report(report_text)
        
        # Print patient info
        print(f"Patient: {patient_info.get('Name', 'N/A')}, "
              f"Age: {patient_info.get('Age', 'N/A')}, "
              f"ID: {patient_info.get('Sample ID', 'N/A')}")
        
        # Count extracted fields
        extracted_count = sum(1 for v in cbc_values.values() if v is not None)
        print(f"\nExtracted: {extracted_count}/18 fields\n")
        
        # Print all values
        print(f"{'Test Name':<35} {'Value':<12} {'Unit':<15} {'Status':<15}")
        print("-" * 80)
        
        for test_name in [
            "Hemoglobin", "Total R.B.C. Count", "Haematocrit (PCV/HCT)",
            "Mean Corpuscular Volume (M.C.V.)", "Mean Corpuscular Hb (M.C.H.)",
            "Total W.B.C. Count", "Neutrophils", "Lymphocytes", "Eosinophils",
            "Monocytes", "Basophils", "Platelet Count", "MPV",
            "Neutrophils (abs)", "Lymphocytes (abs)", "Eosinophils (abs)",
            "Monocytes (abs)", "Basophils (abs)"
        ]:
            value = cbc_values.get(test_name)
            ref_info = formatter.REFERENCE_RANGES[test_name]
            
            if value is not None:
                is_abnormal = formatter.is_abnormal(value, ref_info["min"], ref_info["max"])
                status = "ABNORMAL" if is_abnormal else "NORMAL"
                print(f"{test_name:<35} {value:<12.1f} {ref_info['unit']:<15} {status:<15}")
            else:
                print(f"{test_name:<35} {'NOT DETECTED':<12} {ref_info['unit']:<15} {'MISSING':<15}")
        
        # Summary
        abnormal = formatter.extract_abnormal_values(cbc_values)
        if abnormal:
            print(f"\n>> Abnormal values: {len(abnormal)}")
            for test_name, (value, status) in abnormal.items():
                print(f"   - {test_name}: {value:.1f} ({status})")
        else:
            print(f"\n>> All values within normal range")
    
    print("\n\n" + "=" * 100)
    print("✓ COMPREHENSIVE TESTS COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    run_comprehensive_tests()
