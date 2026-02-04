import sys
sys.path.insert(0, '.')

from lab_report_formatter import CBCReportFormatter
import re

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

text_lower = columnar_report.lower().replace(",", "").replace("(abs)", " abs").replace("(absolute)", " abs")
lines = text_lower.split("\n")

# Debug columnar extraction
result_line_idx = -1
for idx, line in enumerate(lines):
    if re.search(r"\b(result|value|values)\b", line, re.IGNORECASE):
        result_line_idx = idx
        print(f"Result header found at line {idx}: '{line}'")
        break

unit_line_idx = -1
for idx in range(result_line_idx + 1, len(lines)):
    line = lines[idx]
    if re.search(r"^\s*(unit|range|reference|biological)\s*$", line, re.IGNORECASE):
        unit_line_idx = idx
        print(f"Unit header found at line {idx}: '{line}'")
        break

if unit_line_idx == -1:
    unit_line_idx = len(lines)

print(f"\nExtracting numbers from lines {result_line_idx+1} to {unit_line_idx}:")
print("-" * 80)

result_numbers = []
for idx in range(result_line_idx + 1, unit_line_idx):
    line = lines[idx]
    
    if not line.strip():
        print(f"Line {idx}: EMPTY")
        continue
    
    print(f"Line {idx}: '{line}'")
    
    for match in re.finditer(r"(\d+\.?\d*|\d*\.\d+)", line):
        val = float(match.group(1))
        if val > 0:
            print(f"  Found: {val}")
            result_numbers.append(val)

print(f"\n\nAll extracted numbers ({len(result_numbers)} total):")
print(result_numbers)
print(f"\nExpected Platelet Count at index 11: {result_numbers[11] if len(result_numbers) > 11 else 'NOT FOUND'}")
