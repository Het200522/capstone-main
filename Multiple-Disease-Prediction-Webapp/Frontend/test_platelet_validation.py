import sys
sys.path.insert(0, '.')

from lab_report_formatter import CBCReportFormatter

# Check platelet count validation
test_name = "Platelet Count"
value = 65000

print(f"Testing validation for {test_name}: {value}")
print(f"Reference ranges: {CBCReportFormatter.REFERENCE_RANGES[test_name]}")

is_valid = CBCReportFormatter._validate_value(test_name, value)
print(f"Is valid: {is_valid}")

# Check the margin calculation
ref_info = CBCReportFormatter.REFERENCE_RANGES[test_name]
min_val = ref_info["min"]
max_val = ref_info["max"]

print(f"\nMin: {min_val}, Max: {max_val}")

# For absolute counts
if "abs" in test_name.lower() or "/ul" in ref_info["unit"].lower():
    lower_bound = min_val * 0.25
    upper_bound = max_val * 3.0
    print(f"Absolute count bounds: {lower_bound} - {upper_bound}")
    print(f"Is {value} in bounds? {lower_bound <= value <= upper_bound}")
