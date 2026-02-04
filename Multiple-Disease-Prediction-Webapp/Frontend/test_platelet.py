import re

report_text = """
PLATELETS:
Platelet Count
MPV

ABSOLUTE COUNTS:
Neutrophils (abs)
Lymphocytes (abs)
Eosinophils (abs)
Monocytes (abs)
Basophils (abs)

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
"""

text_lower = report_text.lower()
lines = text_lower.split("\n")

print("Looking for 'platelet count' pattern:")
platelet_pattern = r"platelet\s+count|platelet(?!\s*(?:abs|\())"

for idx, line in enumerate(lines):
    if "platelet" in line:
        print(f"Line {idx}: '{line}'")
        match = re.search(platelet_pattern, line, re.IGNORECASE)
        print(f"  Pattern match: {match is not None}")
        if match:
            print(f"  Matched: '{match.group()}'")

print("\n\nLooking for numbers after 'Platelet Count' line:")
platelet_line = -1
for idx, line in enumerate(lines):
    if re.search(r"platelet\s+count", line, re.IGNORECASE):
        platelet_line = idx
        break

if platelet_line >= 0:
    print(f"Found 'Platelet Count' at line {platelet_line}")
    print(f"Next 5 lines:")
    for i in range(platelet_line, min(platelet_line + 6, len(lines))):
        print(f"  Line {i}: '{lines[i]}'")
