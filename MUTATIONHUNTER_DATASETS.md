# MutationHunter: Genetic Variant Dataset Search
## Nature-Inspired Detection and Prioritization of Significant Genetic Mutations

This document provides a comprehensive, research-grade catalog of publicly available genetic mutation and variant datasets collected for the **MutationHunter** project. All dataset records, schemas, and endpoints were verified using **Scrapling** across official repositories, Hugging Face, Kaggle, Zenodo, and the UCI Machine Learning Repository.

---

## Executive Summary & Top 3 Recommendations

| Rank | Dataset Name | Source / Platform | Total Variants / Records | Primary Use Case in MutationHunter |
| :---: | :--- | :--- | :--- | :--- |
| **🥇 1** | **[Genetic Variant Classifications (ClinVar Conflicting)](https://www.kaggle.com/datasets/kevinarvai/clinvar-conflicting)** | Kaggle (NCBI ClinVar) | 65,188 variants | **Fast Prototyping & Tabular Feature Selection**: Pre-processed CSV with 46 rich features (CADD, SIFT, PolyPhen, BLOSUM62, allele frequencies). Ideal for binary GA feature selection and AIS antibody-antigen affinity rules. |
| **🥈 2** | **[ProteinGym v1](https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1)** | Hugging Face (Harvard / Oxford) | ~2,700,000+ variants | **Sequence-Level Nature-Inspired Modeling**: Direct protein wild-type and mutant sequence strings (`target_seq` & `mutated_sequence`) + continuous experimental fitness scores (`DMS_score`) and clinical labels (`pathogenic` vs `benign`). |
| **🥉 3** | **[AlphaMissense Predictions Database](https://zenodo.org/records/8208688)** | Zenodo (Google DeepMind / Science) | 71,280,000 variants | **Proteome-Wide Priority Benchmarking**: Continuous pathogenicity scores (`am_pathogenicity` 0.0–1.0) for 89% of all possible human missense variants. Acts as the state-of-the-art ground truth. |

---

## Detailed Dataset Catalog

### 1. Genetic Variant Classifications (ClinVar Conflicting)

- **Source / Platform**: [Kaggle](https://www.kaggle.com/datasets/kevinarvai/clinvar-conflicting) (Derived from NCBI ClinVar)
- **Direct URL**: https://www.kaggle.com/datasets/kevinarvai/clinvar-conflicting
- **Description**: ClinVar is a public archive containing annotations about human genetic variants classified by clinical diagnostic laboratories. A major challenge in genomic medicine occurs when clinical laboratories disagree on classification (e.g., Benign vs. Pathogenic). This dataset provides a cleaned, ML-ready extraction of human genetic variants with extensive functional, population, and conservation annotations to predict classification conflict and score mutation severity.
- **Records / Variants**: **65,188** variants.
- **Available Features / Columns (46 total)**:
  - **Genomic coordinates**: `CHROM`, `POS`, `REF`, `ALT`, `STRAND`
  - **Population allele frequencies**: `AF_ESP`, `AF_EXAC`, `AF_TGP` (1000 Genomes)
  - **Variant consequence & location**: `CLNVC`, `ORIGIN`, `Consequence`, `IMPACT`, `cDNA_position`, `CDS_position`, `Protein_position`, `Amino_acids`, `Codons`, `Exon`, `INTRON`, `SYMBOL`
  - **In silico baseline scores**: `CADD_RAW`, `CADD_PHRED`, `SIFT`, `PolyPhen`, `BLOSUM62`, `LoFtool`
  - **Phenotypic links**: `CLNDN` (ClinVar disease names), `CLNDISDB`
- **Target / Label Column**:
  - `CLASS` (binary: 0 = consistent clinical classification, 1 = conflicting classification)
  - `CLNSIG` / `CLNSIGCONF` (multiclass categorical: Benign, Likely Benign, VUS, Likely Pathogenic, Pathogenic)
- **Disease / Biological Context**: Broad spectrum of human Mendelian and complex hereditary diseases.
- **File Format**: CSV (`clinvar_conflicting.csv`, ~3.76 MB compressed / ~35 MB uncompressed).
- **License / Restrictions**: **CC0: Public Domain** (Open data, no restrictions).
- **Publication / Update Date**: March 2020.
- **Academic / Research Suitability**: **Yes**; widely used in machine learning and bioinformatics literature.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Pre-engineered Features**: Features are already tabular and clean, eliminating complex bioinformatic parsing pipelines.
> - **GA Feature Selection**: A 46-bit binary chromosome where bit $i \in \{0, 1\}$ represents the inclusion of feature $i$. GA optimizes classification accuracy and AUROC while minimizing feature count to discover the minimal set of biomarkers required to predict severe or conflicting mutations.
> - **AIS Clonal & Negative Selection**: Tolerant/benign variants (high population frequency in `AF_EXAC`/`AF_TGP`, neutral `BLOSUM62`) represent "self" cells. Deleterious variants (high `CADD_PHRED`, damaging `PolyPhen`) act as "non-self" antigens. B-cell receptors evolve through affinity maturation to detect lethal mutation patterns.
> - **Baseline Comparison**: The inclusion of `CADD`, `SIFT`, and `PolyPhen` within the rows enables direct comparison between conventional scoring baselines and MutationHunter's evolved priority score.

---

### 2. ProteinGym v1 (Clinical Substitutions & Indels / DMS Benchmarks)

- **Source / Platform**: [Hugging Face Datasets](https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1) (Harvard Marks Lab & Oxford OATML)
- **Direct URL**: https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1 (Project: https://proteingym.org/)
- **Description**: The premier open benchmark for evaluating protein fitness and variant effect prediction models. Developed by the Marks Lab (Harvard) and OATML (Oxford) and presented at NeurIPS 2023. Encompasses both experimental deep mutational scanning (DMS) measurements and clinically annotated human variants from ClinVar and gnomAD.
- **Records / Variants**: **~2,700,000+** variants across 217 experimental DMS assays + clinical substitutions/indels.
- **Available Features / Columns**:
  - `target_seq`: Complete wild-type amino acid sequence.
  - `mutated_sequence`: Full protein sequence with the specific mutation applied.
  - `mutant`: Single/multiple mutation nomenclature (e.g., `M1A`, `P104L`).
  - `protein_id` / `DMS_id`: Standardized protein identifier.
  - `DMS_score`: Quantitative measured fitness score (continuous).
  - `DMS_score_bin`: Binned functional activity (binary/ordinal).
  - `annotation`: Clinical classification from ClinVar/gnomAD (`pathogenic` vs `benign`).
- **Target / Label Column**:
  - Clinical sets: `annotation` (`pathogenic` vs `benign`).
  - DMS sets: `DMS_score` (continuous regression) and `DMS_score_bin` (binary classification).
- **Disease / Biological Context**: Critical human disease proteins (*BRCA1*, *TP53*, *PTEN*, *MSH2*, *CFTR*, *VKORC1*, *SCN5A*) with biophysical, biochemical, and cellular survival impact.
- **File Format**: Parquet / CSV (direct load via `datasets.load_dataset("OATML-Markslab/ProteinGym_v1")`).
- **License / Restrictions**: **MIT License / CC-BY 4.0** (Open science, free for academic and commercial use).
- **Publication / Update Date**: NeurIPS 2023; updated July 2025.
- **Academic / Research Suitability**: **Yes**; recognized as the gold standard in protein machine learning.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Sequence-Level Nature-Inspired Encoding**: Unlike purely numerical tables, ProteinGym provides raw sequences (`target_seq` and `mutated_sequence`). Chromosomes in GA can directly represent sequences with crossover and mutation operators mirroring biological DNA/amino acid mutations.
> - **AIS Shape-Space & Affinity Maturation**: AIS affinity functions can compute physicochemical shape-space distance (Grantham scale, hydrophobicity change, steric volume clash, charge reversal) between wild-type and mutant sequence segments. Memory cells learn to recognize pathogenic "epitopes" where small changes drastically reduce `DMS_score`.
> - **Continuous Priority Scoring**: The experimental `DMS_score` provides an objective, real-world biophysical fitness measurement against which MutationHunter's continuous mutation priority score can be validated using Spearman correlation.

---

### 3. AlphaMissense Proteome-wide Missense Predictions

- **Source / Platform**: [Zenodo](https://zenodo.org/records/8208688) / [Google DeepMind](https://github.com/google-deepmind/alphamissense)
- **Direct URL**: https://zenodo.org/records/8208688
- **Description**: Developed by Google DeepMind and published in *Science* (Cheng et al., 2023), AlphaMissense adapts AlphaFold to predict the functional consequences of missense mutations. It leverages structural context, evolutionary conservation, and structural modeling to classify 89% of all 71 million possible human missense variants.
- **Records / Variants**: **71,280,000** missense variants covering 19,000+ human proteins.
- **Available Features / Columns**:
  - `#CHROM`, `POS`: Genomic coordinates (available in both GRCh38/hg38 and GRCh37/hg19).
  - `REF`, `ALT`: Reference and mutated nucleotide.
  - `genome`: Assembly version.
  - `uniprot_id`: UniProt protein accession code.
  - `transcript_id`: Ensembl transcript identifier.
  - `protein_variant`: Amino acid substitution nomenclature (e.g., `p.Arg45Trp`).
  - `am_pathogenicity`: Continuous predicted pathogenicity score ranging from **0.0** (strictly benign) to **1.0** (highly pathogenic).
  - `am_class`: Categorical call (`likely_benign`, `ambiguous`, `likely_pathogenic`).
  - Gene-level summary file: `AlphaMissense_gene_hg38.tsv.gz` contains gene-level mean pathogenicity scores (`mean_am_pathogenicity`).
- **Target / Label Column**: `am_class` (categorical) and `am_pathogenicity` (continuous priority score).
- **Disease / Biological Context**: Whole human exome and proteome, including rare Mendelian disorders, complex traits, and somatic oncogenesis.
- **File Format**: TSV Gzipped (`AlphaMissense_hg38.tsv.gz` 613 MB, `AlphaMissense_aa_substitutions.tsv.gz` 1.15 GB).
- **License / Restrictions**: **CC BY-NC-SA 4.0** (Free for academic research use with attribution).
- **Publication / Update Date**: September 19, 2023 (*Science* 381, eadg7492).
- **Academic / Research Suitability**: **Yes**; state-of-the-art benchmark.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Definitive Baseline Benchmark**: AlphaMissense represents the current state-of-the-art in variant effect prediction. MutationHunter can evaluate its priority score against AlphaMissense across tens of thousands of test variants.
> - **GA Multi-Objective Optimization**: GA can optimize a multi-objective fitness function that balances high sensitivity on high-confidence pathogenic variants (`am_pathogenicity > 0.8`) against specificity on benign population variants (`am_pathogenicity < 0.2`).
> - **AIS Clonal Selection**: AIS detectors can be trained to recognize mutation hotspots across different protein families, with clonal expansion driven by `am_pathogenicity` affinity metrics.

---

### 4. NCBI ClinVar Official Variant Summary

- **Source / Platform**: [NCBI / NIH](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/)
- **Direct URL**: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
- **Description**: The official United States National Institutes of Health (NIH) public database of human genomic variants and interpretations of their clinical significance. Maintained by the National Center for Biotechnology Information (NCBI), it aggregates clinical assertions submitted by genetic testing laboratories, medical centers, and expert panels.
- **Records / Variants**: **>3,500,000+** variant records (>2.4 million distinct genomic alleles).
- **Available Features / Columns (32 columns)**:
  - `AlleleID`, `Type` (single nucleotide variant, deletion, duplication, indel)
  - `Name`, `GeneID`, `GeneSymbol`, `HGNC_ID`
  - `ClinicalSignificance`: Consensus clinical classification
  - `ClinSigSimple`: Binary indicator (0 = Benign/Likely Benign, 1 = Pathogenic/Likely Pathogenic, -1 = Uncertain)
  - `ReviewStatus`: Gold-star curation ranking (0 = no criteria, 1 = criteria provided, 2 = multiple submitters without conflict, 3 = expert panel, 4 = practice guideline)
  - `NumberSubmitters`, `LastEvaluated`
  - `RS# (dbSNP)`, `nsv/esv (dbVar)`
  - `PhenotypeIDs`, `PhenotypeList`, `Origin`
  - `Assembly` (`GRCh37` or `GRCh38`), `Chromosome`, `Start`, `Stop`, `ReferenceAllele`, `AlternateAllele`, `Cytogenetic`
- **Target / Label Column**: `ClinSigSimple` (0 vs 1) and `ClinicalSignificance` (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign).
- **Disease / Biological Context**: All human hereditary and germline conditions documented in MedGen and OMIM.
- **File Format**: Tab-delimited compressed text (`variant_summary.txt.gz`, ~240 MB compressed / ~2.5 GB uncompressed).
- **License / Restrictions**: **Public Domain** (US Government work; no copyright restrictions).
- **Publication / Update Date**: Updated weekly; monthly archival releases maintained continuously (Current 2026 archive).
- **Academic / Research Suitability**: **Yes**; the gold standard for clinical variant classification.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Gold-Standard Curation**: The `ReviewStatus` column allows filtering the dataset to only high-confidence variants (e.g., 2+ gold stars), creating a clean ground-truth training and testing split.
> - **GA Weight Optimization**: GA can optimize scoring weights assigned to variant type, chromosomal position, and gene intolerance metrics to produce an interpretable Mutation Priority Score.
> - **AIS Danger Theory**: In Matzinger's AIS Danger Model, `ClinSigSimple` acts as the danger signal: benign variants (0) are accepted into the immune repertoire, while pathogenic variants (1) activate clonal proliferation and memory detector formation.

---

### 5. TCGA MC3 Pan-Cancer Somatic Mutation Dataset

- **Source / Platform**: [NCI Genomic Data Commons (GDC)](https://gdc.cancer.gov/about-data/publications/mc3-2017)
- **Direct URL**: https://gdc.cancer.gov/about-data/publications/mc3-2017 (MAF: `mc3.v0.2.8.PUBLIC.maf.gz`)
- **Description**: The consensus somatic mutation encyclopedia of The Cancer Genome Atlas (TCGA) PanCanAtlas project, published in *Cell Systems* (Ellrott et al., 2018). It uniformly re-analyzed exome sequencing data from 10,295 cancer patients across 33 distinct tumor types using an ensemble of 7 independent somatic mutation callers.
- **Records / Variants**: **3,600,963** curated somatic mutation calls.
- **Available Features / Columns (Mutation Annotation Format - MAF)**:
  - `Hugo_Symbol`, `Entrez_Gene_Id`
  - `Chromosome`, `Start_Position`, `End_Position`, `Strand`
  - `Variant_Classification`: Missense_Mutation, Nonsense_Mutation, Frame_Shift_Del, Frame_Shift_Ins, In_Frame_Del, In_Frame_Ins, Splice_Site
  - `Variant_Type`: SNP, DNP, TNP, INS, DEL
  - `Reference_Allele`, `Tumor_Seq_Allele1`, `Tumor_Seq_Allele2`
  - `t_depth` (total tumor read depth), `t_ref_count`, `t_alt_count` (tumor alternate allele reads — used to calculate Variant Allele Frequency: $VAF = t\_alt / t\_depth$)
  - `n_depth`, `n_ref_count`, `n_alt_count` (matched normal sequencing depth)
  - `FILTER`: `PASS` flag vs artifact filter flags
  - `SIFT`, `PolyPhen` consequence annotations
- **Target / Label Column**: `Variant_Classification` (truncating/loss-of-function vs silent) or somatic driver status.
- **Disease / Biological Context**: Oncology across 33 major human cancer types (GBM, BRCA, LUAD, COAD, SKCM, etc.).
- **File Format**: MAF (tab-delimited TSV gzipped, ~950 MB).
- **License / Restrictions**: **NCI Open-Access Data** (Freely available for research; open access).
- **Publication / Update Date**: *Cell Systems* 2018; hosted on GDC.
- **Academic / Research Suitability**: **Yes**; foundational dataset for cancer somatic genomics.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Driver vs. Passenger Prioritization**: Somatic cancer genomes contain thousands of benign passenger mutations and only a few critical driver mutations. MutationHunter's nature-inspired optimization can be trained to distinguish driver events from passenger noise.
> - **GA Fitness Function**: GA can evolve an optimal formula combining Variant Allele Frequency ($VAF = t\_alt\_count / t\_depth$), sequencing quality depth, and consequence severity (`Variant_Classification`) to prioritize somatic mutations by clonal dominance.
> - **AIS Immune Surveillance**: In an AIS framework, antibodies represent patterns of neutral passenger mutations; strong antigenic activation signals somatic driver events that escape normal evolutionary suppression.

---

### 6. Glioma Grading Clinical and Mutation Features

- **Source / Platform**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/759/glioma+grading+clinical+and+mutation+features) / [Kaggle](https://www.kaggle.com/)
- **Direct URL**: https://archive.ics.uci.edu/dataset/759/glioma+grading+clinical+and+mutation+features (DOI: https://doi.org/10.24432/C5R62J)
- **Description**: Derived from TCGA-LGG (Lower-Grade Glioma) and TCGA-GBM (Glioblastoma Multiforme), this benchmark dataset focuses on determining brain tumor grade from the mutation status of 20 critical cancer genes combined with basic demographic features. The explicit experimental goal is to discover the minimal, highest-priority subset of gene mutations needed to accurately classify tumor severity.
- **Records / Variants**: **839** patient cases.
- **Available Features / Columns (23 features)**:
  - **Clinical Features**: `Age_at_diagnosis`, `Gender`, `Race`
  - **20 Gene Mutation Statuses** (binary: `mutated` vs `not_mutated`):
    `IDH1`, `TP53`, `ATRX`, `PTEN`, `EGFR`, `CIC`, `MUC16`, `PIK3CA`, `NF1`, `PIK3R1`, `FUBP1`, `RB1`, `NOTCH1`, `BCOR`, `CSMD3`, `SMARCA4`, `GRIN2A`, `IDH2`, `FAT4`, `PDGFRA`
- **Target / Label Column**: `Grade` (Binary: `0 = LGG` [Lower-Grade Glioma], `1 = GBM` [Glioblastoma Multiforme]).
- **Disease / Biological Context**: Neuro-oncology / Human brain tumors (Gliomas).
- **File Format**: CSV (Can be loaded directly via Python `ucimlrepo`).
- **License / Restrictions**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Publication / Update Date**: 2022 (Tasci et al.).
- **Academic / Research Suitability**: **Yes**; officially hosted by UCI.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Explicitly Designed for Feature Selection & Prioritization**: The primary objective is discovering the optimal, minimal subset of mutated genes that distinguishes aggressive Glioblastoma (`GBM`) from Lower-Grade Glioma (`LGG`).
> - **Binary GA Optimization**: Chromosomes represent a 23-bit binary vector where bit $i = 1$ includes the corresponding gene mutation. GA maximizes diagnostic accuracy while penalizing the number of genes selected, evolving an optimal, cost-effective mutation panel.
> - **AIS Clonal Selection Algorithm (CLONALG)**: B-cells represent mutation profiles. Antigenic affinity is high when a specific combination of mutations (e.g., wildtype `IDH1` + mutated `EGFR` + mutated `PTEN`) reliably detects the malignant GBM phenotype.

---

### 7. dbNSFP (Database for Non-synonymous SNPs' Functional Predictions)

- **Source / Platform**: University of South Florida / [Ensembl](https://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh38/database/dbNSFP/) (Liu et al.)
- **Direct URL**: https://sites.google.com/site/jpopgen/dbNSFP (Ensembl: https://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh38/database/dbNSFP/)
- **Description**: dbNSFP compiles in silico functional predictions, conservation scores, population allele frequencies, and clinical annotations for **every possible** nonsynonymous single nucleotide variant (nsSNV) and splice-site SNV in the human genome (~84 million variants).
- **Records / Variants**: **~84,000,000** human variants.
- **Available Features / Columns (>100 numerical and categorical columns)**:
  - **Baseline predictors**: `SIFT_score`, `Polyphen2_HDIV_score`, `Polyphen2_HVAR_score`, `CADD_raw`, `CADD_phred`, `REVEL_score`, `MutationTaster_score`, `MutationAssessor_score`, `FATHMM_score`, `PROVEAN_score`, `MetaSVM_score`, `MetaLR_score`, `VEST4_score`
  - **Conservation scores**: `GERP++_RS`, `phyloP100way_vertebrate`, `phastCons100way_vertebrate`, `SiPhy_29way_logOdds`
  - **Population frequencies**: `gnomAD_exomes_AF`, `gnomAD_genomes_AF`, `1000Gp3_AF`, `ExAC_AF`
  - **Clinical annotations**: `clinvar_clnsig`, `clinvar_review`, `clinvar_trait`
- **Target / Label Column**: `clinvar_clnsig` (Pathogenic vs Benign) or consensus ensemble predictions.
- **Disease / Biological Context**: Whole-exome human genetic disease genetics, pharmacogenomics, and evolutionary constraint.
- **File Format**: Tabix-indexed TSV gzipped files split by chromosome.
- **License / Restrictions**: Free for non-commercial academic research.
- **Publication / Update Date**: Current v4.x release (regularly updated by Liu et al.).
- **Academic / Research Suitability**: **Yes**; standard reference table in computational genomics.

> **Why this dataset is suitable for MutationHunter and what features can be used by the GA/AIS algorithm:**
> - **Comprehensive Predictor Ensemble**: Contains over 30 baseline algorithm scores and 10 conservation scores in every single record.
> - **GA Meta-Predictor Weight Optimization**: MutationHunter can formulate a composite mutation priority score:
>   $$\text{PriorityScore}(v) = \sum_{i=1}^M w_i \cdot f_i(v)$$
>   GA can evolve the weight vector $\vec{w}$ and non-linear thresholds to outperform any individual baseline algorithm (`CADD`, `REVEL`, `SIFT`).
> - **AIS Immune Memory**: High-affinity memory detectors can be trained to recognize lethal evolutionary conservation combinations (`GERP++` > 4.0, `phyloP` > 7.0, `gnomAD_AF` < $10^{-5}$).

---

## Comparison Matrix

| Dataset                  | Platform     |   Records   | Key Features                  | Target Column                  | GA / AIS Mechanism                             |  File Format  |
| :----------------------- | :----------- | :---------: | :---------------------------- | :----------------------------- | :--------------------------------------------- | :-----------: |
| **ClinVar Conflicting**  | Kaggle       |   65,188    | CADD, SIFT, PolyPhen, AFs     | `CLASS` (0/1), `CLNSIG`        | GA Feature Selection / AIS Clonal Selection    |      CSV      |
| **ProteinGym v1**        | Hugging Face | ~2,700,000+ | Sequences + DMS Fitness       | `DMS_score`, `annotation`      | GA Sequence Mutation / AIS Shape Space         | Parquet / CSV |
| **AlphaMissense**        | Zenodo       | 71,280,000  | AM Pathogenicity, Class       | `am_pathogenicity`, `am_class` | GA Multi-objective / Baseline Benchmarking     |    TSV.gz     |
| **NCBI ClinVar Summary** | NCBI / NIH   | >3,500,000  | Clinical Significance, Review | `ClinSigSimple` (0/1)          | GA Weight Calibration / AIS Negative Selection |    TSV.gz     |
| **TCGA MC3 Somatic**     | NCI GDC      |  3,600,963  | VAF, Classification, Depths   | Driver vs Passenger / $VAF$    | GA Clonal Prioritization / AIS Danger Theory   | MAF (TSV.gz)  |
| **Glioma Mutation**      | UCI ML       |     839     | 20 Gene Mutations + Clinical  | `Grade` (LGG vs GBM)           | Binary GA Feature Selection / AIS CLONALG      |      CSV      |
| **dbNSFP**               | Ensembl/USF  | ~84,000,000 | >30 Predictor Scores, GERP    | `clinvar_clnsig`               | GA Meta-Predictor / AIS Hypermutation          | Tabix TSV.gz  |

---

## Recommended Project Phasing for MutationHunter

```
Phase 1: Fast Prototyping
├── ClinVar Conflicting (Kaggle - 65,188 rows)
└── Glioma Mutation Features (UCI - 839 rows)
    └── Objective: Validate GA feature selection and AIS CLONALG algorithms in Python (pandas/scikit-learn).

Phase 2: Sequence-Level Modeling
└── ProteinGym v1 (Hugging Face - 2.7M rows)
    └── Objective: Train sequence-level GA chromosomes and AIS shape-space affinity models on true wild-type/mutant sequences.

Phase 3: Large-Scale Benchmarking
├── AlphaMissense (Zenodo - 71M rows)
└── dbNSFP (Ensembl - 84M rows)
    └── Objective: Benchmark the MutationHunter Priority Score against CADD, REVEL, and AlphaMissense.
```
