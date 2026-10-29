"""
Clinical Variant Conflict Predictor & Inference Engine
MutationHunter: Nature-Inspired Variant Conflict Detection (ClinVar)
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class MutationHunterPredictor:
    def __init__(self, data_dir="data", results_dir="results"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.meta = None
        self.selected_features = None
        self.model = None
        self._load()
        
    def _load(self):
        meta_path = os.path.join(self.data_dir, "processed", "features_meta.json")
        with open(meta_path, "r") as f:
            self.meta = json.load(f)
            
        results_path = os.path.join(self.results_dir, "benchmark_results.json")
        if os.path.exists(results_path):
            with open(results_path, "r") as f:
                results = json.load(f)
            self.selected_features = results["ga_optimized"]["selected_features"]
        else:
            # Fallback to key in silico and allele frequency features
            self.selected_features = ["CADD_PHRED", "CADD_RAW", "LoFtool", "Max_AF", "Is_Novel", "BLOSUM62"]
            
        # Fit model on training set with selected features
        train_path = os.path.join(self.data_dir, "processed", "train.csv")
        train_df = pd.read_csv(train_path)
        
        X_train_sub = train_df[self.selected_features]
        y_train = train_df["CLASS"]
        
        self.model = RandomForestClassifier(
            n_estimators=80, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1
        )
        self.model.fit(X_train_sub, y_train)
        
    def predict(self, input_data: dict):
        """
        input_data format:
        {
            "CADD_PHRED": 15.5,
            "CADD_RAW": 2.4,
            "LoFtool": 0.35,
            "BLOSUM62": -1.0,
            "AF_ESP": 0.001,
            "AF_EXAC": 0.002,
            "AF_TGP": 0.001,
            "REF_len": 1,
            "ALT_len": 1,
            "CHROM_num": 17,
            "STRAND": 1.0,
            "IMPACT": "MODERATE",
            "CLNVC": "single_nucleotide_variant",
            "Consequence": "missense_variant"
        }
        """
        row = {}
        
        # 1. Allele frequencies
        af_esp = float(input_data.get("AF_ESP", 0.0))
        af_exac = float(input_data.get("AF_EXAC", 0.0))
        af_tgp = float(input_data.get("AF_TGP", 0.0))
        max_af = max(af_esp, af_exac, af_tgp)
        is_novel = 1 if max_af == 0.0 else 0
        
        raw_vals = {
            "CADD_PHRED": float(input_data.get("CADD_PHRED", 15.0)),
            "CADD_RAW": float(input_data.get("CADD_RAW", 2.0)),
            "LoFtool": float(input_data.get("LoFtool", 0.3)),
            "BLOSUM62": float(input_data.get("BLOSUM62", -1.0)),
            "AF_ESP": af_esp,
            "AF_EXAC": af_exac,
            "AF_TGP": af_tgp,
            "Max_AF": max_af,
            "REF_len": float(input_data.get("REF_len", 1)),
            "ALT_len": float(input_data.get("ALT_len", 1)),
            "CHROM_num": float(input_data.get("CHROM_num", 1))
        }
        
        # Scale continuous features using stored means and scales
        for col, val in raw_vals.items():
            mean = self.meta["means"].get(col, 0.0)
            scale = self.meta["scales"].get(col, 1.0)
            row[col] = (val - mean) / (scale if scale != 0 else 1.0)
            
        row["Is_Novel"] = is_novel
        row["STRAND"] = float(input_data.get("STRAND", 1.0))
        
        # Categoricals one-hot
        impact_val = str(input_data.get("IMPACT", "MODERATE")).strip().upper()
        for f in self.meta["all_feature_names"]:
            if f.startswith("IMPACT_"):
                row[f] = 1 if f == f"IMPACT_{impact_val}" else 0
                
        clnvc_val = str(input_data.get("CLNVC", "single_nucleotide_variant")).strip()
        for f in self.meta["all_feature_names"]:
            if f.startswith("CLNVC_"):
                row[f] = 1 if f == f"CLNVC_{clnvc_val}" else 0
                
        csq_val = str(input_data.get("Consequence", "missense_variant")).strip()
        for f in self.meta["all_feature_names"]:
            if f.startswith("CSQ_"):
                row[f] = 1 if f == f"CSQ_{csq_val}" else 0
                
        # Form sub-dataframe matching selected features
        sub_vector = {col: [row.get(col, 0.0)] for col in self.selected_features}
        df_sub = pd.DataFrame(sub_vector)
        
        # Inference
        proba = self.model.predict_proba(df_sub)[0]
        prob_consistent = float(proba[0])
        prob_conflicting = float(proba[1])
        predicted_class = int(np.argmax(proba))
        
        # Clinical genetics threshold: baseline prevalence is ~25%. Risk >= 30% flags discordance alert.
        is_conflict = (prob_conflicting >= 0.30) or (predicted_class == 1)
        
        status_label = "Conflicting Clinical Classification" if is_conflict else "Consistent Clinical Classification"
        risk_level = "High Classification Conflict Risk" if is_conflict else "Consistent Diagnostic Classification"
        confidence = float((prob_conflicting if is_conflict else prob_consistent) * 100.0)
        
        # Clinical & Biological insights
        insights = []
        cadd_phred = raw_vals["CADD_PHRED"]
        if is_novel == 1:
            insights.append("Novel / unobserved population variant (AF = 0.0): elevated ambiguity due to lack of large-scale population cohort evidence.")
        else:
            insights.append(f"Documented population frequency (Max AF = {max_af:.4f}): provides empirical population allele constraint.")
            
        if cadd_phred >= 20.0:
            insights.append(f"High CADD PHRED score ({cadd_phred:.1f} >= 20, top 1% deleterious): in silico predictors forecast damaging functional consequence.")
        elif cadd_phred < 10.0:
            insights.append(f"Low CADD PHRED score ({cadd_phred:.1f} < 10): in silico predictors suggest neutral evolutionary tolerance.")
            
        if raw_vals["LoFtool"] < 0.25:
            insights.append("Low LoFtool score indicates gene is highly intolerant to loss-of-function variations, increasing clinical scrutiny.")
            
        return {
            "predicted_class_code": 1 if is_conflict else 0,
            "predicted_class_label": status_label,
            "risk_assessment": risk_level,
            "confidence_percentage": round(confidence, 1),
            "probability_consistent": round(prob_consistent * 100.0, 1),
            "probability_conflicting": round(prob_conflicting * 100.0, 1),
            "selected_biomarkers_used": self.selected_features,
            "num_biomarkers_used": len(self.selected_features),
            "clinical_insights": insights
        }
