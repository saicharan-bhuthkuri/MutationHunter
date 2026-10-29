
"""
Data Acquisition and Preprocessing Pipeline
MutationHunter: Genetic Variant Classifications (ClinVar Conflicting)
Dataset: Kaggle / NCBI ClinVar (65,188 variants, 46 raw features)
Target: CLASS (0 = Consistent clinical interpretation, 1 = Conflicting clinical classification)
"""

import os
import json
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from huggingface_hub import hf_hub_download

def download_and_preprocess_clinvar(data_dir="data", random_state=42):
    raw_dir = os.path.join(data_dir, "raw")
    processed_dir = os.path.join(data_dir, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    raw_csv_path = os.path.join(raw_dir, "clinvar_conflicting.csv")
    
    # 1. Download if not already present
    if not os.path.exists(raw_csv_path):
        print("[1/4] Downloading ClinVar Conflicting dataset from Hugging Face (huseyincavus/genomics)...")
        cached_path = hf_hub_download(
            repo_id="huseyincavus/genomics",
            filename="clinvar_conflicting/clinvar_conflicting.csv",
            repo_type="dataset"
        )
        shutil.copyfile(cached_path, raw_csv_path)
        print(f"      Downloaded to {raw_csv_path}")
    else:
        print(f"[1/4] ClinVar raw dataset verified at {raw_csv_path}")
        
    df_raw = pd.read_csv(raw_csv_path, low_memory=False)
    print(f"      Loaded raw dataset with {df_raw.shape[0]} variants and {df_raw.shape[1]} columns.")
    
    # 2. Metadata
    meta = {
        "dataset_name": "Genetic Variant Classifications (ClinVar Conflicting)",
        "source": "NCBI ClinVar / Kaggle / Hugging Face (huseyincavus/genomics)",
        "total_variants": int(df_raw.shape[0]),
        "raw_columns": int(df_raw.shape[1]),
        "target_column": "CLASS",
        "classes": {
            0: "Consistent Classification (Concordant diagnostic assertions)",
            1: "Conflicting Classification (Discordant pathogenicity assertions across labs)"
        },
        "target_distribution": {str(k): int(v) for k, v in df_raw["CLASS"].value_counts().items()},
        "license": "CC0: Public Domain"
    }
    with open(os.path.join(raw_dir, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
        
    print("[2/4] Feature engineering and genomic covariate extraction...")
    df = df_raw.copy()
    
    # Allele frequencies: unobserved variants receive 0.0 frequency
    df["AF_ESP"] = df["AF_ESP"].fillna(0.0).astype(float)
    df["AF_EXAC"] = df["AF_EXAC"].fillna(0.0).astype(float)
    df["AF_TGP"] = df["AF_TGP"].fillna(0.0).astype(float)
    df["Max_AF"] = df[["AF_ESP", "AF_EXAC", "AF_TGP"]].max(axis=1)
    df["Is_Novel"] = (df["Max_AF"] == 0.0).astype(int)
    
    # In silico scores median imputation
    df["CADD_PHRED"] = df["CADD_PHRED"].fillna(df["CADD_PHRED"].median()).astype(float)
    df["CADD_RAW"] = df["CADD_RAW"].fillna(df["CADD_RAW"].median()).astype(float)
    df["LoFtool"] = df["LoFtool"].fillna(df["LoFtool"].median()).astype(float)
    df["BLOSUM62"] = df["BLOSUM62"].fillna(df["BLOSUM62"].median()).astype(float)
    
    # Structural features
    df["REF_len"] = df["REF"].astype(str).str.len().astype(int)
    df["ALT_len"] = df["ALT"].astype(str).str.len().astype(int)
    df["STRAND"] = df["STRAND"].fillna(1.0).astype(float)
    
    # Chromosome mapping
    chrom_map = {str(i): i for i in range(1, 23)}
    chrom_map["X"] = 23
    chrom_map["Y"] = 24
    df["CHROM_num"] = df["CHROM"].astype(str).map(chrom_map).fillna(0).astype(int)
    
    # Categorical One-Hot Encoding
    impact_dummies = pd.get_dummies(df["IMPACT"].fillna("UNKNOWN"), prefix="IMPACT", dtype=int)
    clnvc_dummies = pd.get_dummies(df["CLNVC"].fillna("UNKNOWN"), prefix="CLNVC", dtype=int)
    
    top_csq = ["missense_variant", "synonymous_variant", "intron_variant", "frameshift_variant", "stop_gained"]
    df["Csq_group"] = df["Consequence"].apply(lambda x: x if x in top_csq else "other")
    csq_dummies = pd.get_dummies(df["Csq_group"], prefix="CSQ", dtype=int)
    
    num_features = [
        "CADD_PHRED", "CADD_RAW", "LoFtool", "BLOSUM62",
        "AF_ESP", "AF_EXAC", "AF_TGP", "Max_AF", "Is_Novel",
        "REF_len", "ALT_len", "CHROM_num", "STRAND"
    ]
    
    feature_df = pd.concat([
        df[num_features],
        impact_dummies,
        clnvc_dummies,
        csq_dummies
    ], axis=1)
    
    target_series = df["CLASS"].astype(int)
    print(f"      Engineered {feature_df.shape[1]} clean tabular features across {len(feature_df)} variants.")
    
    # 3. Stratified 80/20 train/test split
    print("[3/4] Stratified 80/20 train/test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        feature_df, target_series, test_size=0.20, random_state=random_state, stratify=target_series
    )
    
    # Numerical scaling
    scaler = StandardScaler()
    continuous_cols = ["CADD_PHRED", "CADD_RAW", "LoFtool", "BLOSUM62", "AF_ESP", "AF_EXAC", "AF_TGP", "Max_AF", "REF_len", "ALT_len", "CHROM_num"]
    
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    
    X_train_scaled[continuous_cols] = scaler.fit_transform(X_train[continuous_cols])
    X_test_scaled[continuous_cols] = scaler.transform(X_test[continuous_cols])
    
    print("[4/4] Saving processed datasets...")
    train_df = pd.concat([X_train_scaled, y_train], axis=1)
    test_df = pd.concat([X_test_scaled, y_test], axis=1)
    
    # Subsampled stratified search set for fast GA optimization (5,000 samples)
    _, sample_train_df = train_test_split(
        train_df, test_size=5000, stratify=train_df["CLASS"], random_state=random_state
    )
    
    train_df.to_csv(os.path.join(processed_dir, "train.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test.csv"), index=False)
    sample_train_df.to_csv(os.path.join(processed_dir, "train_ga_sample.csv"), index=False)
    
    features_info = {
        "all_feature_names": list(feature_df.columns),
        "continuous_features": continuous_cols,
        "total_features": int(feature_df.shape[1]),
        "total_variants": int(len(df)),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "ga_sample_size": int(len(sample_train_df)),
        "class_counts": {str(k): int(v) for k, v in target_series.value_counts().items()},
        "means": {col: float(m) for col, m in zip(continuous_cols, scaler.mean_)},
        "scales": {col: float(s) for col, s in zip(continuous_cols, scaler.scale_)}
    }
    with open(os.path.join(processed_dir, "features_meta.json"), "w") as f:
        json.dump(features_info, f, indent=2)
        
    print(f"      Completed successfully. Processed ClinVar data ready in '{processed_dir}/'.")
    return X_train_scaled, X_test_scaled, y_train, y_test, features_info

if __name__ == "__main__":
    download_and_preprocess_clinvar()
