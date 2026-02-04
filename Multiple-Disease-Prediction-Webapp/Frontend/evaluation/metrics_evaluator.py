"""
=============================================================================
PRODUCTION-GRADE METRICS EVALUATOR
=============================================================================
Academic-Grade Model Evaluation Framework for Capstone Project

This module provides comprehensive evaluation capabilities including:
- Classification reports (Precision, Recall, F1-Score, Support)
- Confusion matrices with professional visualizations
- ROC-AUC curves and Precision-Recall curves
- Performance comparison across models
- JSON and CSV report exports for documentation

Features:
✓ Handles real medical data
✓ Professional visualization with proper formatting
✓ Comprehensive metrics storage for capstone report
✓ Support for multiple model types (sklearn, keras, custom)
✓ Built-in logging and error handling

Author: Capstone Project Team
Generated: January 2026
=============================================================================
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, Any, Optional, Union

# Visualization
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# ML Metrics
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    auc,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionMetricsEvaluator:
    """
    Production-grade ML model evaluation framework for medical diagnosis systems.
    
    Designed for capstone project requirements:
    - Generates publication-quality confusion matrices
    - Stores metrics in reusable formats (JSON, CSV, PNG)
    - Creates academic documentation
    - Supports model comparison and performance tracking
    
    Usage:
        evaluator = ProductionMetricsEvaluator()
        results = evaluator.evaluate_model(
            y_true, y_pred, y_pred_proba,
            model_name="Dengue Prediction"
        )
    """
    
    def __init__(self, metrics_dir: Optional[str] = None, verbose: bool = True):
        """
        Initialize evaluator with output directory.
        
        Args:
            metrics_dir: Path to save outputs (default: ./metrics/)
            verbose: Print detailed output (default: True)
        """
        if metrics_dir is None:
            # Default to metrics folder at project root
            metrics_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'metrics'
            )
        
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # Create subdirectories
        self.dirs = {
            'confusion_matrices': self.metrics_dir / 'confusion_matrices',
            'reports': self.metrics_dir / 'classification_reports',
            'roc_curves': self.metrics_dir / 'roc_curves',
            'comparisons': self.metrics_dir / 'model_comparisons',
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self._log(f"✓ Evaluator initialized | Output: {self.metrics_dir}")
    
    def _log(self, message: str):
        """Conditional logging based on verbose flag."""
        if self.verbose:
            print(message)
        logger.info(message)
    
    def evaluate_model(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None,
        model_name: str = "Model",
        dataset_split: str = "test",
        class_names: Optional[list] = None,
        save_plots: bool = True,
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of classification model.
        
        Args:
            y_true: Ground truth labels (array-like)
            y_pred: Predicted labels (array-like)
            y_pred_proba: Prediction probabilities (array-like, optional)
            model_name: Name of the model (for file naming)
            dataset_split: 'train', 'test', 'validation'
            class_names: List of class names for reports
            save_plots: Save visualizations (default: True)
        
        Returns:
            Dictionary with comprehensive evaluation results:
            {
                'accuracy': float,
                'precision': float,
                'recall': float,
                'f1_score': float,
                'roc_auc': float or None,
                'classification_report': dict,
                'confusion_matrix': np.ndarray,
                'metrics_summary': dict,
                'files_saved': list,
            }
        """
        
        if class_names is None:
            class_names = ['Negative', 'Positive']
        
        results = {
            'model_name': model_name,
            'dataset_split': dataset_split,
            'timestamp': datetime.now().isoformat(),
            'files_saved': [],
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_model_name = model_name.lower().replace(' ', '_')
        
        # ===== HEADER =====
        self._log("\n" + "="*75)
        self._log(f"MODEL EVALUATION: {model_name.upper()}")
        self._log(f"Dataset Split: {dataset_split.upper()} | Samples: {len(y_true)}")
        self._log("="*75)
        
        # ===== 1. CLASSIFICATION REPORT =====
        self._log("\n📊 GENERATING CLASSIFICATION REPORT...")
        
        clf_report = classification_report(
            y_true, y_pred,
            target_names=class_names,
            output_dict=True,
            zero_division=0
        )
        
        results['classification_report'] = clf_report
        
        # Print classification report
        print("\n" + classification_report(
            y_true, y_pred,
            target_names=class_names,
            zero_division=0
        ))
        
        # Save as JSON
        report_json_path = self.dirs['reports'] / f"{safe_model_name}_{dataset_split}_{timestamp}.json"
        with open(report_json_path, 'w') as f:
            json.dump(clf_report, f, indent=4)
        results['files_saved'].append(str(report_json_path))
        self._log(f"✓ Classification report saved: {report_json_path.name}")
        
        # ===== 2. CONFUSION MATRIX =====
        self._log("\n📈 GENERATING CONFUSION MATRIX...")
        
        cm = confusion_matrix(y_true, y_pred)
        results['confusion_matrix'] = cm.tolist()
        
        if save_plots:
            cm_path = self._plot_confusion_matrix(
                cm, class_names, model_name,
                dataset_split, timestamp, safe_model_name
            )
            if cm_path:
                results['files_saved'].append(str(cm_path))
        
        # ===== 3. CORE METRICS =====
        self._log("\n✅ CALCULATING CORE METRICS...")
        
        accuracy = accuracy_score(y_true, y_pred)
        positive_class_name = class_names[1] if len(class_names) > 1 else class_names[0]
        
        precision = clf_report[positive_class_name]['precision']
        recall = clf_report[positive_class_name]['recall']
        f1 = clf_report[positive_class_name]['f1-score']
        
        results['accuracy'] = float(accuracy)
        results['precision'] = float(precision)
        results['recall'] = float(recall)
        results['f1_score'] = float(f1)
        
        # Print metrics summary
        self._log(f"\n  • Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        self._log(f"  • Precision: {precision:.4f}")
        self._log(f"  • Recall:    {recall:.4f}")
        self._log(f"  • F1-Score:  {f1:.4f}")
        
        # ===== 4. ROC-AUC (if probabilities provided) =====
        if y_pred_proba is not None:
            self._log("\n📊 CALCULATING ROC-AUC...")
            try:
                # Handle 2D probability arrays
                if y_pred_proba.ndim == 2:
                    if y_pred_proba.shape[1] == 2:
                        y_proba_binary = y_pred_proba[:, 1]
                    else:
                        y_proba_binary = np.max(y_pred_proba, axis=1)
                else:
                    y_proba_binary = y_pred_proba
                
                roc_auc = roc_auc_score(y_true, y_proba_binary)
                results['roc_auc'] = float(roc_auc)
                self._log(f"  • ROC-AUC: {roc_auc:.4f}")
                
                if save_plots:
                    roc_path = self._plot_roc_curve(
                        y_true, y_proba_binary, roc_auc,
                        model_name, dataset_split, timestamp, safe_model_name
                    )
                    if roc_path:
                        results['files_saved'].append(str(roc_path))
                        
            except Exception as e:
                self._log(f"⚠️  ROC-AUC calculation failed: {e}")
                results['roc_auc'] = None
        
        # ===== 5. METRICS SUMMARY FOR DOCUMENTATION =====
        metrics_summary = {
            'model_name': model_name,
            'dataset_split': dataset_split,
            'evaluation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_samples': int(len(y_true)),
            'metrics': {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(results.get('roc_auc', 0)) if results.get('roc_auc') else None,
            },
            'class_names': class_names,
            'confusion_matrix': cm.tolist(),
            'confusion_matrix_labels': {
                'actual_label': 'Actual',
                'predicted_label': 'Predicted',
            }
        }
        
        results['metrics_summary'] = metrics_summary
        
        # Save summary as JSON
        summary_path = self.dirs['reports'] / f"{safe_model_name}_{dataset_split}_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(metrics_summary, f, indent=4)
        results['files_saved'].append(str(summary_path))
        self._log(f"✓ Metrics summary saved: {summary_path.name}")
        
        self._log("\n" + "="*75 + "\n")
        
        return results
    
    def _plot_confusion_matrix(
        self, cm: np.ndarray, class_names: list,
        model_name: str, dataset_split: str,
        timestamp: str, safe_name: str
    ) -> Optional[Path]:
        """Generate and save professional confusion matrix visualization."""
        
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Heatmap
            sns.heatmap(
                cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names,
                cbar_kws={'label': 'Count'},
                ax=ax,
                annot_kws={'size': 14, 'weight': 'bold'},
            )
            
            ax.set_title(
                f"{model_name}\nConfusion Matrix ({dataset_split.upper()} SET)",
                fontsize=16, fontweight='bold', pad=20
            )
            ax.set_ylabel('Actual Label', fontsize=13, fontweight='bold')
            ax.set_xlabel('Predicted Label', fontsize=13, fontweight='bold')
            
            plt.tight_layout()
            
            cm_path = self.dirs['confusion_matrices'] / f"{safe_name}_{dataset_split}_cm_{timestamp}.png"
            plt.savefig(cm_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self._log(f"✓ Confusion matrix saved: {cm_path.name}")
            return cm_path
            
        except Exception as e:
            self._log(f"❌ Error saving confusion matrix: {e}")
            return None
    
    def _plot_roc_curve(
        self, y_true: np.ndarray, y_pred_proba: np.ndarray,
        roc_auc: float, model_name: str, dataset_split: str,
        timestamp: str, safe_name: str
    ) -> Optional[Path]:
        """Generate and save professional ROC curve visualization."""
        
        try:
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            ax.plot(fpr, tpr, color='darkorange', lw=2.5,
                   label=f'ROC Curve (AUC = {roc_auc:.4f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                   label='Random Classifier (AUC = 0.5000)')
            
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate', fontsize=13, fontweight='bold')
            ax.set_ylabel('True Positive Rate', fontsize=13, fontweight='bold')
            ax.set_title(f"{model_name}\nROC Curve ({dataset_split.upper()} SET)",
                        fontsize=16, fontweight='bold', pad=20)
            ax.legend(loc="lower right", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            roc_path = self.dirs['roc_curves'] / f"{safe_name}_{dataset_split}_roc_{timestamp}.png"
            plt.savefig(roc_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self._log(f"✓ ROC curve saved: {roc_path.name}")
            return roc_path
            
        except Exception as e:
            self._log(f"❌ Error saving ROC curve: {e}")
            return None
    
    def create_comparison_report(
        self, models_results: Dict[str, Dict],
        output_name: str = "model_comparison"
    ) -> Optional[Path]:
        """
        Create comprehensive comparison report across multiple models.
        
        Args:
            models_results: Dict with model names as keys, results as values
            output_name: Name for output CSV file
        
        Returns:
            Path to saved comparison report
        """
        
        self._log("\n" + "="*75)
        self._log("MULTI-MODEL PERFORMANCE COMPARISON")
        self._log("="*75)
        
        comparison_data = []
        
        for model_name, results in models_results.items():
            if 'metrics' in results or 'accuracy' in results:
                comparison_data.append({
                    'Model': model_name,
                    'Accuracy': f"{results.get('accuracy', 0):.4f}",
                    'Precision': f"{results.get('precision', 0):.4f}",
                    'Recall': f"{results.get('recall', 0):.4f}",
                    'F1-Score': f"{results.get('f1_score', 0):.4f}",
                    'ROC-AUC': f"{results.get('roc_auc', 0):.4f}" if results.get('roc_auc') else 'N/A',
                })
        
        if not comparison_data:
            self._log("⚠️  No results to compare")
            return None
        
        df = pd.DataFrame(comparison_data)
        print("\n" + df.to_string(index=False))
        
        # Save as CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.dirs['comparisons'] / f"{output_name}_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        
        self._log(f"\n✓ Comparison report saved: {csv_path.name}")
        
        return csv_path


if __name__ == "__main__":
    print("✓ Production Metrics Evaluator module loaded successfully")
