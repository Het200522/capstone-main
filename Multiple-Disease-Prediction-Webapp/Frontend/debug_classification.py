#!/usr/bin/env python3
"""Debug pneumonia type classification"""
import numpy as np
import cv2

def debug_classify(img_array, test_name):
    print(f'\n{test_name}')
    print('-' * 40)
    
    h, w = img_array.shape
    
    left_lung = img_array[:, :w//2]
    right_lung = img_array[:, w//2:]
    
    left_brightness = np.mean(left_lung)
    right_brightness = np.mean(right_lung)
    bilateral_diff = abs(left_brightness - right_brightness)
    
    edges = cv2.Canny(img_array, 50, 150)
    edge_density = np.sum(edges) / (h * w)
    
    hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
    dark_pixels = np.sum(hist[:100]) / np.sum(hist)
    total_dark_pixels = np.sum(hist[:120]) / np.sum(hist)
    
    print(f'Left brightness:     {left_brightness:.2f}')
    print(f'Right brightness:    {right_brightness:.2f}')
    print(f'Bilateral diff:      {bilateral_diff:.2f}')
    print(f'Edge density:        {edge_density:.4f}')
    print(f'Dark pixels (<100):  {dark_pixels:.4f}')
    print(f'Dark pixels (<120):  {total_dark_pixels:.4f}')
    
    print('\nCondition checks:')
    print(f'  Bacterial (diff>20, dark>0.32, edges>0.12): {bilateral_diff > 20 and dark_pixels > 0.32 and edge_density > 0.12}')
    print(f'  COVID (diff<15, dark120>0.38): {bilateral_diff < 15 and total_dark_pixels > 0.38}')
    print(f'  Viral (diff<18, dark>0.25, edges<0.10): {bilateral_diff < 18 and dark_pixels > 0.25 and edge_density < 0.10}')

# Test 1: Bacterial
img_bacterial = np.full((256, 256), 180, dtype=np.uint8)
img_bacterial[50:200, 30:120] = np.random.randint(40, 90, (150, 90))
debug_classify(img_bacterial, 'Test 1: Bacterial (unilateral)')

# Test 3: Viral
img_viral = np.full((256, 256), 190, dtype=np.uint8)
img_viral[30:180, :] = np.random.randint(140, 180, (150, 256))
debug_classify(img_viral, 'Test 3: Viral (bilateral diffuse)')
