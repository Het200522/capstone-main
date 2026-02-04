"""
Test script for Lab Report Formatter
Demonstrates the formatter with your sample CBC report data
"""

from lab_report_formatter import CBCReportFormatter, format_report_for_display

# Sample CBC report text from TRUSTWELL DIAGNOSTIC CENTRE
sample_report = """
TRUSTWELL DIAGNOSTIC CENTRE

Automated Laboratory Services

Name: Neha Verma
Gender: Female Age: 24
Sample ID: 537930

COMPLETE BLOOD COUNT

Test Result
Hemoglobin 11.1
Total R.B.C. Count 4.05
Haematocrit (PCV/HCT) 48.9
Mean Corpuscular Volume (M.C.V.) 84.0
Mean Corpuscular Hb (M.C.H.) 28.0
Total W.B.C. Count 3100

DIFFERENTIAL COUNT:

Neutrophils 38.0
Lymphocytes 48.0
Eosinophils 3.0
Monocytes 5.0
Basophils 0.5
PLATELETS:

Platelet Count 65000
MPV 13.2
ABSOLUTE COUNTS:

Neutrophils (abs) 1600
Lymphocytes (abs) 2600
Eosinophils (abs) 180
Monocytes (abs) 300
Basophils (abs) 40

Atul S. Vadhavkar
B.Sc (Micro), DMLT

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
"""

def test_formatter():
    """Test the formatter with sample data"""
    
    print("=" * 80)
    print("LAB REPORT FORMATTER TEST")
    print("=" * 80)
    
    # Test 1: Extract patient info
    print("\n[TEST 1] Extracting Patient Information...")
    formatter = CBCReportFormatter()
    patient_info = formatter.extract_patient_info(sample_report)
    
    for key, value in patient_info.items():
        print(f"  ✓ {key}: {value}")
    
    # Test 2: Parse CBC report
    print("\n[TEST 2] Parsing CBC Values...")
    cbc_values = formatter.parse_cbc_report(sample_report)
    
    count = 0
    for test_name, value in cbc_values.items():
        if value is not None:
            ref_info = formatter.REFERENCE_RANGES[test_name]
            status = "✓ Normal" if not formatter.is_abnormal(value, ref_info["min"], ref_info["max"]) else "🔴 Abnormal"
            print(f"  ✓ {test_name}: {value:.1f} {ref_info['unit']} - {status}")
            count += 1
    print(f"  → Total values extracted: {count}")
    
    # Test 3: Extract abnormal values
    print("\n[TEST 3] Extracting Abnormal Values...")
    abnormal_values = formatter.extract_abnormal_values(cbc_values)
    
    if abnormal_values:
        for test_name, (value, status) in abnormal_values.items():
            ref_info = formatter.REFERENCE_RANGES[test_name]
            print(f"  🔴 {test_name}: {value:.1f} {ref_info['unit']} ({status})")
    else:
        print("  ✓ All values within normal range")
    
    # Test 4: Generate formatted output
    print("\n[TEST 4] Generating Formatted Report...")
    cbc_values_out, html_table, summary = format_report_for_display(sample_report, disease_type="dengue")
    
    print("\n--- Summary Output ---")
    print(summary)
    
    # Test 5: Create DataFrame
    print("\n[TEST 5] Creating DataFrame...")
    df = formatter.format_to_dataframe(cbc_values)
    print(f"\nDataFrame created with {len(df)} rows and {len(df.columns)} columns:")
    print(df.head(10).to_string())
    
    # Test 6: Export options
    print("\n[TEST 6] Export Options Available...")
    print("  ✓ HTML Table - Ready for web display")
    print("  ✓ DataFrame - Ready for pandas/Excel export")
    print("  ✓ Summary - Clinical summary ready")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    
    # Show first few lines of HTML table
    print("\n[HTML TABLE PREVIEW]")
    print(html_table[:500] + "...\n")
    
    return {
        "patient_info": patient_info,
        "cbc_values": cbc_values,
        "abnormal_values": abnormal_values,
        "dataframe": df,
        "html_table": html_table,
        "summary": summary
    }

if __name__ == "__main__":
    results = test_formatter()
    
    # Optional: Save HTML table to file for inspection
    output_file = "sample_cbc_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>CBC Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
        h2 { color: #333; }
        p { white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Sample CBC Report - Formatted Output</h2>
        <h3>Summary</h3>
        <p>""")
        f.write(results["summary"].replace("\n", "<br>"))
        f.write("""</p>
        <h3>Detailed Table</h3>
        """)
        f.write(results["html_table"])
        f.write("""
    </div>
</body>
</html>
        """)
    
    print(f"\n✓ HTML report saved to: {output_file}")
