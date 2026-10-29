"""
End-to-End Pipeline Runner
MutationHunter: Genetic Variant Conflict Prioritization
Steps:
1. Topic Selection & Overview
2. Download & Preprocess ClinVar Dataset (65,188 variants)
3. Baseline Model Implementation (Random Forest & Logistic Regression)
4. Nature-Inspired Optimization (Genetic Algorithm & Particle Swarm Optimization)
5. Comparison & Benchmarking (Accuracy, F1, Precision, Recall, ROC-AUC, Latency)
6. Prototype Screenshot Capture
"""

import sys
import subprocess
from src.data_loader import download_and_preprocess_clinvar
from src.evaluate import run_evaluation

def main():
    print("=" * 70)
    print("MUTATIONHUNTER: END-TO-END PIPELINE")
    print("Nature-Inspired Detection of Genetic Classification Conflicts")
    print("=" * 70)
    
    # 1. Download & Preprocess
    print("\n>>> STEP 2 & 3: Downloading & Preprocessing ClinVar Conflicting Dataset...")
    download_and_preprocess_clinvar()
    
    # 2. Baseline & NIC Evaluation
    print("\n>>> STEP 4, 5 & 6: Training Baselines & NIC Optimizers (GA & PSO)...")
    run_evaluation()
    
    # 3. Prototype Screenshots
    print("\n>>> STEP 7: Capturing Prototype Screenshots...")
    try:
        subprocess.run([sys.executable, "capture_prototype_screenshots.py"], check=True)
    except Exception as e:
        print(f"Warning: Screenshot capture encountered: {e}")
        
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    main()
