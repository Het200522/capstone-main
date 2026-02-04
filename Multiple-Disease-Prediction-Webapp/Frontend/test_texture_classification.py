#!/usr/bin/env python3
"""
Test texture-based classification on bacterial X-rays
"""
import cv2
import numpy as np
from pathlib import Path

test_images_dir = Path("data/pneumonia_xray/val/PNEUMONIA")
bacterial_images = list(test_images_dir.glob("*bacteria*.jpeg"))[:3]

for img_path in bacterial_images:
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    
    if img is not None:
        h, w = img.shape
        img_norm = img.astype(float) / 255.0
        
        # Opacity measures
        global_mean = np.mean(img_norm)
        global_std = np.std(img_norm)
        
        # Local variance
        patch_size = 32
        variances = []
        for i in range(0, h - patch_size, patch_size):
            for j in range(0, w - patch_size, patch_size):
                patch = img_norm[i:i+patch_size, j:j+patch_size]
                variances.append(np.var(patch))
        
        mean_patch_var = np.mean(variances) if variances else 0
        
        # Symmetry
        left_lung = img_norm[:, :w//2]
        right_lung = img_norm[:, w//2:]
        left_mean = np.mean(left_lung)
        right_mean = np.mean(right_lung)
        left_std = np.std(left_lung)
        right_std = np.std(right_lung)
        
        asymmetry_mean = abs(left_mean - right_mean)
        asymmetry_std = abs(left_std - right_std)
        
        # Dark areas
        very_dark_pct = np.sum(img_norm < 0.25) / img_norm.size
        moderately_dark_pct = np.sum((img_norm >= 0.25) & (img_norm < 0.50)) / img_norm.size
        
        print(f"\n{'='*60}")
        print(f"Image: {img_path.name}")
        print(f"{'='*60}")
        print(f"Global Mean: {global_mean:.4f} | Global Std: {global_std:.4f}")
        print(f"Mean Patch Variance: {mean_patch_var:.6f}")
        print(f"Asymmetry (mean): {asymmetry_mean:.4f} | Asymmetry (std): {asymmetry_std:.4f}")
        print(f"Very Dark (<0.25): {very_dark_pct:.4f}")
        print(f"Moderately Dark (0.25-0.50): {moderately_dark_pct:.4f}")
        
        # Classify
        if global_std > 0.20:
            predicted = "Bacterial"
        elif (global_mean < 0.50 and global_std < 0.12 and asymmetry_mean < 0.08 and very_dark_pct > 0.20):
            predicted = "COVID-19"
        elif (global_mean > 0.50 and global_std < 0.18 and moderately_dark_pct < 0.18):
            predicted = "Viral"
        else:
            if global_std > 0.18:
                predicted = "Bacterial"
            elif global_mean < 0.48 and global_std < 0.13:
                predicted = "COVID-19"
            else:
                predicted = "Viral"
        
        print(f"\nPredicted: {predicted} (Expected: BACTERIAL)")
