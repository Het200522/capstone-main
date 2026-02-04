#!/usr/bin/env python3
"""Test pneumonia detection with fresh imports"""
import sys
import importlib

# Clean import
if 'pneumonia_utils' in sys.modules:
    del sys.modules['pneumonia_utils']

from pneumonia_utils import predict_pneumonia, MODEL_LOADED
from PIL import Image
import numpy as np

print('PNEUMONIA DETECTION TEST')
print('=' * 65)
print(f'Model Loaded: {MODEL_LOADED}')
print()

tests = [
    ("Consolidation (15% dark)", lambda: np.full((512, 512), 220, dtype=np.uint8)),
    ("Normal noise", lambda: np.random.randint(160, 200, (512, 512), dtype=np.uint8)),
    ("Asymmetry", lambda: (
        lambda img: (
            img.__setitem__((slice(80, 350), slice(40, 200)), np.random.randint(50, 95, (270, 160))),
            img
        )[1]
    )(np.full((512, 512), 200, dtype=np.uint8))),
    ("Blank", lambda: np.full((512, 512), 200, dtype=np.uint8)),
]

# Fix consolidation test
img_consol = np.full((512, 512), 220, dtype=np.uint8)
img_consol[100:300, 100:200] = 50
img_consol[100:300, 300:400] = 60

img_asym = np.full((512, 512), 200, dtype=np.uint8)
img_asym[80:350, 40:200] = np.random.randint(50, 95, (270, 160))

tests_fixed = [
    ("Consolidation", img_consol),
    ("Normal noise", np.random.randint(160, 200, (512, 512), dtype=np.uint8)),
    ("Asymmetry", img_asym),
    ("Blank", np.full((512, 512), 200, dtype=np.uint8)),
]

for name, img_array in tests_fixed:
    result, conf, ptype, _ = predict_pneumonia(Image.fromarray(img_array))
    status = "DETECTED" if conf >= 0.50 else "NORMAL"
    print(f"{name:20} -> {status:10} ({conf:.3f})")

print('=' * 65)
