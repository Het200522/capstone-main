"""
=============================================================================
MASTER EVALUATION SCRIPT - ALL DISEASE MODELS
=============================================================================
Comprehensive evaluation and reporting for capstone project.

This script:
1. Evaluates all 3 disease prediction models
2. Generates confusion matrices and metrics
3. Creates model comparison reports
4. Saves all results for capstone documentation

Execution: python evaluate_all_models.py
Output: metrics/ directory with organized reports and visualizations

Generated: January 2026
=============================================================================
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metrics_evaluator import ProductionMetricsEvaluator
from evaluate_dengue import evaluate_dengue_model
from evaluate_asthma import evaluate_asthma_model
from evaluate_pneumonia import evaluate_pneumonia_model


def main():
    """Run comprehensive evaluation for all models."""
    
    print("\n" + "="*80)
    print(" "*20 + "MULTIPLE DISEASE PREDICTION SYSTEM")
    print(" "*15 + "COMPREHENSIVE MODEL EVALUATION & REPORT GENERATION")
    print("="*80)
    
    all_results = {}
    evaluation_order = [
        ("Dengue", evaluate_dengue_model),
        ("Asthma", evaluate_asthma_model),
        ("Pneumonia", evaluate_pneumonia_model),
    ]
    
    # Evaluate each model
    for disease_name, evaluation_func in evaluation_order:
        print(f"\n\n{'#'*80}")
        print(f"# EVALUATING: {disease_name.upper()}")
        print(f"{'#'*80}")
        
        try:
            results = evaluation_func()
            all_results[disease_name] = results
            print(f"\n✅ {disease_name} evaluation successful!")
        except Exception as e:
            print(f"\n❌ {disease_name} evaluation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate comparison report
    if len(all_results) > 1:
        print("\n\n" + "="*80)
        print("GENERATING MULTI-MODEL COMPARISON REPORT")
        print("="*80)
        
        evaluator = ProductionMetricsEvaluator()
        
        # Prepare data for comparison
        comparison_data = {}
        for disease, results in all_results.items():
            comparison_data[f"{disease} Model"] = results
        
        # Create comparison
        evaluator.create_comparison_report(
            comparison_data,
            output_name="disease_models_comparison"
        )
    
    # Final summary
    print("\n\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    
    for disease, results in all_results.items():
        print(f"\n{disease.upper()}:")
        if 'accuracy' in results:
            print(f"  ✓ Accuracy:  {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
            print(f"  ✓ Precision: {results['precision']:.4f}")
            print(f"  ✓ Recall:    {results['recall']:.4f}")
            print(f"  ✓ F1-Score:  {results['f1_score']:.4f}")
            if results.get('roc_auc'):
                print(f"  ✓ ROC-AUC:   {results['roc_auc']:.4f}")
    
    print("\n" + "="*80)
    print("📊 All metrics, confusion matrices, and reports saved to: metrics/")
    print("="*80 + "\n")
    
    return all_results


if __name__ == "__main__":
    try:
        results = main()
        print("\n✅ EVALUATION COMPLETE - All results saved!")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
