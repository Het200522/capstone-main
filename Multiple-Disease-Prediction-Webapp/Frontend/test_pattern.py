import re

text_lower = """total r.b.c. count""".lower()

# Test the RBC pattern
patterns = [r"total\s+r\.?b\.?c|rbc\s+count|r\.?b\.?c(?:\s|$|:)|total.*rbc"]

for pattern in patterns:
    match = re.search(pattern, text_lower)
    print(f"Pattern '{pattern}': {match is not None}")
    if match:
        print(f"  Matched: '{match.group()}'")

# The issue: we need to match "total r.b.c. count" but pattern looks for "total r.b.c"
# Let's test better pattern
print("\nTesting improved patterns:")
better_patterns = [
    r"total.*?r\.?b\.?c",
    r"total.*rbc",
    r"r\.?b\.?c.*count"
]

for pattern in better_patterns:
    match = re.search(pattern, text_lower)
    print(f"Pattern '{pattern}': {match is not None}")
    if match:
        print(f"  Matched: '{match.group()}'")
