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

text_lower = columnar_report.lower().replace(",", "").replace("(abs)", " abs").replace("(absolute)", " abs")
lines = text_lower.split("\n")

print("Testing _try_columnar_extraction directly:")
col_result = CBCReportFormatter._try_columnar_extraction(text_lower, lines)
print(f"Result: {len(col_result)} values")
for test, val in col_result.items():
    print(f"  {test}: {val}")

print(f"\n\nPlatelet Count in result: {'Platelet Count' in col_result}")
if 'Platelet Count' in col_result:
    print(f"Platelet Count value: {col_result['Platelet Count']}")
