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

# Find all numbers with positions
all_numbers = []
for line_num, line in enumerate(lines):
    for match in re.finditer(r"(\d+\.?\d*|\d*\.\d+)", line):
        try:
            val = float(match.group(1))
            if val > 0:
                all_numbers.append({
                    "idx": len(all_numbers),
                    "line_num": line_num,
                    "value": val,
                    "line_text": line
                })
        except ValueError:
            continue

# Find "Platelet Count" line
platelet_line = -1
for idx, line in enumerate(lines):
    if "platelet count" in line:
        platelet_line = idx
        break

print(f"Platelet Count found at line {platelet_line}: '{lines[platelet_line]}'")
print(f"\nAll numbers and their positions:")
print("-" * 80)
for num_obj in all_numbers:
    print(f"Line {num_obj['line_num']:2d}: {num_obj['value']:10.1f} | {num_obj['line_text'][:60]}")

print(f"\n\nLooking for numbers near Platelet Count (line {platelet_line}):")
print("-" * 80)
for num_obj in all_numbers:
    dist = abs(num_obj['line_num'] - platelet_line)
    if dist <= 15:
        print(f"Line {num_obj['line_num']:2d}: {num_obj['value']:10.1f} | Distance: {dist:2d} | {num_obj['line_text'][:60]}")

print(f"\nExpected value for Platelet Count: 65000")
print(f"Check: Is 65000 > 450? {65000 > 450}")
print(f"Check: Is 13.2 > 450? {13.2 > 450}")
