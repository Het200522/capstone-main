# Lab Report Formatter - Visual Output Examples

## Example 1: Formatted Patient Information & CBC Table

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      PATIENT INFORMATION                                  ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Name: Neha Verma              Gender: Female         Age: 24             ║
║  Sample ID: 537930             Lab: TRUSTWELL DIAGNOSTIC CENTRE           ║
║  Report Date: 15-11-2025 13:36:11                                         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

## Example 2: Complete Blood Count Results Table

```
╔═════════════════════════════════┬════════╦══════════╦════════════════╦═══════════╗
║ TEST NAME                       │Result ║ Unit     ║ Reference Range║ Status    ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ Hemoglobin                      │ 11.1  ║ g/dl     ║ 10.0-17.0      ║ ✓ Normal  ║
║ Total R.B.C. Count              │ 4.0   ║ millions ║ 4.4-5.5        ║ 🔴 LOW    ║
║ Haematocrit (PCV/HCT)           │ 48.9  ║ %        ║ 40-50          ║ ✓ Normal  ║
║ Mean Corpuscular Volume (M.C.V.)│  —    ║ fl       ║ 83-95          ║ Not Found ║
║ Mean Corpuscular Hb (M.C.H.)    │  —    ║ Pg       ║ 27-32          ║ Not Found ║
║ Total W.B.C. Count              │ 3100  ║ /uL      ║ 4000-10000     ║ 🔴 LOW    ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ DIFFERENTIAL COUNT              │       ║          ║                ║           ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ Neutrophils                     │ 38.0  ║ %        ║ 40-70          ║ 🔴 LOW    ║
║ Lymphocytes                     │ 48.0  ║ %        ║ 20-40          ║ 🔴 HIGH   ║
║ Eosinophils                     │ 3.0   ║ %        ║ 1-6            ║ ✓ Normal  ║
║ Monocytes                       │ 5.0   ║ %        ║ 2-10           ║ ✓ Normal  ║
║ Basophils                       │ 0.5   ║ %        ║ 0-1            ║ ✓ Normal  ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ PLATELETS                       │       ║          ║                ║           ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ Platelet Count                  │ 65000 ║ /uL      ║ 150-450        ║ 🔴 HIGH   ║
║ Mean Platelet Volume (MPV)      │ 13.2  ║ fL       ║ 6.78-13.46     ║ ✓ Normal  ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ ABSOLUTE COUNTS                 │       ║          ║                ║           ║
╠═════════════════════════════════╬════════╬══════════╬════════════════╬═══════════╣
║ Neutrophils (abs)               │ 1600  ║ /uL      ║ 1575-8800      ║ ✓ Normal  ║
║ Lymphocytes (abs)               │ 2600  ║ /uL      ║ 1125-4950      ║ ✓ Normal  ║
║ Eosinophils (abs)               │ 180   ║ /uL      ║ 0-400          ║ ✓ Normal  ║
║ Monocytes (abs)                 │ 300   ║ /uL      ║ 0-1000         ║ ✓ Normal  ║
║ Basophils (abs)                 │ 40    ║ /uL      ║ 0-100          ║ ✓ Normal  ║
╚═════════════════════════════════╩════════╩══════════╩════════════════╩═══════════╝
```

## Example 3: Clinical Summary

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    REPORT SUMMARY FOR DENGUE                              ║
╚════════════════════════════════════════════════════════════════════════════╝

Patient: Neha Verma, Female, Age: 24

⚠️ ABNORMAL VALUES DETECTED:

1. Total R.B.C. Count: 4.0 millions/cumm (LOW)
   - Reference Range: 4.4-5.5 millions/cumm
   - Indicator: Low RBC count
   
2. Total W.B.C. Count: 3100 /uL (LOW)
   - Reference Range: 4000-10000 /uL
   - Indicator: Low WBC count (Leukopenia)
   
3. Neutrophils: 38.0 % (LOW)
   - Reference Range: 40-70 %
   - Indicator: Low neutrophil percentage
   
4. Lymphocytes: 48.0 % (HIGH)
   - Reference Range: 20-40 %
   - Indicator: High lymphocyte percentage (Relative Lymphocytosis)
   
5. Platelet Count: 65000 /uL (HIGH - CRITICAL)
   - Reference Range: 150-450 /uL
   - Indicator: Extremely high platelet count (Thrombocytosis)
   - ⚠️ SIGNIFICANT FINDING

═══════════════════════════════════════════════════════════════════════════════

CLINICAL INTERPRETATION:
The blood count shows several significant abnormalities that warrant further
investigation. The combination of low WBC and RBC with very high platelets
suggests possible hematologic dysfunction or infection response.

RECOMMENDATIONS:
- Consult with medical professional for clinical correlation
- Consider additional tests (liver function, renal function)
- Monitor for signs of dengue fever
- Serial CBC recommended for trend analysis

═══════════════════════════════════════════════════════════════════════════════
```

## Example 4: HTML Table Display (Streamlit App)

```html
<div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #2196F3;">
    <h3 style="margin-top: 0;">Patient Information</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td><strong>Name:</strong> Neha Verma</td>
            <td><strong>Gender:</strong> Female</td>
            <td><strong>Age:</strong> 24</td>
        </tr>
        <tr>
            <td><strong>Sample ID:</strong> 537930</td>
            <td><strong>Report Date:</strong> 15-11-2025 13:36:11</td>
            <td><strong>Lab:</strong> TRUSTWELL DIAGNOSTIC CENTRE</td>
        </tr>
    </table>
</div>

<table style="width: 100%; border-collapse: collapse; border: 2px solid #ddd;">
    <thead style="background-color: #2196F3; color: white;">
        <tr>
            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Test Name</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Result</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Unit</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Reference Range</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Status</th>
        </tr>
    </thead>
    <tbody>
        <tr style="background-color: #e8f5e9;">
            <td style="padding: 10px; border: 1px solid #ddd;">Hemoglobin</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;"><strong>11.1</strong></td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">g/dl</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">10.0-17.0</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">✓ Normal</td>
        </tr>
        <tr style="background-color: #ffe0e0;">
            <td style="padding: 10px; border: 1px solid #ddd;">Total R.B.C. Count</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;"><strong>4.0</strong></td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">millions/cumm</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">4.4-5.5</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">🔴 Abnormal</td>
        </tr>
        <!-- More rows... -->
    </tbody>
</table>
```

## Example 5: Streamlit App Interface Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  🦟 Multiple Disease Prediction System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Dengue Prediction (CBC Analysis)                            │
│                                                                 │
│  ○ Upload PDF (OCR)   ○ Manual Input                            │
│                                                                 │
│  [Choose file...]                                               │
│  Trustwell_CBC_Report.pdf [Upload]                              │
│                                                                 │
│  ▼ 📄 Raw Extracted Text                                        │
│  ┌────────────────────────────────────────┐                     │
│  │ TRUSTWELL DIAGNOSTIC CENTRE            │                     │
│  │ Automated Laboratory Services          │                     │
│  │ ...                                    │                     │
│  └────────────────────────────────────────┘                     │
│                                                                 │
│  📊 Formatted CBC Report                                        │
│                                                                 │
│  ┌────────────────────────────────────────┐                     │
│  │ Patient Information                    │                     │
│  │ Name: Neha Verma                       │                     │
│  │ Gender: Female  Age: 24                │                     │
│  └────────────────────────────────────────┘                     │
│                                                                 │
│  ┌──────────────┬────────┬────────────────┐                     │
│  │ Test Name    │ Result │ Status         │                     │
│  ├──────────────┼────────┼────────────────┤                     │
│  │ Hemoglobin   │ 11.1   │ ✓ Normal       │                     │
│  │ RBC Count    │ 4.0    │ 🔴 Abnormal    │                     │
│  │ WBC Count    │ 3100   │ 🔴 Abnormal    │                     │
│  │ Platelets    │ 65000  │ 🔴 Abnormal    │                     │
│  └──────────────┴────────┴────────────────┘                     │
│                                                                 │
│  ⚠️ Abnormal Values Detected:                                   │
│  • Total R.B.C. Count: 4.0 (LOW)                                │
│  • Total W.B.C. Count: 3100 (LOW)                               │
│  • Platelet Count: 65000 (HIGH)                                 │
│  • Neutrophils: 38.0 (LOW)                                      │
│  • Lymphocytes: 48.0 (HIGH)                                     │
│                                                                 │
│  [Predict Dengue (PDF)]                                         │
│                                                                 │
│  🔴 Dengue Risk Detected | Estimated risk: 75.3%               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Color Coding Legend

- 🟢 **Green (#e8f5e9)**: Values within normal reference range
- 🔴 **Red (#ffe0e0)**: Values outside reference range (Abnormal)
- ⚪ **Gray (#f9f9f9)**: Value not detected in report

## Status Indicators

- ✓ Normal - Value within reference range
- 🔴 Abnormal - Value outside reference range
- — (dash) - Value not detected in report
- 🟡 WARNING - Value significantly abnormal

---

**All these examples are automatically generated and displayed in your Streamlit app when you upload a CBC report PDF!**
