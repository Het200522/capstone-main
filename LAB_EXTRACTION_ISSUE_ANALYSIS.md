# Lab Report Field Extraction Issue - Root Cause Analysis

## Problem Summary
Some reports extract only a few fields instead of all 18 expected CBC test parameters. This causes incomplete test results in the formatted output.

## Root Causes Identified

### 1. **Flawed Number Extraction Logic in `_aggressive_extraction()` (Lines 450-520)**

**Problem:**
```python
# Only takes FIRST number found on the line
numbers = re.findall(r"(\d+\.?\d*|\d*\.\d+)", search_line)
if numbers:
    val = float(numbers[0])  # ❌ Takes FIRST number always
```

**Issue:** When multiple numbers appear on a line, the function always takes the FIRST number instead of matching the position to the test name. 

**Example Failure:**
```
Hemoglobin Neutrophils Lymphocytes     11.1  38.0  48.0
```
When extracting Hemoglobin, if this columnar line is parsed, it would take `11.1` (correct by luck). But if the line is structured differently, it might take a completely wrong value.

---

### 2. **Shared Value Tracking Bug (Lines 461, 493)**

**Problem:**
```python
used_values = set()

# Line 465 - Absolute counts phase
if val > 0 and val not in used_values:
    values[test_name] = val
    used_values.add(val)  # ❌ Adds the VALUE

# Line 494 - Regular tests phase  
if val > 0 and val not in used_values:  # ❌ Checks if VALUE already used
    values[test_name] = val
    used_values.add(val)
```

**Issue:** Tracking by VALUE instead of POSITION means:
- If two different tests have the same value (e.g., both `48.0`), the second one is skipped
- Duplicate values like `100.0`, `50.0`, `10.0` cause entire fields to be marked as "already extracted"
- This is the PRIMARY reason fields are missing!

---

### 3. **Early Break Logic Limits Search (Lines 468, 500)**

**Problem:**
```python
for line_idx, line in enumerate(lines):
    found = False
    # Skip lines with "abs"
    if " abs" in line or " absolute" in line:
        continue
    
    for pattern in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            # Search for value
            for search_idx in search_range:
                # ...
                if found:
                    break
            if found:
                break
    
    if found:
        break  # ❌ Stops searching after FIRST line that matches pattern
```

**Issue:** 
- If a test name appears in a section header or early in the document, it stops searching
- Doesn't try to find the value on that line - just moves to next test
- Multiple occurrences of same test name aren't handled

---

### 4. **Incomplete Format Detection (Lines 215-240)**

**Problem:** The `_universal_extraction()` function checks for "columnar" format:
```python
if test_lines and len(test_lines) >= 10:
    # Columnar format detected
    # Match test names in order to values in order
```

**Issue:**
- If only 9 test names are detected (not 10+), it falls back to other methods
- Falls back to position-based matching which can fail with complex formats
- Multi-section reports (COMPLETE BLOOD COUNT, DIFFERENTIAL, ABSOLUTE COUNTS) confuse the detector

---

### 5. **Position-Based Matching Fails in Complex Layouts (Lines 280-340)**

**Problem:** Uses "distance score" to match:
```python
col_score = rdist if result_col_pos != -1 else abs(npos - test_pos)
distance_score = abs(npos - test_pos)
total_score = col_score * 0.7 + distance_score * 0.3

# If score below threshold: match it
if total_score < best_score:
    best_score = total_score
    best_match = val
```

**Issue:**
- When multiple numbers are nearby, the "best" match is ambiguous
- Scoring algorithm doesn't account for unit/range constraints
- A value like `1.5` could match either Hemoglobin or MCH incorrectly

---

## Example Scenario: Why Fields Go Missing

**Report Format:**
```
HEMOGLOBIN                                    11.1
TOTAL R.B.C. COUNT                           4.05  
HAEMATOCRIT (PCV/HCT)                        48.9
NEUTROPHILS %                                38.0
NEUTROPHILS (ABS)                           1600
```

**Extraction Process:**
1. Extract `11.1` for Hemoglobin ✓
2. Extract `4.05` for R.B.C. → marks `4.05` as used
3. Extract `48.9` for Haematocrit → marks `48.9` as used  
4. Extract `38.0` for Neutrophils % → marks `38.0` as used
5. Try to extract Lymphocytes - searches but if value was `48.0` earlier, skips it
6. Try to extract Neutrophils (abs) - value is `1600`, tries to match but if searching fails early, stops

**Result:** 5 fields extracted, 13 missing

---

## Solutions to Implement

### Fix 1: Use Position-Based Tracking Instead of Value-Based
```python
used_positions = set()  # Track (line_num, number_index)

for idx, (lnum, pos, val) in enumerate(all_numbers):
    if idx in used_positions:
        continue
    # ... extract value ...
    used_positions.add(idx)
```

### Fix 2: Implement Multi-Pattern Extraction with Better Matching
- Match test name to value using proximity + unit constraints
- Use value range validation: if expected range is 10-17, reject values < 5 or > 100
- Return best match from multiple candidates

### Fix 3: Separate Absolute Counts Section from Percentages
- Parse document into sections (COMPLETE BLOOD COUNT, DIFFERENTIAL, ABSOLUTE)
- Extract each section independently
- Merge results with conflict resolution

### Fix 4: Add Fallback Extraction with Manual Pattern List
- If automatic extraction gets < 12 fields, trigger fallback
- Use OCR-specific patterns (account for digit confusions: 0→O, 1→l, etc.)
- Implement confidence scoring

### Fix 5: Validate Extracted Values
```python
# For each test, validate extracted value
if test_name in REFERENCE_RANGES:
    min_val = REFERENCE_RANGES[test_name]["min"]
    max_val = REFERENCE_RANGES[test_name]["max"]
    
    # If value is way outside range, it's probably wrong
    if value < min_val * 0.5 or value > max_val * 2:
        flag_for_manual_verification()
```

---

## Impact
- **Critical**: Affects dengue diagnosis (uses multiple CBC values)
- **Critical**: Affects asthma diagnosis (uses CBC values)
- **High**: User experience (incomplete reports look broken)

## Recommended Priority
1. **URGENT**: Fix used_values tracking (causes cascading failures)
2. **HIGH**: Add value range validation 
3. **MEDIUM**: Implement section-aware parsing
4. **LOW**: Add manual verification UI
