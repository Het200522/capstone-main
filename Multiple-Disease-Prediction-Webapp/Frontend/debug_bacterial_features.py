#!/usr/bin/env python3
"""
Debug script to analyze features from bacterial pneumonia X-ray
"""
import cv2
import numpy as np
from pathlib import Path

# Find the bacterial X-ray image
test_images_dir = Path(".")
bacterial_image = None

for img_file in test_images_dir.glob("*bacteria*.jpeg"):
    bacterial_image = str(img_file)
    break

if not bacterial_image:
    for img_file in test_images_dir.glob("**/*bacteria*.jpeg"):
        bacterial_image = str(img_file)
        break

if not bacterial_image:
    # Try with person80 name
    for img_file in test_images_dir.glob("*person80*.jpeg"):
        bacterial_image = str(img_file)
        break

if bacterial_image:
    print(f"Found image: {bacterial_image}")
    
    # Load image
    img = cv2.imread(bacterial_image, cv2.IMREAD_GRAYSCALE)
    
    if img is not None:
        h, w = img.shape
        
        # Calculate features
        left_lung = img[:, :w//2]
        right_lung = img[:, w//2:]
        
        left_brightness = np.mean(left_lung)
        right_brightness = np.mean(right_lung)
        bilateral_diff = abs(left_brightness - right_brightness)
        
        edges = cv2.Canny(img, 50, 150)
        edge_density = np.sum(edges) / (h * w)
        
        mean_intensity = np.mean(img) / 255.0
        
        hist, _ = np.histogram(img, bins=256, range=(0, 256))
        dark_pixels_very = np.sum(hist[:80]) / np.sum(hist)
        dark_pixels_mod = np.sum(hist[:140]) / np.sum(hist)
        
        print("\n=== FEATURE ANALYSIS ===")
        print(f"Bilateral Difference: {bilateral_diff:.2f}")
        print(f"Edge Density: {edge_density:.4f}")
        print(f"Mean Intensity (0-1): {mean_intensity:.3f}")
        print(f"Dark Pixels (<80): {dark_pixels_very:.3f}")
        print(f"Dark Pixels (<140): {dark_pixels_mod:.3f}")
        
        print("\n=== CURRENT THRESHOLDS ===")
        print(f"Bacterial: bilateral_diff > 22? {bilateral_diff > 22} AND (edge_density > 0.06 OR actual unilateral)")
        print(f"COVID-19: bilateral_diff < 12 AND mean_intensity < 0.62? {bilateral_diff < 12} AND {mean_intensity < 0.62}")
        print(f"Viral: bilateral_diff < 18 AND edge_density < 0.06? {bilateral_diff < 18} AND {edge_density < 0.06}")
        
        print("\n=== FALLBACK LOGIC ===")
        print(f"bilateral_diff > 15? {bilateral_diff > 15}")
        print(f"mean_intensity < 0.58 and bilateral_diff < 14? {mean_intensity < 0.58 and bilateral_diff < 14}")
        print(f"mean_intensity < 0.70? {mean_intensity < 0.70}")
        
        # Predict type
        if bilateral_diff > 22:
            predicted = "Bacterial"
        elif bilateral_diff < 12 and mean_intensity < 0.62:
            predicted = "COVID-19"
        elif bilateral_diff < 18 and edge_density < 0.06 and mean_intensity < 0.72:
            predicted = "Viral"
        else:
            if bilateral_diff > 15:
                predicted = "Bacterial"
            elif mean_intensity < 0.58 and bilateral_diff < 14:
                predicted = "COVID-19"
            elif mean_intensity < 0.70:
                predicted = "Viral"
            else:
                predicted = "Unknown"
        
        print(f"\n=== PREDICTED TYPE: {predicted} ===")
        print(f"(Expected: BACTERIAL)")
    else:
        print("Could not load image")
else:
    print("Could not find bacterial image file")
