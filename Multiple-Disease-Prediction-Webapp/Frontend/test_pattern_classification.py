#!/usr/bin/env python3
"""
Test pattern-based classification on real bacterial X-ray
"""
import cv2
import numpy as np
from pathlib import Path

# Find the bacterial X-ray image
test_images_dir = Path("data/pneumonia_xray/val/PNEUMONIA")
bacterial_images = list(test_images_dir.glob("*bacteria*.jpeg"))

if bacterial_images:
    for img_path in bacterial_images[:3]:  # Test first 3
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        
        if img is not None:
            h, w = img.shape
            img_norm = img.astype(float) / 255.0
            
            # 1. Detect edges
            edges = cv2.Canny(img.astype(np.uint8), 50, 150)
            edge_mask = edges > 0
            
            # 2. Find dark regions
            dark_mask = img_norm < 0.5
            dark_ratio = np.sum(dark_mask) / (h * w)
            
            # 3. Consolidation patterns
            very_dark = img_norm < 0.3
            very_dark_ratio = np.sum(very_dark) / (h * w)
            
            # 4. Local clustering
            if dark_ratio > 0.05:
                dark_uint8 = (dark_mask * 255).astype(np.uint8)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                dark_uint8 = cv2.morphologyEx(dark_uint8, cv2.MORPH_CLOSE, kernel)
                contours, _ = cv2.findContours(dark_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                num_dark_regions = len(contours)
            else:
                num_dark_regions = 0
            
            # 5. Edge sharpness
            edges_in_dark = np.sum(edge_mask & dark_mask) if dark_ratio > 0.05 else 0
            edge_sharpness = edges_in_dark / max(np.sum(dark_mask), 1)
            
            # 6. Bilateral asymmetry
            left_lung = img_norm[:, :w//2]
            right_lung = img_norm[:, w//2:]
            left_dark = np.sum(left_lung < 0.5) / (left_lung.size)
            right_dark = np.sum(right_lung < 0.5) / (right_lung.size)
            bilateral_asymmetry = abs(left_dark - right_dark)
            
            print(f"\n{'='*60}")
            print(f"Image: {img_path.name}")
            print(f"{'='*60}")
            print(f"Dark Ratio: {dark_ratio:.4f}")
            print(f"Very Dark Ratio: {very_dark_ratio:.4f}")
            print(f"Edge Sharpness: {edge_sharpness:.4f}")
            print(f"Num Dark Regions: {num_dark_regions}")
            print(f"Bilateral Asymmetry: {bilateral_asymmetry:.4f}")
            
            # Classify
            if dark_ratio > 0.15 and edge_sharpness > 0.15:
                predicted = "Bacterial"
            elif dark_ratio > 0.20 and bilateral_asymmetry < 0.08 and num_dark_regions > 5:
                predicted = "COVID-19"
            elif dark_ratio < 0.15 and edge_sharpness < 0.30:
                predicted = "Viral"
            else:
                if very_dark_ratio > 0.05 and edge_sharpness > 0.10:
                    predicted = "Bacterial"
                elif very_dark_ratio > 0.08 and bilateral_asymmetry < 0.10:
                    predicted = "COVID-19"
                elif dark_ratio < 0.18:
                    predicted = "Viral"
                else:
                    predicted = "Unknown"
            
            print(f"\nPredicted: {predicted} (Expected: BACTERIAL)")
