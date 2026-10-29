"""
Comprehensive Evaluation & Benchmarking Module for ClinVar
MutationHunter: Genetic Variant Conflicting Classification
Comparison: Baseline Models vs Nature-Inspired Computing (GA and PSO)
Metrics: Accuracy, F1-Score (macro/weighted), Precision, Recall, ROC-AUC, Feature Count, Runtime
"""

import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from baseline_model import BaselineModel
from nic_optimizer import GeneticAlgorithmFeatureSelector, ParticleSwarmFeatureSelector

def run_evaluation(data_dir="data", output_dir="results", plots_dir="static/plots", random_state=42):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. Load data
    train_path = os.path.join(data_dir, "processed", "train.csv")
    test_path = os.path.join(data_dir, "processed", "test.csv")
    ga_sample_path = os.path.join(data_dir, "processed", "train_ga_sample.csv")
    meta_path = os.path.join(data_dir, "processed", "features_meta.json")
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    sample_df = pd.read_csv(ga_sample_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    feature_names = meta["all_feature_names"]
    
    X_train_full = train_df[feature_names]
    y_train_full = train_df["CLASS"]
    X_test_full = test_df[feature_names]
    y_test_full = test_df["CLASS"]
    
    X_search = sample_df[feature_names]
    y_search = sample_df["CLASS"]
    
    print(f"Loaded ClinVar Dataset: {len(train_df)} train variants, {len(test_df)} test variants across {len(feature_names)} features.")
    print(f"NIC Optimization Search Cohort: {len(sample_df)} stratified variants.")
    
    results = {}
    
    # =========================================================================
    # Step 4: Baseline Models
    # =========================================================================
    print("\n--- Running Step 4: Baseline Models on ClinVar (30 Features) ---")
    print("[1/2] Training Random Forest Baseline...")
    rf_baseline = BaselineModel(classifier_type="rf", random_state=random_state)
    rf_metrics = rf_baseline.fit_and_evaluate(X_train_full, y_train_full, X_test_full, y_test_full, feature_names)
    results["rf_baseline"] = rf_metrics
    print(f"      Accuracy: {rf_metrics['test_accuracy']:.4f} | F1: {rf_metrics['test_f1_macro']:.4f} | Training: {rf_metrics['training_time_sec']:.2f}s")
    
    print("[2/2] Training Logistic Regression Baseline...")
    lr_baseline = BaselineModel(classifier_type="lr", random_state=random_state)
    lr_metrics = lr_baseline.fit_and_evaluate(X_train_full, y_train_full, X_test_full, y_test_full, feature_names)
    results["lr_baseline"] = lr_metrics
    print(f"      Accuracy: {lr_metrics['test_accuracy']:.4f} | F1: {lr_metrics['test_f1_macro']:.4f} | Training: {lr_metrics['training_time_sec']:.2f}s")
    
    # =========================================================================
    # Step 5: Nature-Inspired Computing Algorithms (GA & PSO)
    # =========================================================================
    print("\n--- Running Step 5: Nature-Inspired Computing (NIC) Algorithms ---")
    print("[1/2] Running Genetic Algorithm (GA) Feature Selector (20 Generations)...")
    ga_selector = GeneticAlgorithmFeatureSelector(
        population_size=30,
        generations=20,
        crossover_rate=0.85,
        mutation_rate=0.04,
        alpha=0.85,
        random_state=random_state
    )
    ga_opt_time = ga_selector.fit(X_search, y_search, feature_names)
    ga_metrics = ga_selector.evaluate_on_full_test(X_train_full, y_train_full, X_test_full, y_test_full, feature_names)
    ga_metrics["optimization_runtime_sec"] = ga_opt_time
    ga_metrics["total_runtime_sec"] = ga_opt_time + ga_metrics["training_time_sec"]
    results["ga_optimized"] = ga_metrics
    print(f"      Optimization Search Time: {ga_opt_time:.2f}s")
    print(f"      Selected Biomarkers: {ga_metrics['feature_count']} / {len(feature_names)} features ({ga_metrics['reduction_percentage']}% reduction)")
    print(f"      GA Test Accuracy: {ga_metrics['test_accuracy']:.4f} | F1: {ga_metrics['test_f1_macro']:.4f} | ROC-AUC: {ga_metrics['roc_auc']:.4f}")
    print(f"      Key Biomarkers: {', '.join(ga_metrics['selected_features'][:6])}...")
    
    print("\n[2/2] Running Binary Particle Swarm Optimization (BPSO)...")
    pso_selector = ParticleSwarmFeatureSelector(
        num_particles=20,
        iterations=15,
        alpha=0.85,
        random_state=random_state
    )
    pso_opt_time = pso_selector.fit(X_search, y_search, feature_names)
    pso_metrics = pso_selector.evaluate_on_full_test(X_train_full, y_train_full, X_test_full, y_test_full, feature_names)
    pso_metrics["optimization_runtime_sec"] = pso_opt_time
    pso_metrics["total_runtime_sec"] = pso_opt_time + pso_metrics["training_time_sec"]
    results["pso_optimized"] = pso_metrics
    print(f"      Optimization Search Time: {pso_opt_time:.2f}s")
    print(f"      Selected Biomarkers: {pso_metrics['feature_count']} / {len(feature_names)} features ({pso_metrics['reduction_percentage']}% reduction)")
    print(f"      PSO Test Accuracy: {pso_metrics['test_accuracy']:.4f} | F1: {pso_metrics['test_f1_macro']:.4f} | ROC-AUC: {pso_metrics['roc_auc']:.4f}")
    
    # =========================================================================
    # Step 6: Comparison Table
    # =========================================================================
    print("\n--- Running Step 6: Quantitative Comparison ---")
    comp_data = [
        {
            "Method": "Random Forest Baseline",
            "Nature-Inspired": "No",
            "Features Used": rf_metrics["feature_count"],
            "Feature Reduction (%)": "0.0%",
            "Accuracy": f"{rf_metrics['test_accuracy']:.4f}",
            "F1-Score (Macro)": f"{rf_metrics['test_f1_macro']:.4f}",
            "Precision": f"{rf_metrics['test_precision']:.4f}",
            "Recall": f"{rf_metrics['test_recall']:.4f}",
            "ROC-AUC": f"{rf_metrics['roc_auc']:.4f}",
            "Training Time (s)": f"{rf_metrics['training_time_sec']:.3f}",
            "Total Pipeline Runtime (s)": f"{rf_metrics['total_runtime_sec']:.3f}",
            "Inference Latency (ms)": f"{rf_metrics['inference_time_sec']*1000:.2f}"
        },
        {
            "Method": "Logistic Regression Baseline",
            "Nature-Inspired": "No",
            "Features Used": lr_metrics["feature_count"],
            "Feature Reduction (%)": "0.0%",
            "Accuracy": f"{lr_metrics['test_accuracy']:.4f}",
            "F1-Score (Macro)": f"{lr_metrics['test_f1_macro']:.4f}",
            "Precision": f"{lr_metrics['test_precision']:.4f}",
            "Recall": f"{lr_metrics['test_recall']:.4f}",
            "ROC-AUC": f"{lr_metrics['roc_auc']:.4f}",
            "Training Time (s)": f"{lr_metrics['training_time_sec']:.3f}",
            "Total Pipeline Runtime (s)": f"{lr_metrics['total_runtime_sec']:.3f}",
            "Inference Latency (ms)": f"{lr_metrics['inference_time_sec']*1000:.2f}"
        },
        {
            "Method": "Genetic Algorithm (GA) + RF",
            "Nature-Inspired": "Yes (Darwinian Evolution)",
            "Features Used": ga_metrics["feature_count"],
            "Feature Reduction (%)": f"{ga_metrics['reduction_percentage']:.1f}%",
            "Accuracy": f"{ga_metrics['test_accuracy']:.4f}",
            "F1-Score (Macro)": f"{ga_metrics['test_f1_macro']:.4f}",
            "Precision": f"{ga_metrics['test_precision']:.4f}",
            "Recall": f"{ga_metrics['test_recall']:.4f}",
            "ROC-AUC": f"{ga_metrics['roc_auc']:.4f}",
            "Training Time (s)": f"{ga_metrics['training_time_sec']:.3f}",
            "Total Pipeline Runtime (s)": f"{ga_metrics['total_runtime_sec']:.3f}",
            "Inference Latency (ms)": f"{ga_metrics['inference_time_sec']*1000:.2f}"
        },
        {
            "Method": "Particle Swarm (PSO) + RF",
            "Nature-Inspired": "Yes (Swarm Intelligence)",
            "Features Used": pso_metrics["feature_count"],
            "Feature Reduction (%)": f"{pso_metrics['reduction_percentage']:.1f}%",
            "Accuracy": f"{pso_metrics['test_accuracy']:.4f}",
            "F1-Score (Macro)": f"{pso_metrics['test_f1_macro']:.4f}",
            "Precision": f"{pso_metrics['test_precision']:.4f}",
            "Recall": f"{pso_metrics['test_recall']:.4f}",
            "ROC-AUC": f"{pso_metrics['roc_auc']:.4f}",
            "Training Time (s)": f"{pso_metrics['training_time_sec']:.3f}",
            "Total Pipeline Runtime (s)": f"{pso_metrics['total_runtime_sec']:.3f}",
            "Inference Latency (ms)": f"{pso_metrics['inference_time_sec']*1000:.2f}"
        }
    ]
    comp_df = pd.DataFrame(comp_data)
    csv_out = os.path.join(output_dir, "comparison_table.csv")
    comp_df.to_csv(csv_out, index=False)
    print("\nComparison Table:")
    print(comp_df.to_string(index=False))
    
    results_json = os.path.join(output_dir, "benchmark_results.json")
    with open(results_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved benchmark results to '{results_json}' and '{csv_out}'.")
    
    # =========================================================================
    # Step 6 Visualizations: Confusion Matrices, ROC Curves, GA Convergence
    # =========================================================================
    print("\nGenerating evaluation visualizations in 'static/plots/'...")
    
    # 1. Confusion Matrices Comparison
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    labels = ["Consistent (0)", "Conflicting (1)"]
    
    cm_models = [
        ("Baseline (Random Forest - 30 Feats)", rf_metrics["confusion_matrix"]),
        (f"NIC: Genetic Algorithm ({ga_metrics['feature_count']} Feats)", ga_metrics["confusion_matrix"]),
        (f"NIC: Particle Swarm ({pso_metrics['feature_count']} Feats)", pso_metrics["confusion_matrix"])
    ]
    
    for ax, (title, cm) in zip(axes, cm_models):
        sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", cbar=False, ax=ax,
                    xticklabels=labels, yticklabels=labels, annot_kws={"size": 13, "weight": "bold"})
        ax.set_title(title, fontsize=12, pad=10, weight="bold")
        ax.set_xlabel("Predicted ClinVar Classification", fontsize=11)
        ax.set_ylabel("True Clinical Label", fontsize=11)
        
    plt.tight_layout()
    cm_path = os.path.join(plots_dir, "confusion_matrices.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"      Saved {cm_path}")
    
    # 2. ROC Curves Comparison
    plt.figure(figsize=(8, 6))
    plt.plot(rf_metrics["roc_curve"]["fpr"], rf_metrics["roc_curve"]["tpr"], 
             label=f"Baseline RF (AUC = {rf_metrics['roc_auc']:.3f}, 30 Feats)", color="#dc3545", lw=2.2, linestyle="--")
    plt.plot(ga_metrics["roc_curve"]["fpr"], ga_metrics["roc_curve"]["tpr"], 
             label=f"NIC: GA + RF (AUC = {ga_metrics['roc_auc']:.3f}, {ga_metrics['feature_count']} Feats)", color="#0d6efd", lw=2.5)
    plt.plot(pso_metrics["roc_curve"]["fpr"], pso_metrics["roc_curve"]["tpr"], 
             label=f"NIC: PSO + RF (AUC = {pso_metrics['roc_auc']:.3f}, {pso_metrics['feature_count']} Feats)", color="#198754", lw=2.2)
    plt.plot([0, 1], [0, 1], "k:", lw=1.2, label="Random Guess (AUC = 0.500)")
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
    plt.ylabel("True Positive Rate (Sensitivity)", fontsize=12)
    plt.title("ClinVar Variant Conflict Prediction: ROC Curves", fontsize=14, weight="bold", pad=12)
    plt.legend(loc="lower right", fontsize=10, frameon=True)
    plt.grid(True, alpha=0.3)
    roc_path = os.path.join(plots_dir, "roc_curves.png")
    plt.savefig(roc_path, dpi=200)
    plt.close()
    print(f"      Saved {roc_path}")
    
    # 3. GA Convergence History
    ga_hist = ga_metrics["convergence_history"]
    gens = [h["generation"] for h in ga_hist]
    best_fits = [h["best_fitness"] for h in ga_hist]
    mean_fits = [h["generation_mean_fitness"] for h in ga_hist]
    feat_counts = [h["best_feature_count"] for h in ga_hist]
    
    fig, ax1 = plt.subplots(figsize=(9, 5))
    color = "#0d6efd"
    ax1.set_xlabel("Generation", fontsize=12)
    ax1.set_ylabel("Fitness (F1-score + Parsimony)", color=color, fontsize=12)
    l1 = ax1.plot(gens, best_fits, color=color, lw=2.5, marker="o", label="Best Chromosome Fitness")
    l2 = ax1.plot(gens, mean_fits, color="#6c757d", lw=1.8, linestyle="--", label="Mean Population Fitness")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    color2 = "#d63384"
    ax2.set_ylabel("Number of Features in Chromosome", color=color2, fontsize=12)
    l3 = ax2.plot(gens, feat_counts, color=color2, lw=2.0, marker="s", linestyle="-.", label="Features Selected")
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim([0, len(feature_names) + 1])
    
    lines = l1 + l2 + l3
    labels_leg = [l.get_label() for l in lines]
    ax1.legend(lines, labels_leg, loc="center right", fontsize=10, frameon=True)
    plt.title("Genetic Algorithm Convergence on ClinVar Genetic Variants", fontsize=14, weight="bold", pad=12)
    ga_conv_path = os.path.join(plots_dir, "ga_convergence.png")
    plt.tight_layout()
    plt.savefig(ga_conv_path, dpi=200)
    plt.close()
    print(f"      Saved {ga_conv_path}")
    
    # 4. Feature Importance Bar Chart
    plt.figure(figsize=(10, 6))
    ga_feats = ga_metrics["feature_importances"]
    sorted_feats = sorted(ga_feats.items(), key=lambda x: x[1], reverse=True)[:15]
    feat_names_plot = [x[0] for x in sorted_feats]
    importances_plot = [x[1] for x in sorted_feats]
    
    plt.barh(range(len(feat_names_plot)), importances_plot, color="#0284c7", align="center", alpha=0.85)
    plt.yticks(range(len(feat_names_plot)), feat_names_plot, fontsize=10)
    plt.gca().invert_yaxis()
    plt.xlabel("Gini Feature Importance in GA-Selected Classifier", fontsize=11)
    plt.title("Top Predictive Features for ClinVar Classification Conflict", fontsize=13, weight="bold")
    plt.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    feat_path = os.path.join(plots_dir, "selected_biomarkers.png")
    plt.savefig(feat_path, dpi=200)
    plt.close()
    print(f"      Saved {feat_path}")
    
    # 5. Core Performance Metrics Comparison Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    methods = ["Baseline (RF)", "Baseline (LR)", "NIC: GA + RF", "NIC: PSO + RF"]
    accuracies = [rf_metrics["test_accuracy"] * 100, lr_metrics["test_accuracy"] * 100, ga_metrics["test_accuracy"] * 100, pso_metrics["test_accuracy"] * 100]
    f1_scores = [rf_metrics["test_f1_macro"] * 100, lr_metrics["test_f1_macro"] * 100, ga_metrics["test_f1_macro"] * 100, pso_metrics["test_f1_macro"] * 100]
    
    x = np.arange(len(methods))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, accuracies, width, label="Accuracy (%)", color="#0284c7", alpha=0.85)
    rects2 = ax.bar(x + width/2, f1_scores, width, label="F1-Score Macro (%)", color="#10b981", alpha=0.85)
    
    ax.set_ylabel("Score (%)", fontsize=12)
    ax.set_title("Performance Comparison: Accuracy & F1-Score on ClinVar (Test Set)", fontsize=14, weight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=10, weight="bold")
    ax.set_ylim([40, 90])
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, weight="bold")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, weight="bold")
                    
    metrics_path = os.path.join(plots_dir, "metrics_comparison.png")
    plt.tight_layout()
    plt.savefig(metrics_path, dpi=200)
    plt.close()
    print(f"      Saved {metrics_path}")
    
    return results

if __name__ == "__main__":
    run_evaluation()
