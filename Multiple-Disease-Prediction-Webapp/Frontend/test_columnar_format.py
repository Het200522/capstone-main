"""
Test the columnar format extraction with the user's provided report
"""
import sys
sys.path.insert(0, '.')

from lab_report_formatter import CBCReportFormatter

# User's provided report text (columnar format)
columnar_report = """
METRO PATHOLOGY

Automated Laboratory Services

Name: Ananya Miller
Gender: Female Age: 34
Sample ID: 724631

COMPLETE BLOOD COUNT

Test

Hemoglobin

Total R.B.C. Count

Haematocrit (PCV/HCT)

Mean Corpuscular Volume (M.C.V.)
Mean Corpuscular Hb (M.C.H.)
Total W.B.C. Count

DIFFERENTIAL COUNT:
Neutrophils

Lymphocytes

Eosinophils

Monocytes

Basophils

PLATELETS:
Platelet Count
MPV

ABSOLUTE COUNTS:
Neutrophils (abs)
Lymphocytes (abs)
Eosinophils (abs)
Monocytes (abs)
Basophils (abs)

Atul S. Vadhavkar
B.Sc (Micro), DMLT

Result
11.1
4.05
48.9
84.0
28.0
3100

38.0
48.0
3.0
5.0
0.5

65000
13.2

1600
2600
180
300
40

Unit

g/dl
millions/cumm
%

fl

Pg
ful

%
%
%
%
%

ful
fL

ful
ful
ful
ful

ful

End of Report

Branch: South Donald

Contact: +91 9791524861
Report Release: 15-11-2025 13:36:11

Biological Ref. Range
10.0-17.0 g/dl

4.4-5.5

40-50 %

83-95 fl

27-32 pg

4000-10000 /uL

40-70 %
20-40 %
1-6 %
2-10 %
0-1 %

150-450 /uL
6.78-13.46 fL

1575-8800 /uL
1125-4950 /uL
0-400 /uL
0-1000 /uL
0-100 /uL

& Date: 18-02-2025
"""

# Test the extraction
print("=" * 60)
print("TESTING COLUMNAR FORMAT EXTRACTION")
print("=" * 60)

result = CBCReportFormatter.get_cbc_report_with_ranges(columnar_report)

print("\nExtracted Values:")
print("-" * 60)
extracted_count = 0
for test_name, test_data in result.items():
    if isinstance(test_data, dict) and "Value" in test_data:
        print(f"{test_name}: {test_data['Value']}")
        extracted_count += 1

print(f"\n✅ Total Extracted: {extracted_count}/18 fields")
print("=" * 60)

# Expected values for verification
expected = {
    "Hemoglobin": 11.1,
    "Total R.B.C. Count": 4.05,
    "Haematocrit (PCV/HCT)": 48.9,
    "Mean Corpuscular Volume (M.C.V.)": 84.0,
    "Mean Corpuscular Hb (M.C.H.)": 28.0,
    "Total W.B.C. Count": 3100,
    "Neutrophils": 38.0,
    "Lymphocytes": 48.0,
    "Eosinophils": 3.0,
    "Monocytes": 5.0,
    "Basophils": 0.5,
    "Platelet Count": 65000,
    "MPV": 13.2,
    "Neutrophils (abs)": 1600,
    "Lymphocytes (abs)": 2600,
    "Eosinophils (abs)": 180,
    "Monocytes (abs)": 300,
    "Basophils (abs)": 40,
}

print("\nVerification Against Expected Values:")
print("-" * 60)
correct = 0
for test_name, expected_val in expected.items():
    if test_name in result and isinstance(result[test_name], dict):
        actual_val = result[test_name].get("Value")
        
        if actual_val is not None:
            match = "✅" if abs(actual_val - expected_val) < 1 else "❌"  # Allow 1 unit tolerance
            print(f"{match} {test_name}: Expected {expected_val}, Got {actual_val}")
            if abs(actual_val - expected_val) < 1:
                correct += 1
        else:
            print(f"❌ {test_name}: NOT EXTRACTED (expected {expected_val})")
    else:
        print(f"❌ {test_name}: NOT EXTRACTED (expected {expected_val})")

print(f"\n✅ ACCURACY: {correct}/18 fields extracted correctly")
print("=" * 60)
