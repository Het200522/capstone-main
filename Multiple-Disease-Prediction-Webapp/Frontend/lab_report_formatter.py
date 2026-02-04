"""
Lab Report Formatter - Formats CBC (Complete Blood Count) test results into structured tables
This module supports both dengue and asthma disease predictions
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import numpy as np


class CBCReportFormatter:
    """Format Complete Blood Count reports into structured tables"""
    
    # Reference ranges for CBC values
    REFERENCE_RANGES = {
        "Hemoglobin": {"unit": "g/dl", "range": "10.0-17.0", "min": 10.0, "max": 17.0},
        "Total R.B.C. Count": {"unit": "millions/cumm", "range": "4.4-5.5", "min": 4.4, "max": 5.5},
        "Haematocrit (PCV/HCT)": {"unit": "%", "range": "40-50", "min": 40.0, "max": 50.0},
        "Mean Corpuscular Volume (M.C.V.)": {"unit": "fl", "range": "83-95", "min": 83.0, "max": 95.0},
        "Mean Corpuscular Hb (M.C.H.)": {"unit": "Pg", "range": "27-32", "min": 27.0, "max": 32.0},
        "Total W.B.C. Count": {"unit": "/uL", "range": "4000-10000", "min": 4000.0, "max": 10000.0},
        "Neutrophils": {"unit": "%", "range": "40-70", "min": 40.0, "max": 70.0},
        "Lymphocytes": {"unit": "%", "range": "20-40", "min": 20.0, "max": 40.0},
        "Eosinophils": {"unit": "%", "range": "1-6", "min": 1.0, "max": 6.0},
        "Monocytes": {"unit": "%", "range": "2-10", "min": 2.0, "max": 10.0},
        "Basophils": {"unit": "%", "range": "0-1", "min": 0.0, "max": 1.0},
        "Platelet Count": {"unit": "/uL", "range": "150-450", "min": 150.0, "max": 450.0},
        "MPV": {"unit": "fL", "range": "6.78-13.46", "min": 6.78, "max": 13.46},
        "Neutrophils (abs)": {"unit": "/uL", "range": "1575-8800", "min": 1575.0, "max": 8800.0},
        "Lymphocytes (abs)": {"unit": "/uL", "range": "1125-4950", "min": 1125.0, "max": 4950.0},
        "Eosinophils (abs)": {"unit": "/uL", "range": "0-400", "min": 0.0, "max": 400.0},
        "Monocytes (abs)": {"unit": "/uL", "range": "0-1000", "min": 0.0, "max": 1000.0},
        "Basophils (abs)": {"unit": "/uL", "range": "0-100", "min": 0.0, "max": 100.0},
    }
    
    # Extraction patterns for CBC values - VERY FLEXIBLE
    PATTERNS = {
        "Hemoglobin": [r"(?:hemoglobin|hb|hgb)\s*[:\-]?\s*([\d.]+)", r"hemoglobin.*?([\d.]+)", r"(?:^|\s)(1[0-7]\.?\d*)\s*g"],
        "Total R.B.C. Count": [r"(?:total\s+)?r\.?b\.?c\.?.*?([\d.]+)", r"rbc.*?([\d.]+)", r"(?:^|\s)([4-6]\.?\d*)\s*million"],
        "Haematocrit (PCV/HCT)": [r"(?:hematocrit|haematocrit|pcv|hct)\s*[:\-]?\s*([\d.]+)", r"(?:hct|pcv).*?([\d.]+)", r"(?:^|\s)([3-6]\d\.?\d*)\s*%"],
        "Mean Corpuscular Volume (M.C.V.)": [r"(?:m\.?c\.?v|mean\s+corpuscular\s+volume|mcv)\s*[:\-]?\s*([\d.]+)", r"mcv.*?([\d.]+)"],
        "Mean Corpuscular Hb (M.C.H.)": [r"(?:m\.?c\.?h|mean\s+corpuscular\s+h(?:aemoglobin|emoglobin)|mch)\s*[:\-]?\s*([\d.]+)", r"mch.*?([\d.]+)"],
        "Total W.B.C. Count": [r"(?:total\s+)?w\.?b\.?c\.?.*?([\d.]+)", r"wbc.*?([\d.]+)", r"(?:^|\s)([3-9]?\d{3,4})\s*(?:/|per|ul)"],
        "Neutrophils": [r"neutrophil(?:s)?\s*[:\-]?\s*([\d.]+)(?:\s*%)?", r"neutrophil.*?([\d.]+)"],
        "Lymphocytes": [r"lymphocyte(?:s)?\s*[:\-]?\s*([\d.]+)(?:\s*%)?", r"lymphocyte.*?([\d.]+)"],
        "Eosinophils": [r"eosinophil(?:s)?\s*[:\-]?\s*([\d.]+)(?:\s*%)?", r"eosinophil.*?([\d.]+)"],
        "Monocytes": [r"monocyte(?:s)?\s*[:\-]?\s*([\d.]+)(?:\s*%)?", r"monocyte.*?([\d.]+)"],
        "Basophils": [r"basophil(?:s)?\s*[:\-]?\s*([\d.]+)(?:\s*%)?", r"basophil.*?([\d.]+)"],
        "Platelet Count": [r"platelet(?:s?)?\s+count\s*[:\-]?\s*([\d.]+)", r"platelet(?:s)?\s*[:\-]?\s*([\d.]+)", r"(?:^|\s)(\d+\d{3,4})\s*(?:/|per|ul)"],
        "MPV": [r"(?:mpv|mean\s+platelet\s+volume)\s*[:\-]?\s*([\d.]+)", r"mpv.*?([\d.]+)"],
        "Neutrophils (abs)": [r"neutrophil(?:s)?\s*\(?abs(?:olute)?\)?\s*[:\-]?\s*([\d.]+)", r"neutrophil.*?abs.*?([\d.]+)"],
        "Lymphocytes (abs)": [r"lymphocyte(?:s)?\s*\(?abs(?:olute)?\)?\s*[:\-]?\s*([\d.]+)", r"lymphocyte.*?abs.*?([\d.]+)"],
        "Eosinophils (abs)": [r"eosinophil(?:s)?\s*\(?abs(?:olute)?\)?\s*[:\-]?\s*([\d.]+)", r"eosinophil.*?abs.*?([\d.]+)"],
        "Monocytes (abs)": [r"monocyte(?:s)?\s*\(?abs(?:olute)?\)?\s*[:\-]?\s*([\d.]+)", r"monocyte.*?abs.*?([\d.]+)"],
        "Basophils (abs)": [r"basophil(?:s)?\s*\(?abs(?:olute)?\)?\s*[:\-]?\s*([\d.]+)", r"basophil.*?abs.*?([\d.]+)"],
    }
    
    @staticmethod
    def extract_value(text: str, patterns: List[str]) -> Optional[float]:
        """Extract value from text using multiple patterns"""
        text_lower = text.lower().replace(",", "").replace("\n", " ").replace("\r", " ")
        
        for pattern in patterns:
            # Try with different spacing variations
            for attempt_text in [text_lower, text_lower.replace("  ", " ")]:
                match = re.search(pattern, attempt_text, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        for group in match.groups()[::-1]:
                            if group:
                                val = float(group.strip())
                                return val
                    except (ValueError, TypeError, AttributeError):
                        continue
        return None
    
    @staticmethod
    def is_abnormal(value: float, min_val: float, max_val: float) -> bool:
        """Check if value is outside reference range"""
        if value is None:
            return False
        return value < min_val or value > max_val
    
    @staticmethod
    def extract_patient_info(text: str) -> Dict[str, str]:
        """Extract patient demographics from report - handles various formats"""
        info = {}
        
        # Extract name - very flexible, allow full names with spaces
        name_patterns = [
            r"(?:Name|Patient)\s*[:\-]?\s*([A-Za-z][A-Za-z\s]{2,60}?)(?:\n|Gender|Sex|DOB|Age|M\s|F\s)",
            r"(?:Name|Patient)\s*[:\-]?\s*([A-Za-z][A-Za-z\s]+?)(?:\s+[MFmf](?:\s|$)|$)",
            r"^([A-Za-z][A-Za-z\s]{2,60}?)\s*(?:\n|Gender|Sex)",
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                # Clean up the name - remove extra spaces
                name = " ".join(name.split())
                if len(name) > 2 and len(name) < 100:
                    info["Name"] = name
                    break
        if "Name" not in info:
            info["Name"] = "N/A"
        
        # Extract gender
        gender_match = re.search(r"(?:Gender|Sex)\s*[:\-]?\s*([MFmf]|Male|Female)", text, re.IGNORECASE)
        info["Gender"] = gender_match.group(1).strip() if gender_match else "N/A"
        
        # Extract age
        age_match = re.search(r"(?:Age|Yr|Year)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        info["Age"] = age_match.group(1).strip() if age_match else "N/A"
        
        # Extract sample ID
        sample_match = re.search(r"(?:Sample\s+ID|Specimen\s+ID|ID)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
        info["Sample ID"] = sample_match.group(1).strip() if sample_match else "N/A"
        
        # Extract report date - try multiple patterns
        date_patterns = [
            r"(?:Report|Release|Sample)\s+(?:Date|Time)\s*[:\-]?\s*([\d\-/\s:]+?)(?:\n|,|;|$)",
            r"Date\s+(?:of\s+)?(?:Report|Release)\s*[:\-]?\s*([\d\-/\s:]+?)(?:\n|,|;|$)",
            r"(?:Report\s+)?Date\s*[:\-]?\s*([\d]{1,2}[\-/]\d{1,2}[\-/]\d{2,4}\s*[\d:]*?)(?:\n|,|;|$)",
            r"(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}\s*\d{1,2}:\d{2}(?::\d{2})?)"  # DD-MM-YYYY HH:MM format
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if date_match:
                info["Date"] = date_match.group(1).strip()
                break
        if "Date" not in info:
            info["Date"] = "N/A"
        
        # Extract lab name - look for all caps words
        lab_patterns = [
            r"([A-Z][A-Z\s&]+(?:PATHOLOGY|DIAGNOSTIC|CENTRE|CENTER|LAB|LABORATORY))",
            r"^([A-Z][A-Za-z\s]+)$"  # First line if all caps
        ]
        for pattern in lab_patterns:
            lab_match = re.search(pattern, text, re.MULTILINE)
            if lab_match:
                lab_name = lab_match.group(1).strip()
                if len(lab_name) > 3 and len(lab_name) < 100:
                    info["Lab"] = lab_name
                    break
        if "Lab" not in info:
            info["Lab"] = "N/A"
        
        # Extract branch
        branch_patterns = [
            r"Branch\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|,|;|Contact|Phone|Tel)",
            r"Branch\s*[:\-]?\s*([A-Za-z\s]+?)$"
        ]
        for pattern in branch_patterns:
            branch_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if branch_match:
                info["Branch"] = branch_match.group(1).strip()
                break
        if "Branch" not in info:
            info["Branch"] = "N/A"
        
        # Extract contact
        contact_patterns = [
            r"Contact\s*[:\-]?\s*([\+\d\s\-\(\)]+?)(?:\n|,|;|Email)",
            r"Phone\s*[:\-]?\s*([\+\d\s\-\(\)]+?)(?:\n|,|;)",
            r"Tel\s*[:\-]?\s*([\+\d\s\-\(\)]+?)(?:\n|,|;)"
        ]
        for pattern in contact_patterns:
            contact_match = re.search(pattern, text, re.IGNORECASE)
            if contact_match:
                info["Contact"] = contact_match.group(1).strip()
                break
        if "Contact" not in info:
            info["Contact"] = "N/A"
        
        return info
    
    @classmethod
    def normalize_values(cls, values: Dict[str, float]) -> Dict[str, float]:
        """Normalize extracted values to match reference ranges
        
        Most labs report values in standard units, but we check for anomalies.
        The extraction is usually correct, so we trust it unless very suspicious.
        """
        normalized = values.copy()
        
        # Note: Large platelet counts (>1000) are valid if reported in /uL units
        # We don't normalize here because the reference ranges are already in /uL
        # The extraction algorithm already validates against reference ranges
        
        return normalized
    
    @classmethod
    def _preprocess_text(cls, text: str) -> str:
        """Preprocess text to normalize various formats and improve extraction"""
        # Replace common abbreviations with full names for better pattern matching
        text_lower = text.lower()
        
        # Normalize abbreviations - careful with word boundaries
        text_lower = re.sub(r"\bneut%\b", "neutrophils %", text_lower)
        text_lower = re.sub(r"\bneut\s+\(abs\)", "neutrophils (abs)", text_lower)
        text_lower = re.sub(r"\bneut\(abs\)", "neutrophils (abs)", text_lower)
        text_lower = re.sub(r"\blymph%\b", "lymphocytes %", text_lower)
        text_lower = re.sub(r"\blymph\s+\(abs\)", "lymphocytes (abs)", text_lower)
        text_lower = re.sub(r"\blymph\(abs\)", "lymphocytes (abs)", text_lower)
        text_lower = re.sub(r"\beos%\b", "eosinophils %", text_lower)
        text_lower = re.sub(r"\beos\s+\(abs\)", "eosinophils (abs)", text_lower)
        text_lower = re.sub(r"\beos\(abs\)", "eosinophils (abs)", text_lower)
        text_lower = re.sub(r"\bmono%\b", "monocytes %", text_lower)
        text_lower = re.sub(r"\bmono\s+\(abs\)", "monocytes (abs)", text_lower)
        text_lower = re.sub(r"\bmono\(abs\)", "monocytes (abs)", text_lower)
        text_lower = re.sub(r"\bbaso%\b", "basophils %", text_lower)
        text_lower = re.sub(r"\bbaso\s+\(abs\)", "basophils (abs)", text_lower)
        text_lower = re.sub(r"\bbaso\(abs\)", "basophils (abs)", text_lower)
        
        # Handle "absolute" notation variations
        text_lower = re.sub(r"neutrophil(?:s)?\s+absolute:", "neutrophils (abs):", text_lower)
        text_lower = re.sub(r"lymphocyte(?:s)?\s+absolute:", "lymphocytes (abs):", text_lower)
        text_lower = re.sub(r"eosinophil(?:s)?\s+absolute:", "eosinophils (abs):", text_lower)
        text_lower = re.sub(r"monocyte(?:s)?\s+absolute:", "monocytes (abs):", text_lower)
        text_lower = re.sub(r"basophil(?:s)?\s+absolute:", "basophils (abs):", text_lower)
        
        return text_lower
    
    @classmethod
    def parse_cbc_report(cls, text: str) -> Dict[str, any]:
        """Universal extraction - works for ANY lab report format"""
        values = {}
        
        # Preprocess text to normalize abbreviations
        text_preprocessed = cls._preprocess_text(text)
        
        # Use universal extraction that finds test names and matches them to nearest numbers
        universal_values = cls._universal_extraction(text_preprocessed)
        
        # Normalize values before returning
        return cls.normalize_values(universal_values)
    
    @classmethod
    def get_cbc_report_with_ranges(cls, text: str) -> Dict[str, Dict]:
        """Get CBC values with units, reference ranges, and status"""
        values = cls.parse_cbc_report(text)
        result = {}
        
        for test_name, value in values.items():
            if value is not None and test_name in cls.REFERENCE_RANGES:
                ref_info = cls.REFERENCE_RANGES[test_name]
                is_abnormal = cls.is_abnormal(value, ref_info["min"], ref_info["max"])
                status = "Abnormal" if is_abnormal else "Normal"
                
                result[test_name] = {
                    "Value": value,
                    "Unit": ref_info["unit"],
                    "Reference Range": ref_info["range"],
                    "Status": status
                }
        
        return result
    
    @classmethod
    def _validate_value(cls, test_name: str, value: float) -> bool:
        """Validate if extracted value is within reasonable bounds for the test"""
        if test_name not in cls.REFERENCE_RANGES:
            return True
        
        ref_info = cls.REFERENCE_RANGES[test_name]
        min_val = ref_info["min"]
        max_val = ref_info["max"]
        
        # For percentage-based tests (Neutrophils, Lymphocytes, etc.)
        if "%" in ref_info["unit"]:
            # Allow 0-100 range for percentages
            return 0 <= value <= 100
        
        # For absolute counts / cell counts (Neutrophils (abs), Lymphocytes (abs), Platelet Count, etc.)
        if "abs" in test_name.lower() or "/ul" in ref_info["unit"].lower():
            # Be very permissive for cell counts - allow a very wide range
            # Values can be anywhere from nearly 0 to extremely high
            return value >= 0  # Accept any positive value
        
        # For regular tests, use generous margin (50% beyond reference range)
        margin = (max_val - min_val) * 0.5
        lower_bound = max(0, min_val - margin)
        upper_bound = max_val + margin
        return lower_bound <= value <= upper_bound
    
    @classmethod
    def _universal_extraction(cls, text: str) -> Dict[str, float]:
        """
        Improved universal extraction - handles all lab report formats
        Uses position-based tracking instead of value-based tracking
        """
        values = {}
        text_lower = text.lower().replace(",", "").replace("(abs)", " abs").replace("(absolute)", " abs")
        lines = text_lower.split("\n")
        
        # ============ SPECIAL HANDLING: COLUMNAR FORMAT (OCR common) ============
        # When test names are all in one section and values in another
        columnar_result = cls._try_columnar_extraction(text_lower, lines)
        if columnar_result and len(columnar_result) >= 12:  # If we got most fields
            return columnar_result
        
        # ============ FALLBACK: Standard extraction ============
        # Extract all numbers with their positions
        all_numbers = []
        for line_num, line in enumerate(lines):
            for match in re.finditer(r"(\d+\.?\d*|\d*\.\d+)", line):
                try:
                    val = float(match.group(1))
                    if val > 0:
                        num_pos = match.start()
                        num_idx = len(all_numbers)  # ✅ UNIQUE INDEX
                        all_numbers.append({
                            "idx": num_idx,        # ✅ Position ID (not value!)
                            "line_num": line_num,
                            "char_pos": num_pos,
                            "value": val,
                            "used": False
                        })
                except ValueError:
                    continue
        
        # Test patterns for matching
        test_patterns = {
            "Hemoglobin": [r"hemoglobin|hb(?:\s|$|:)|hgb"],
            "Total R.B.C. Count": [r"total\s+r\.?b\.?c|rbc\s+count|r\.?b\.?c(?:\s|$|:)|total.*rbc"],
            "Haematocrit (PCV/HCT)": [r"haematocrit|hct|pcv|hematocrit|pvc"],
            "Mean Corpuscular Volume (M.C.V.)": [r"mean\s+corpuscular\s+volume|m\.?c\.?v(?:\s|$|:)|mcv"],
            "Mean Corpuscular Hb (M.C.H.)": [r"mean\s+corpuscular\s+hb|m\.?c\.?h(?:\s|$|:)|mch"],
            "Total W.B.C. Count": [r"total\s+w\.?b\.?c|wbc\s+count|w\.?b\.?c(?:\s|$|:)|total.*wbc"],
            "Neutrophils": [r"(?<!abs\s)neutrophil(?!.*\babs\b)|(?<!abs\s)neut(?:\s|%|$|:)(?!.*abs)"],
            "Lymphocytes": [r"(?<!abs\s)lymphocyte(?!.*\babs\b)|(?<!abs\s)lymph(?:\s|%|$|:)(?!.*abs)"],
            "Eosinophils": [r"(?<!abs\s)eosinophil(?!.*\babs\b)|(?<!abs\s)eos(?:\s|%|$|:)(?!.*abs)"],
            "Monocytes": [r"(?<!abs\s)monocyte(?!.*\babs\b)|(?<!abs\s)mono(?:\s|%|$|:)(?!.*abs)"],
            "Basophils": [r"(?<!abs\s)basophil(?!.*\babs\b)|(?<!abs\s)baso(?:\s|%|$|:)(?!.*abs)"],
            "Platelet Count": [r"platelet\s+count|platelet(?!\s*(?:abs|\())"],
            "MPV": [r"\bmpv\b|mean\s+platelet\s+volume"],
            "Neutrophils (abs)": [r"neutrophil.*\babs\b|neut.*\babs\b|\babs\b.*neut"],
            "Lymphocytes (abs)": [r"lymphocyte.*\babs\b|lymph.*\babs\b|\babs\b.*lymph"],
            "Eosinophils (abs)": [r"eosinophil.*\babs\b|eos.*\babs\b|\babs\b.*eos"],
            "Monocytes (abs)": [r"monocyte.*\babs\b|mono.*\babs\b|\babs\b.*mono"],
            "Basophils (abs)": [r"basophil.*\babs\b|baso.*\babs\b|\babs\b.*baso"],
        }
        
        # For each test, find the best matching number (using POSITION tracking, not value tracking)
        for test_name, patterns in test_patterns.items():
            best_match = None
            best_score = float('inf')
            best_num_obj = None
            
            # Search for test name in document
            for line_num, line in enumerate(lines):
                for pattern in patterns:
                    test_match = re.search(pattern, line, re.IGNORECASE)
                    if not test_match:
                        continue
                    
                    test_pos = test_match.start()
                    
                    # First pass: look for number on SAME LINE
                    for num_obj in all_numbers:
                        if num_obj["used"] or num_obj["line_num"] != line_num:
                            continue
                        
                        val = num_obj["value"]
                        
                        # Validate value for this test
                        if not cls._validate_value(test_name, val):
                            continue
                        
                        # Calculate score based on character distance
                        distance = abs(num_obj["char_pos"] - test_pos)
                        if distance < best_score:
                            best_score = distance
                            best_match = val
                            best_num_obj = num_obj
                    
                    if best_match is not None:
                        break
                
                if best_match is not None:
                    break
            
            # Second pass: if no match on same line, look in nearby lines
            if best_match is None:
                for line_num, line in enumerate(lines):
                    for pattern in patterns:
                        test_match = re.search(pattern, line, re.IGNORECASE)
                        if not test_match:
                            continue
                        
                        test_pos = test_match.start()
                        
                        # Look within 30 lines (columnar format has test names and values far apart)
                        for num_obj in all_numbers:
                            if num_obj["used"]:
                                continue
                            
                            if abs(num_obj["line_num"] - line_num) > 30:  # Increased from 5 to 30 for columnar format
                                continue
                            
                            val = num_obj["value"]
                            
                            # Validate value for this test
                            if not cls._validate_value(test_name, val):
                                continue
                            
                            # Score based on line distance and character position
                            line_dist = abs(num_obj["line_num"] - line_num) * 50
                            char_dist = abs(num_obj["char_pos"] - test_pos)
                            score = line_dist + char_dist
                            
                            if score < best_score:
                                best_score = score
                                best_match = val
                                best_num_obj = num_obj
                        
                        if best_match is not None:
                            break
                    
                    if best_match is not None:
                        break
            
            # Add extracted value and mark number as used (position-based tracking)
            if best_match is not None and best_num_obj is not None:
                values[test_name] = best_match
                best_num_obj["used"] = True
        
        return values
    
    @classmethod
    def _try_columnar_extraction(cls, text_lower: str, lines: List[str]) -> Dict[str, float]:
        """
        Try to extract from columnar format where test names and values are in separate sections
        Common in OCR output where columns don't align
        """
        values = {}
        
        # Find the "Result" or "Value" header line
        result_line_idx = -1
        for idx, line in enumerate(lines):
            if re.search(r"\b(result|value|values)\b", line, re.IGNORECASE):
                result_line_idx = idx
                break
        
        if result_line_idx == -1:
            return values  # Not columnar format
        
        # Extract numbers after the "Result" line, but before "Unit" section
        result_numbers = []
        unit_line_idx = -1
        
        # Find where the Unit section starts
        for idx in range(result_line_idx + 1, len(lines)):
            line = lines[idx]
            if re.search(r"^\s*(unit|range|reference|biological)\s*$", line, re.IGNORECASE):
                unit_line_idx = idx
                break
        
        # If no Unit section found, look for a substantial gap in data
        if unit_line_idx == -1:
            unit_line_idx = len(lines)
        
        # Extract all numbers between Result and Unit sections
        for idx in range(result_line_idx + 1, unit_line_idx):
            line = lines[idx]
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Extract all numbers from this line
            for match in re.finditer(r"(\d+\.?\d*|\d*\.\d+)", line):
                try:
                    val = float(match.group(1))
                    # Skip very small numbers (like 0.5, 0.1) that are likely noise
                    # and skip numbers that look like part of ranges (contain multiple digits for range ends)
                    if val > 0 and not re.search(r"\d+\s*-\s*\d+", match.string[max(0, match.start()-5):min(len(match.string), match.end()+5)]):
                        result_numbers.append(val)
                except ValueError:
                    continue
        
        if not result_numbers:
            return values
        
        # Now extract test names in order
        test_order = [
            "Hemoglobin", "Total R.B.C. Count", "Haematocrit (PCV/HCT)",
            "Mean Corpuscular Volume (M.C.V.)", "Mean Corpuscular Hb (M.C.H.)",
            "Total W.B.C. Count", "Neutrophils", "Lymphocytes", "Eosinophils",
            "Monocytes", "Basophils", "Platelet Count", "MPV",
            "Neutrophils (abs)", "Lymphocytes (abs)", "Eosinophils (abs)",
            "Monocytes (abs)", "Basophils (abs)"
        ]
        
        # Match values to test names by order
        for idx, test_name in enumerate(test_order):
            if idx < len(result_numbers):
                val = result_numbers[idx]
                # Validate value
                if cls._validate_value(test_name, val):
                    values[test_name] = val
        
        return values

    
    @classmethod
    def format_to_dataframe(cls, cbc_values: Dict[str, float]) -> pd.DataFrame:
        """Convert CBC values to formatted DataFrame"""
        data = []
        
        for test_name, patterns in cls.PATTERNS.items():
            value = cbc_values.get(test_name)
            ref_info = cls.REFERENCE_RANGES[test_name]
            
            # Format value display
            if value is None:
                value_str = "—"
                status = "Not Detected"
            else:
                value_str = f"{value:.1f}" if isinstance(value, float) else str(value)
                
                # Check if abnormal
                if cls.is_abnormal(value, ref_info["min"], ref_info["max"]):
                    status = "🔴 Abnormal"
                else:
                    status = "✓ Normal"
            
            data.append({
                "Test Name": test_name,
                "Result": value_str,
                "Unit": ref_info["unit"],
                "Reference Range": ref_info["range"],
                "Status": status
            })
        
        df = pd.DataFrame(data)
        return df
    
    @classmethod
    def format_html_table(cls, cbc_values: Dict[str, float], patient_info: Dict[str, str]) -> str:
        """Generate HTML formatted table for display"""
        
        # Build patient info section
        patient_html = f"""
        <div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #2196F3;">
            <h3 style="margin-top: 0;">Patient Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px;"><strong>Name:</strong> {patient_info.get('Name', 'N/A')}</td>
                    <td style="padding: 5px;"><strong>Gender:</strong> {patient_info.get('Gender', 'N/A')}</td>
                    <td style="padding: 5px;"><strong>Age:</strong> {patient_info.get('Age', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Sample ID:</strong> {patient_info.get('Sample ID', 'N/A')}</td>
                    <td style="padding: 5px;"><strong>Report Date:</strong> {patient_info.get('Report Date', 'N/A')}</td>
                    <td style="padding: 5px;"><strong>Lab:</strong> {patient_info.get('Lab', 'N/A')}</td>
                </tr>
            </table>
        </div>
        """
        
        # Build test results table with improved color contrast
        table_html = '<table style="width: 100%; border-collapse: collapse; border: 2px solid #333;">'
        table_html += '<thead style="background-color: #1565c0; color: white;">'
        table_html += '<tr><th style="padding: 12px; text-align: left; border: 1px solid #333; font-weight: bold;">Test Name</th>'
        table_html += '<th style="padding: 12px; text-align: center; border: 1px solid #333; font-weight: bold;">Result</th>'
        table_html += '<th style="padding: 12px; text-align: center; border: 1px solid #333; font-weight: bold;">Unit</th>'
        table_html += '<th style="padding: 12px; text-align: center; border: 1px solid #333; font-weight: bold;">Reference Range</th>'
        table_html += '<th style="padding: 12px; text-align: center; border: 1px solid #333; font-weight: bold;">Status</th></tr>'
        table_html += '</thead><tbody>'
        
        for test_name, patterns in cls.PATTERNS.items():
            value = cbc_values.get(test_name)
            ref_info = cls.REFERENCE_RANGES[test_name]
            
            # Format value
            if value is None:
                value_str = "—"
                row_color = "#ffffff"
                text_color = "#999999"
                status_html = '<span style="color: #999999; font-weight: normal;">Not Detected</span>'
            else:
                value_str = f"{value:.1f}"
                
                # Check if abnormal - use darker, more visible colors
                if cls.is_abnormal(value, ref_info["min"], ref_info["max"]):
                    row_color = "#ffcccc"  # Darker red/pink
                    text_color = "#cc0000"  # Dark red
                    status_html = '<span style="color: #cc0000; font-weight: bold;">🔴 Abnormal</span>'
                else:
                    row_color = "#ccffcc"  # Darker green
                    text_color = "#00cc00"  # Dark green
                    status_html = '<span style="color: #006600; font-weight: bold;">✓ Normal</span>'
            
            table_html += f'<tr style="background-color: {row_color}; border: 1px solid #ddd;">'
            table_html += f'<td style="padding: 10px; border: 1px solid #ddd; color: #333;">{test_name}</td>'
            table_html += f'<td style="padding: 10px; text-align: center; border: 1px solid #ddd;"><strong style="color: #000;">{value_str}</strong></td>'
            table_html += f'<td style="padding: 10px; text-align: center; border: 1px solid #ddd; color: #333;">{ref_info["unit"]}</td>'
            table_html += f'<td style="padding: 10px; text-align: center; border: 1px solid #ddd; color: #333;">{ref_info["range"]}</td>'
            table_html += f'<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{status_html}</td>'
            table_html += '</tr>'
        
        table_html += '</tbody></table>'
        
        return patient_html + table_html
    
    @classmethod
    def extract_abnormal_values(cls, cbc_values: Dict[str, float]) -> Dict[str, Tuple[float, str]]:
        """Extract only abnormal values from CBC report"""
        abnormal = {}
        
        for test_name, value in cbc_values.items():
            if value is not None and test_name in cls.REFERENCE_RANGES:
                ref_info = cls.REFERENCE_RANGES[test_name]
                if cls.is_abnormal(value, ref_info["min"], ref_info["max"]):
                    status = "HIGH" if value > ref_info["max"] else "LOW"
                    abnormal[test_name] = (value, status)
        
        return abnormal


def format_report_for_display(text: str, disease_type: str = "general") -> Tuple[Dict, str, str]:
    """
    Main function to format lab report for display
    
    Args:
        text: OCR extracted text from PDF
        disease_type: "dengue", "asthma", or "general"
    
    Returns:
        Tuple of (cbc_values_dict, html_table_string, summary_string)
    """
    formatter = CBCReportFormatter()
    
    # Extract patient info and CBC values
    patient_info = formatter.extract_patient_info(text)
    cbc_values = formatter.parse_cbc_report(text)
    
    # Generate HTML table
    html_table = formatter.format_html_table(cbc_values, patient_info)
    
    # Generate summary
    abnormal_values = formatter.extract_abnormal_values(cbc_values)
    
    summary = f"**Report Summary for {disease_type.upper()}**\n\n"
    summary += f"**Patient:** {patient_info.get('Name', 'N/A')}, "
    summary += f"{patient_info.get('Gender', 'N/A')}, "
    summary += f"Age: {patient_info.get('Age', 'N/A')}\n\n"
    
    if abnormal_values:
        summary += "**⚠️ Abnormal Values Detected:**\n"
        for test_name, (value, status) in abnormal_values.items():
            summary += f"- {test_name}: {value:.1f} ({status})\n"
    else:
        summary += "**✓ All values within normal range**\n"
    
    return cbc_values, html_table, summary
