# Lab Report Table Formatter - User Guide

## Overview
The Lab Report Table Formatter has been integrated into your disease prediction system to display Complete Blood Count (CBC) test results in a professional, easy-to-read table format for both **Dengue** and **Asthma** disease predictions.

## Features

### ✅ What's New
1. **Professional Table Display** - All CBC results automatically formatted into structured tables with:
   - Test names
   - Actual results
   - Units of measurement
   - Reference ranges
   - Status indicators (Normal ✓ or Abnormal 🔴)

2. **Patient Information Display**
   - Name
   - Gender
   - Age
   - Sample ID
   - Report Date
   - Lab Name

3. **Color-Coded Results**
   - 🟢 Green rows: All values within normal range
   - 🔴 Red rows: Abnormal values (HIGH or LOW)
   - Gray: Values not detected in report

4. **Automatic Abnormality Detection**
   - Compares results against medical reference ranges
   - Highlights values outside normal bounds
   - Indicates whether value is HIGH or LOW

5. **Raw Text Extraction**
   - Hidden by default in expandable section
   - Show raw OCR text for verification if needed

## How to Use

### For Dengue Prediction
1. Go to **🦟 Dengue Prediction** section
2. Select **"Upload PDF (OCR)"** mode
3. Upload your CBC report PDF
4. The system will:
   - Extract text using OCR
   - Parse all CBC values automatically
   - Display a formatted table with patient info and test results
   - Show abnormal values summary
5. Click **"Predict Dengue (PDF)"** for disease prediction

### For Asthma Prediction
1. Go to **🫁 Asthma Prediction** section
2. Select **"Upload PDF (OCR)"** mode
3. Upload your CBC report PDF
4. The system will:
   - Extract text using OCR
   - Parse all CBC values automatically
   - Display a formatted table with patient info and test results
   - Show abnormal values summary
5. Click **"Predict Asthma"** for disease prediction

## Supported CBC Parameters

The formatter recognizes and displays 18 CBC test parameters:

### Complete Blood Count Tests:
- **Hemoglobin** (g/dl)
- **Total R.B.C. Count** (millions/cumm)
- **Haematocrit/PCV/HCT** (%)
- **Mean Corpuscular Volume (M.C.V.)** (fl)
- **Mean Corpuscular Hemoglobin (M.C.H.)** (Pg)
- **Total W.B.C. Count** (/uL)

### Differential Count:
- **Neutrophils** (%)
- **Lymphocytes** (%)
- **Eosinophils** (%)
- **Monocytes** (%)
- **Basophils** (%)

### Platelets:
- **Platelet Count** (/uL)
- **Mean Platelet Volume (MPV)** (fL)

### Absolute Counts:
- **Neutrophils (abs)** (/uL)
- **Lymphocytes (abs)** (/uL)
- **Eosinophils (abs)** (/uL)
- **Monocytes (abs)** (/uL)
- **Basophils (abs)** (/uL)

## Example Output Format

```
┌─────────────────────────────────────────────────────────────┐
│ Patient Information                                          │
├─────────────────────────────────────────────────────────────┤
│ Name: Neha Verma        Gender: Female      Age: 24         │
│ Sample ID: 537930       Report Date: 18-02-2025            │
│ Lab: TRUSTWELL DIAGNOSTIC CENTRE                            │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┬───────┬──────┬────────────┬──────────┐
│ Test Name            │Result │Unit  │Reference  │Status    │
├──────────────────────┼───────┼──────┼────────────┼──────────┤
│ Hemoglobin           │ 11.1  │g/dl  │10.0-17.0  │✓ Normal  │
│ Platelet Count       │ 65000 │/uL   │150-450    │🔴 LOW    │
│ Total W.B.C. Count   │ 3100  │/uL   │4000-10000 │🔴 LOW    │
└──────────────────────┴───────┴──────┴────────────┴──────────┘
```

## Technical Details

### File Location
- Main formatter: `Frontend/lab_report_formatter.py`
- Integrated in: `Frontend/app.py`

### Key Classes & Functions

**CBCReportFormatter** - Main class with static methods:
- `extract_patient_info(text)` - Extracts demographics
- `parse_cbc_report(text)` - Parses all CBC values
- `format_to_dataframe(cbc_values)` - Creates DataFrame
- `format_html_table(cbc_values, patient_info)` - Generates HTML display
- `extract_abnormal_values(cbc_values)` - Finds out-of-range values

**format_report_for_display(text, disease_type)** - Main function
- Takes OCR-extracted text and disease type
- Returns tuple of (values_dict, html_table, summary_string)
- Supports "dengue", "asthma", or "general" disease types

### Customization

To modify reference ranges, edit the `REFERENCE_RANGES` dictionary in `lab_report_formatter.py`:

```python
REFERENCE_RANGES = {
    "Hemoglobin": {"unit": "g/dl", "range": "10.0-17.0", "min": 10.0, "max": 17.0},
    # ... add more or modify existing ranges
}
```

To add new extraction patterns, update the `PATTERNS` dictionary:

```python
PATTERNS = {
    "Your Test Name": [r"pattern1", r"pattern2"],
    # ...
}
```

## Troubleshooting

### Table not displaying?
- Check if OCR extracted the text correctly
- Verify PDF quality is acceptable
- Try with a different PDF

### Missing or incorrect values?
- Some PDFs may have different formatting
- Check the raw extracted text in the expandable section
- Update extraction patterns if needed

### Reference ranges seem wrong?
- Medical reference ranges vary by lab and region
- Update `REFERENCE_RANGES` to match your lab standards
- Verify with your medical professional

## Integration with Disease Prediction

The formatted table works alongside the disease prediction models:

1. **Visual Analysis**: Users can immediately see abnormal values
2. **Contextual Information**: Disease risk is assessed with full patient context
3. **Professional Presentation**: Lab results displayed professionally for clinical use
4. **Audit Trail**: Raw text always available for verification

---

**Note**: This formatter is optimized for CBC reports. For other lab test types, the extraction may need customization based on your specific lab report format.
