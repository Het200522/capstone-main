#!/usr/bin/env python3
"""Test pneumonia type classification"""
import numpy as np
import cv2
import sys
sys.path.insert(0, '.')

from pneumonia_utils import classify_pneumonia_type

print('PNEUMONIA TYPE CLASSIFICATION TEST')
print('=' * 60)

# Test 1: Bacterial (unilateral, dark consolidation)
img_bacterial = np.full((256, 256), 180, dtype=np.uint8)
img_bacterial[50:200, 30:120] = np.random.randint(40, 90, (150, 90))
ptype = classify_pneumonia_type(img_bacterial)
print(f'1. Unilateral dark:     {ptype} (Expected: Bacterial)')

# Test 2: COVID-19 (bilateral, symmetric, dark)
img_covid = np.full((256, 256), 180, dtype=np.uint8)
img_covid[50:200, 30:120] = np.random.randint(50, 95, (150, 90))
img_covid[50:200, 136:226] = np.random.randint(50, 95, (150, 90))
ptype = classify_pneumonia_type(img_covid)
print(f'2. Bilateral symmetric: {ptype} (Expected: COVID-19)')

# Test 3: Viral (bilateral, light, diffuse)
img_viral = np.full((256, 256), 190, dtype=np.uint8)
img_viral[30:180, :] = np.random.randint(140, 180, (150, 256))
ptype = classify_pneumonia_type(img_viral)
print(f'3. Bilateral diffuse:   {ptype} (Expected: Viral)')

# Test 4: Random
img_random = np.random.randint(150, 200, (256, 256), dtype=np.uint8)
ptype = classify_pneumonia_type(img_random)
print(f'4. Random:              {ptype}')

print('=' * 60)
