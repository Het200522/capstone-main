"""
Stress test - testing with edge cases and difficult report formats
"""

from lab_report_formatter import CBCReportFormatter

# Test case 1: Report with missing some fields
test_1_partial = """
Name: Test Patient
Age: 30

CBC RESULTS:
Hemoglobin 12.5
RBC 4.6
PCV 42.0
Total WBC 7000
Neutrophils 55%
Lymphocytes 38%
Eosinophils 4%
Monocytes 2%
Basophils 1%
Platelet 240000
MPV 8.9
"""

# Test case 2: Report with scattered layout
test_2_scattered = """
PATIENT DETAILS
Name: John Doe
Age: 50

HEMATOLOGY PANEL

Hemoglobin      14.2 g/dl
Total RBC       4.8 millions/cumm
Hematocrit      45.1 %
MCV             86.5 fl
MCH             28.8 Pg

WBC Analysis:
  Total WBC Count        8900 /uL
  Neutrophils            58 %
  Lymphocytes            32 %
  Eosinophils            6 %
  Monocytes              3 %
  Basophils              1 %

Platelet Panel:
  Count: 265 x 10^9/L (convert to 265000)
  MPV: 9.1 fL
  
Absolute values:
  Neutrophils abs: 5162
  Lymphocytes abs: 2848
  Eosinophils abs: 534
  Monocytes abs: 267
  Basophils abs: 89
"""

# Test case 3: Extreme minimal format
test_3_minimal = """
HB 13.0
RBC 4.7
PCV 43
MCV 87
MCH 29
WBC 6500
Neut% 50
Lymph% 40
Eos% 6
Mono% 3
Baso% 1
PLT 250000
MPV 9.0
Neut(abs) 3250
Lymph(abs) 2600
Eos(abs) 390
Mono(abs) 195
Baso(abs) 65
"""

# Test case 4: Medical jargon heavy
test_4_medical = """
COMPLETE HEMATOLOGY PROFILE

Patient: Dr. Sample
Specimen Type: Venous Blood
Collection Method: EDTA Tube

PRIMARY PARAMETERS:
Hemoglobin Level: 14.8 g/dl (HIGH-NORMAL)
Erythrocyte Count (RBC): 4.85 millions/cumm (NORMAL)
Hematocrit (HCT) or Packed Cell Volume (PCV): 44.2 % (NORMAL)
Erythrocyte Indices:
    Mean Corpuscular Volume (MCV): 89 fl (NORMAL)
    Mean Corpuscular Hemoglobin (MCH): 30.5 Pg (NORMAL)

LEUKOCYTE ANALYSIS:
Total Leukocyte Count (WBC): 7800 /uL (NORMAL)

Differential Leukocyte Count (Percentage):
    Neutrophils (PMN): 54 % (NORMAL)
    Lymphocytes (Lymphs): 36 % (NORMAL)
    Eosinophils (Eos): 7 % (HIGH)
    Monocytes (Monos): 2 % (LOW)
    Basophils (Basos): 1 % (NORMAL)

THROMBOCYTE ASSESSMENT:
Platelet Count: 280000 /uL (NORMAL)
Mean Platelet Volume (MPV): 8.3 fL (NORMAL)

ABSOLUTE LEUKOCYTE COUNTS:
Neutrophil (absolute): 4212 /uL (NORMAL)
Lymphocyte (absolute): 2808 /uL (NORMAL)
Eosinophil (absolute): 546 /uL (HIGH)
Monocyte (absolute): 156 /uL (LOW)
Basophil (absolute): 78 /uL (NORMAL)
"""

test_cases = {
    "Test 1: Partial Report": test_1_partial,
    "Test 2: Scattered Layout": test_2_scattered,
    "Test 3: Minimal Format": test_3_minimal,
    "Test 4: Medical Heavy": test_4_medical,
}

def run_stress_tests():
    formatter = CBCReportFormatter()
    
    print("=" * 100)
    print("STRESS TEST - EDGE CASES AND DIFFICULT FORMATS")
    print("=" * 100)
    
    all_passed = True
    
    for test_name, report_text in test_cases.items():
        print(f"\n{test_name}")
        print("-" * 100)
        
        try:
            # Extract values
            cbc_values = formatter.parse_cbc_report(report_text)
            patient_info = formatter.extract_patient_info(report_text)
            abnormal = formatter.extract_abnormal_values(cbc_values)
            
            # Count extracted fields
            extracted_count = sum(1 for v in cbc_values.values() if v is not None)
            
            # Determine critical fields present
            critical_fields = [
                "Hemoglobin", "Total W.B.C. Count", "Platelet Count",
                "Neutrophils", "Lymphocytes"
            ]
            
            critical_present = sum(1 for f in critical_fields if cbc_values.get(f) is not None)
            
            # Status
            if extracted_count >= 12:
                status = "PASS"
            elif extracted_count >= 8:
                status = "WARN"
            else:
                status = "FAIL"
                all_passed = False
            
            print(f"  Patient: {patient_info.get('Name', 'N/A')}, Age: {patient_info.get('Age', 'N/A')}")
            print(f"  Extracted: {extracted_count}/18 fields | Critical: {critical_present}/5")
            print(f"  Abnormal values: {len(abnormal)}")
            print(f"  Status: [{status}]")
            
            # Show extracted values
            if extracted_count > 0:
                print(f"\n  Extracted fields:")
                for test_name, value in cbc_values.items():
                    if value is not None:
                        ref_info = formatter.REFERENCE_RANGES[test_name]
                        is_abnormal = formatter.is_abnormal(value, ref_info["min"], ref_info["max"])
                        indicator = "!" if is_abnormal else " "
                        print(f"    {indicator} {test_name}: {value:.1f}")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 100)
    if all_passed:
        print("STRESS TEST RESULT: ALL TESTS PASSED ✓")
    else:
        print("STRESS TEST RESULT: SOME TESTS FAILED")
    print("=" * 100)
    
    return all_passed

if __name__ == "__main__":
    success = run_stress_tests()
    exit(0 if success else 1)
