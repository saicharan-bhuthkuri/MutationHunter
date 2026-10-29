"""
Baseline Model Implementation for ClinVar
MutationHunter: Genetic Variant Conflicting Classification
Standard Machine Learning baselines using all 30 features.
"""

import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)

class BaselineModel:
    def __init__(self, classifier_type="rf", random_state=42):
        self.random_state = random_state
        self.classifier_type = classifier_type
        if classifier_type == "rf":
            self.model = RandomForestClassifier(
                n_estimators=80, max_depth=10, class_weight="balanced", random_state=random_state, n_jobs=-1
            )
            self.name = "Random Forest Baseline (All 30 Features)"
        elif classifier_type == "lr":
            self.model = LogisticRegression(
                max_iter=1000, class_weight="balanced", random_state=random_state
            )
            self.name = "Logistic Regression Baseline (All 30 Features)"
        else:
            raise ValueError(f"Unknown classifier type: {classifier_type}")
            
    def fit_and_evaluate(self, X_train, y_train, X_test, y_test, feature_names=None):
        start_time = time.time()
        
        # Fit on full train set (52,150 variants)
        fit_start = time.time()
        self.model.fit(X_train, y_train)
        training_time = time.time() - fit_start
        total_runtime = time.time() - start_time
        
        # Inference on full test set (13,038 variants)
        infer_start = time.time()
        y_pred = self.model.predict(X_test)
        inference_time = time.time() - infer_start
        
        # Probabilities for ROC-AUC
        if hasattr(self.model, "predict_proba"):
            y_proba = self.model.predict_proba(X_test)[:, 1]
            roc_auc = float(roc_auc_score(y_test, y_proba))
            fpr, tpr, _ = roc_curve(y_test, y_proba)
        else:
            roc_auc = 0.0
            fpr, tpr = [], []
            
        acc = float(accuracy_score(y_test, y_pred))
        f1_macro = float(f1_score(y_test, y_pred, average="macro"))
        f1_weighted = float(f1_score(y_test, y_pred, average="weighted"))
        prec = float(precision_score(y_test, y_pred, average="macro"))
        rec = float(recall_score(y_test, y_pred, average="macro"))
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        importances = {}
        if hasattr(self.model, "feature_importances_") and feature_names is not None:
            for feat, imp in zip(feature_names, self.model.feature_importances_):
                importances[feat] = float(imp)
                
        return {
            "model_name": self.name,
            "classifier_type": self.classifier_type,
            "feature_count": X_train.shape[1],
            "total_features_available": X_train.shape[1],
            "selected_features": list(X_train.columns) if hasattr(X_train, "columns") else None,
            "test_accuracy": acc,
            "test_f1_macro": f1_macro,
            "test_f1_weighted": f1_weighted,
            "test_precision": prec,
            "test_recall": rec,
            "roc_auc": roc_auc,
            "training_time_sec": training_time,
            "total_runtime_sec": total_runtime,
            "inference_time_sec": inference_time,
            "confusion_matrix": cm,
            "roc_curve": {"fpr": [float(x) for x in fpr], "tpr": [float(x) for x in tpr]},
            "feature_importances": importances
        }
