#!/usr/bin/env python3
"""
Test revised classification on real bacterial X-ray
"""
import cv2
import numpy as np
from pathlib import Path

# Find the bacterial X-ray image
test_images_dir = Path("data/pneumonia_xray/val/PNEUMONIA")
bacterial_images = list(test_images_dir.glob("*bacteria*.jpeg"))

if bacterial_images:
    bacterial_image = str(bacterial_images[0])
    print(f"Testing image: {bacterial_image}")
    
    # Load image
    img = cv2.imread(bacterial_image, cv2.IMREAD_GRAYSCALE)
    
    if img is not None:
        h, w = img.shape
        
        # Normalize
        img_norm = img.astype(float) / 255.0
        
        # 1. SPATIAL ASYMMETRY
        left_lung = img_norm[:, :w//2]
        right_lung = img_norm[:, w//2:]
        
        left_mean = np.mean(left_lung)
        right_mean = np.mean(right_lung)
        spatial_diff = abs(left_mean - right_mean)
        
        # 2. HETEROGENEITY
        img_std = np.std(img_norm)
        
        # 3. OPACITY
        global_mean = np.mean(img_norm)
        
        # 4. EDGE STRENGTH
        edges = cv2.Canny((img).astype(np.uint8), 50, 150)
        edge_count = np.sum(edges > 0)
        edge_density = edge_count / (h * w)
        
        # 5. CONSOLIDATION PATTERN
        hist, _ = np.histogram(img_norm, bins=256, range=(0, 1))
        very_dark_ratio = np.sum(hist[:64]) / np.sum(hist)
        
        print("\n=== REVISED FEATURES ===")
        print(f"Spatial Difference: {spatial_diff:.4f}")
        print(f"Std Deviation: {img_std:.4f}")
        print(f"Global Mean Intensity: {global_mean:.4f}")
        print(f"Edge Density (normalized): {edge_density:.6f}")
        print(f"Very Dark Ratio: {very_dark_ratio:.4f}")
        
        print("\n=== NEW THRESHOLDS ===")
        print(f"Bacterial (spatial_diff > 0.15 AND img_std > 0.15 AND edge_density > 0.008)?")
        print(f"  {spatial_diff > 0.15} AND {img_std > 0.15} AND {edge_density > 0.008}")
        print(f"COVID-19 (spatial_diff < 0.12 AND global_mean < 0.50 AND very_dark_ratio > 0.25)?")
        print(f"  {spatial_diff < 0.12} AND {global_mean < 0.50} AND {very_dark_ratio > 0.25}")
        print(f"Viral (spatial_diff < 0.14 AND global_mean < 0.55 AND edge_density < 0.010)?")
        print(f"  {spatial_diff < 0.14} AND {global_mean < 0.55} AND {edge_density < 0.010}")
        
        # Predict type
        if spatial_diff > 0.15 and img_std > 0.15 and edge_density > 0.008:
            predicted = "Bacterial"
        elif spatial_diff < 0.12 and global_mean < 0.50 and very_dark_ratio > 0.25:
            predicted = "COVID-19"
        elif spatial_diff < 0.14 and global_mean < 0.55 and edge_density < 0.010:
            predicted = "Viral"
        else:
            if spatial_diff > 0.12:
                predicted = "Bacterial"
            elif global_mean < 0.48 and spatial_diff < 0.13:
                predicted = "COVID-19"
            elif global_mean < 0.60:
                predicted = "Viral"
            else:
                predicted = "Unknown"
        
        print(f"\n=== PREDICTED: {predicted} ===")
        print(f"Expected: BACTERIAL")
        print(f"Match: {'✓' if predicted == 'Bacterial' else '✗'}")
else:
    print("No bacterial images found")
