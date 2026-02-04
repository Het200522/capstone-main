"""Debug pneumonia detection features"""
import numpy as np
import cv2
from PIL import Image

def debug_pneumonia_features(image: Image.Image):
    """Debug individual feature scores"""
    img_array = np.array(image.convert('L'))
    img_array = cv2.normalize(img_array, None, 0, 255, cv2.NORM_MINMAX)
    
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    img_enhanced = clahe.apply(img_array)
    
    # Feature 1: Consolidation
    _, dark_regions = cv2.threshold(img_enhanced, 110, 255, cv2.THRESH_BINARY_INV)
    consolidation_score = np.sum(dark_regions) / (img_array.shape[0] * img_array.shape[1] * 255)
    
    # Feature 2: Infiltrate
    infiltrate_score = min(np.std(img_enhanced) / 120.0, 1.0)
    
    # Feature 3: Edges
    edges = cv2.Canny(img_enhanced, 50, 150)
    edge_score = np.sum(edges) / (img_array.shape[0] * img_array.shape[1] * 255)
    
    # Feature 4: Histogram
    hist = cv2.calcHist([img_enhanced], [0], None, [256], [0, 256])
    hist_normalized = hist.ravel() / (hist.max() + 1e-8)
    bins = np.arange(256)
    mean_intensity = np.sum(bins * hist_normalized) / (np.sum(hist_normalized) + 1e-8)
    variance = np.sum(((bins - mean_intensity) ** 2) * hist_normalized) / (np.sum(hist_normalized) + 1e-8)
    if variance > 1.0:
        skewness = np.sum(((bins - mean_intensity) ** 3) * hist_normalized) / (np.sum(hist_normalized) * (variance ** 1.5) + 1e-8)
    else:
        skewness = 0
    histogram_score = max(0, min(-skewness / 18.0, 1.0))
    
    # Feature 5: Opacity
    h, w = img_array.shape
    lung_region = img_enhanced[h//4:3*h//4, w//4:3*w//4]
    lung_mean = np.mean(lung_region) / 255.0
    opacity_score = max(0, (0.55 - lung_mean) * 1.8) if lung_mean < 0.55 else 0.0
    
    # Feature 6: Texture
    laplacian = cv2.Laplacian(img_enhanced, cv2.CV_64F)
    texture_score = min(np.std(laplacian) / 150.0, 1.0)
    
    # Feature 7: Local Variance
    local_std = cv2.GaussianBlur(img_enhanced.astype(np.float32), (15, 15), 0)
    variance_score = min(np.std(local_std) / 80.0, 1.0)
    
    print(f"Consolidation: {consolidation_score:.4f}")
    print(f"Infiltrate:    {infiltrate_score:.4f}")
    print(f"Edges:         {edge_score:.4f}")
    print(f"Histogram:     {histogram_score:.4f}")
    print(f"Opacity:       {opacity_score:.4f}")
    print(f"Texture:       {texture_score:.4f}")
    print(f"Variance:      {variance_score:.4f}")
    print(f"Lung Mean:     {lung_mean:.4f}")
    
    base_score = (
        consolidation_score * 0.28 +
        edge_score * 0.22 +
        opacity_score * 0.18 +
        histogram_score * 0.14 +
        variance_score * 0.10 +
        infiltrate_score * 0.05 +
        texture_score * 0.03
    )
    
    print(f"\nBase Score:    {base_score:.4f}")
    
    pneumonia_score = 1 / (1 + np.exp(-3.5 * (base_score - 0.32)))
    print(f"Final Score:   {pneumonia_score:.4f}")
    print(f"Detected:      {pneumonia_score >= 0.50}")
    
    return pneumonia_score


if __name__ == "__main__":
    print("DEBUG: Simulated Pneumonia Pattern")
    print("=" * 50)
    img_pneu = np.full((512, 512), 200, dtype=np.uint8)
    img_pneu[150:300, 150:300] = np.random.randint(50, 100, (150, 150))
    img_pneu[200:350, 300:450] = np.random.randint(60, 110, (150, 150))
    debug_pneumonia_features(Image.fromarray(img_pneu))
