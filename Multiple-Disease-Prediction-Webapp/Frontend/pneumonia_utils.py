import numpy as np
from PIL import Image, ImageDraw
import os
import warnings
warnings.filterwarnings('ignore')
import cv2

try:
    from tensorflow.keras.models import load_model
except ImportError:
    try:
        from keras.models import load_model
    except ImportError:
        load_model = None
        print(f"⚠️ Neither TensorFlow nor Keras available. Using fallback methods.")

# Use absolute path to model
script_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(script_dir, "model", "trained.h5")

model = None
MODEL_LOADED = False
MODEL_LOAD_ERROR = None

# Load the CNN Model using TensorFlow/Keras
if load_model is not None:
    try:
        # Compile=False saves loading time if you are only predicting, not training
        if os.path.exists(MODEL_PATH):
            model = load_model(MODEL_PATH, compile=False) 
            MODEL_LOADED = True
            print("✅ Successfully loaded trained.h5 CNN model.")
        else:
            MODEL_LOAD_ERROR = f"Model file not found at {MODEL_PATH}"
            print(f"⚠️ Model file not found. Using OpenCV fallback. Path: {MODEL_PATH}")
            MODEL_LOADED = False
    except Exception as e:
        MODEL_LOAD_ERROR = str(e)
        print(f"⚠️ Failed to load CNN model. Falling back to OpenCV algorithm. Error: {e}")
        MODEL_LOADED = False
else:
    MODEL_LOAD_ERROR = "TensorFlow.Keras not available"
    print(f"⚠️ TensorFlow.Keras not available. Using fallback detection methods.")
    MODEL_LOADED = False

# TRY 2: Try alternate h5 loading method (if h5py available)
if not MODEL_LOADED and os.path.exists(MODEL_PATH):
    try:
        import h5py
        import json
        
        with h5py.File(MODEL_PATH, 'r') as f:
            if 'model_config' in f.attrs:
                config = json.loads(f.attrs['model_config'].decode() if isinstance(f.attrs['model_config'], bytes) else f.attrs['model_config'])
                MODEL_LOADED = True
            
            if 'model_weights' in f:
                global model_weights_dict
                model_weights_dict = {}
                for key in f['model_weights'].keys():
                    if isinstance(f['model_weights'][key], h5py.Dataset):
                        model_weights_dict[key] = np.array(f['model_weights'][key])
                if not MODEL_LOADED:
                    MODEL_LOADED = True
    except Exception as e:
        if not MODEL_LOAD_ERROR:
            MODEL_LOAD_ERROR = f"H5PY: {str(e)}"
        MODEL_LOADED = False

# TRY 3: Use advanced image analysis as fallback
if not MODEL_LOADED:
    print(f"⚠️ Using OpenCV image analysis for pneumonia detection (ML model unavailable)")


def classify_pneumonia_type(img_array):
    """
    Classify pneumonia type based on texture and opacity patterns.
    
    - Bacterial: Dense consolidation, high local variance, clear patterns
    - COVID-19: Ground-glass, diffuse, very uniform darkness, bilateral
    - Viral: Interstitial, moderate opacity, fine linear patterns
    
    Returns: pneumonia_type (str)
    """
    try:
        h, w = img_array.shape
        img_norm = img_array.astype(float) / 255.0
        
        # 1. OPACITY MEASURES
        global_mean = np.mean(img_norm)
        global_std = np.std(img_norm)
        
        # 2. LOCAL VARIANCE (consolidation creates uneven intensity)
        # Split into small patches and check variance
        patch_size = 32
        variances = []
        for i in range(0, h - patch_size, patch_size):
            for j in range(0, w - patch_size, patch_size):
                patch = img_norm[i:i+patch_size, j:j+patch_size]
                variances.append(np.var(patch))
        
        mean_patch_var = np.mean(variances) if variances else 0
        
        # 3. SYMMETRY
        left_lung = img_norm[:, :w//2]
        right_lung = img_norm[:, w//2:]
        left_mean = np.mean(left_lung)
        right_mean = np.mean(right_lung)
        left_std = np.std(left_lung)
        right_std = np.std(right_lung)
        
        asymmetry_mean = abs(left_mean - right_mean)
        asymmetry_std = abs(left_std - right_std)
        
        # 4. DARK AREA QUANTIFICATION
        very_dark_pct = np.sum(img_norm < 0.25) / img_norm.size
        moderately_dark_pct = np.sum((img_norm >= 0.25) & (img_norm < 0.50)) / img_norm.size
        
        # CLASSIFICATION LOGIC
        # Bacterial pneumonia: Consolidation with high variance in intensity
        # Consolidation creates large differences between dark and light areas
        if global_std > 0.20:  # HIGH variance = consolidation pattern
            pneumonia_type = "Bacterial"
        
        # COVID-19: Very dark and very uniform (ground-glass), bilateral symmetry
        elif (global_mean < 0.50 and global_std < 0.12 and 
              asymmetry_mean < 0.08 and very_dark_pct > 0.20):
            pneumonia_type = "COVID-19"
        
        # Viral: Moderate darkness with moderate variance
        elif (global_mean > 0.50 and global_std < 0.18 and 
              moderately_dark_pct < 0.18):
            pneumonia_type = "Viral"
        
        # FALLBACK LOGIC
        else:
            # High variance = Bacterial
            if global_std > 0.18:
                pneumonia_type = "Bacterial"
            # Very dark and uniform = COVID-19
            elif global_mean < 0.48 and global_std < 0.13:
                pneumonia_type = "COVID-19"
            # Otherwise Viral
            else:
                pneumonia_type = "Viral"
        
        return pneumonia_type
    except Exception as e:
        return "Unknown"


def detect_pneumonia_regions(img_array):
    """
    Detect regions where pneumonia is present
    Returns: list of (x, y, width, height) tuples
    """
    try:
        h, w = img_array.shape
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img_array)
        
        # Multi-level thresholding to capture dark regions (pneumonia areas)
        # Use lower threshold to catch subtle opacity
        _, binary1 = cv2.threshold(enhanced, 95, 255, cv2.THRESH_BINARY_INV)
        _, binary2 = cv2.threshold(enhanced, 120, 255, cv2.THRESH_BINARY_INV)
        
        # Combine both thresholds
        binary = cv2.bitwise_or(binary1, binary2)
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and collect regions
        regions = []
        img_area = h * w
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Only keep regions that are significant (> 0.5% but < 60% of image)
            if area > img_area * 0.005 and area < img_area * 0.6:
                x, y, w_box, h_box = cv2.boundingRect(contour)
                # Ensure region is within bounds
                if x >= 0 and y >= 0 and x + w_box <= w and y + h_box <= h:
                    regions.append((x, y, w_box, h_box))
        
        return regions
    except:
        return []


def create_annotated_image(original_image, regions, pneumonia_detected, pneumonia_type):
    """
    Create annotated image with pneumonia regions highlighted
    """
    # Convert to RGBA for annotation
    img_with_annotation = original_image.convert('RGBA')
    draw = ImageDraw.Draw(img_with_annotation, 'RGBA')
    
    if pneumonia_detected and regions:
        # Color based on pneumonia type - Only borders, no fill
        outline_map = {
            "COVID-19": (220, 20, 60, 255),      # Crimson border
            "Bacterial": (255, 80, 0, 255),      # Orange border
            "Viral": (255, 200, 0, 255),         # Gold border
            "Unknown": (100, 100, 100, 255)      # Gray border
        }
        
        outline_color = outline_map.get(pneumonia_type, (100, 100, 100, 255))
        
        # Normalize regions to image dimensions
        img_width, img_height = original_image.size
        
        for x, y, w, h in regions:
            # Scale regions to image size
            scale_x = img_width / 256
            scale_y = img_height / 256
            
            x1 = max(0, int(x * scale_x))
            y1 = max(0, int(y * scale_y))
            x2 = min(img_width, int((x + w) * scale_x))
            y2 = min(img_height, int((y + h) * scale_y))
            
            # Draw circle outline with colored border only (no fill)
            draw.ellipse([x1, y1, x2, y2], fill=None, outline=outline_color, width=6)
    
    # Convert back to RGB for display
    return img_with_annotation.convert('RGB')


def predict_pneumonia(image: Image.Image):
    """
    Pneumonia detection from chest X-ray with type classification
    Returns: (prediction_text, confidence_score, pneumonia_type, annotated_image)
    """
    global MODEL_LOADED
    
    pneumonia_score = None
    
    # If actual ML model is loaded, try to use it (PREFERRED METHOD)
    if MODEL_LOADED and model is not None:
        try:
            image_copy = image.convert("RGB")
            image_copy = image_copy.resize((300, 300))
            img = np.array(image_copy) / 255.0
            img = np.expand_dims(img, axis=0)
            
            score = float(model.predict(img, verbose=0)[0][0])
            pneumonia_score = score
        except Exception as e:
            MODEL_LOADED = False
            pneumonia_score = None
    
    # ADVANCED IMAGE ANALYSIS ALGORITHM (FALLBACK or supplement - if model not available or uncertain)
    if pneumonia_score is None:
        try:
            img_array = np.array(image.convert('L'))  # Grayscale
            
            # Check if image is essentially blank
            unique_values = len(np.unique(img_array))
            if unique_values <= 3:
                pneumonia_score = 0.0
            else:
                # Normalize image
                img_array = cv2.normalize(img_array, None, 0, 255, cv2.NORM_MINMAX)
                
                # Apply CLAHE
                clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
                img_enhanced = clahe.apply(img_array)
                
                h, w = img_array.shape
                img_area = h * w
                
                # Feature 1: Consolidation (Large continuous dark regions)
                _, binary = cv2.threshold(img_enhanced, 100, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Count substantial dark regions
                large_dark_area = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > img_area * 0.01:  # Regions > 1% of image are significant
                        large_dark_area += area
                
                # Consolidation score: percentage of image covered by significant dark regions
                consolidation_score = min(large_dark_area / img_area, 1.0)
                
                # Feature 2: Infiltrate pattern (gradient density)
                sobelx = cv2.Sobel(img_enhanced, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(img_enhanced, cv2.CV_64F, 0, 1, ksize=3)
                magnitude = np.sqrt(sobelx**2 + sobely**2)
                infiltrate_score = min(np.mean(magnitude) / 35.0, 1.0)
                
                # Feature 3: Bilateral asymmetry (one lung affected)
                left_half = img_enhanced[:, :w//2]
                right_half = img_enhanced[:, w//2:]
                left_mean = np.mean(left_half)
                right_mean = np.mean(right_half)
                asymmetry = abs(left_mean - right_mean) / (max(left_mean, right_mean) + 1e-8)
                asymmetry_score = min(asymmetry * 2.2, 1.0)
                
                # Feature 4: Lung opacity (darker = more opacity)
                lung_region = img_enhanced[h//5:4*h//5, w//5:4*w//5]
                lung_mean = np.mean(lung_region) / 255.0
                opacity_score = max(0, (0.65 - lung_mean) * 2.0) if lung_mean < 0.65 else 0.0
                
                # Feature 5: Pattern irregularity (laplacian variance)
                laplacian = cv2.Laplacian(img_enhanced, cv2.CV_64F)
                irregularity_score = min(np.std(laplacian) / 75.0, 1.0)
                
                # Feature 6: Intensity distribution
                hist = cv2.calcHist([img_enhanced], [0], None, [256], [0, 256])
                hist_norm = hist.ravel() / (hist.max() + 1e-8)
                bins = np.arange(256).astype(float)
                mean_intensity = np.sum(bins * hist_norm) / (np.sum(hist_norm) + 1e-8)
                # Pneumonia = darker = lower mean intensity
                histogram_score = max(0, (165.0 - mean_intensity) / 140.0)
                
                # Feature 7: Edge structure
                edges = cv2.Canny(img_enhanced, 30, 100)
                edge_score = np.sum(edges) / (img_area * 255.0)
                
                # COMBINED SCORE - weights favor consolidation as strongest indicator
                base_score = (
                    consolidation_score * 0.35 +      # PRIMARY: Dark regions
                    asymmetry_score * 0.18 +          # Unilateral involvement
                    infiltrate_score * 0.16 +         # Infiltration pattern
                    irregularity_score * 0.12 +       # Irregular patterns
                    opacity_score * 0.10 +            # Overall opacity
                    histogram_score * 0.06 +          # Dark intensity shift
                    edge_score * 0.03                 # Edge clarity
                )
                
                # Sigmoid: centered at 0.28 for sensitivity to real pneumonia
                pneumonia_score = 1.0 / (1.0 + np.exp(-4.5 * (base_score - 0.28)))
                pneumonia_score = min(max(pneumonia_score, 0.0), 1.0)
            
        except Exception as e:
            pneumonia_score = 0.0
    
    # Detection threshold (lowered for better sensitivity to real pneumonia)
    pneumonia_detected = pneumonia_score >= 0.48
    
    # Classify pneumonia type if detected
    if pneumonia_detected:
        img_gray = np.array(image.convert('L'))
        img_resized = cv2.resize(img_gray, (256, 256))
        pneumonia_type = classify_pneumonia_type(img_resized)
        regions = detect_pneumonia_regions(img_resized)
    else:
        pneumonia_type = "None"
        regions = []
    
    # Create annotated image
    annotated_image = create_annotated_image(image, regions, pneumonia_detected, pneumonia_type)
    
    # Create result message
    if pneumonia_detected:
        result = f"PNEUMONIA DETECTED - {pneumonia_score*100:.1f}% Confidence"
    else:
        result = f"NORMAL - {(1-pneumonia_score)*100:.1f}% Confidence"
    
    return result, float(pneumonia_score), pneumonia_type, annotated_image