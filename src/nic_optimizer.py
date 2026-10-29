"""
Nature-Inspired Computing (NIC) Optimization Engine for ClinVar
MutationHunter: Genetic Variant Conflicting Classification
Algorithms:
1. Genetic Algorithm (GA) - Darwinian chromosome evolution, uniform crossover, bit-flip mutation, elitism
2. Binary Particle Swarm Optimization (BPSO) - Swarm velocity dynamics, pbest, gbest, sigmoid transfer
"""

import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)

class GeneticAlgorithmFeatureSelector:
    def __init__(
        self,
        population_size=30,
        generations=20,
        crossover_rate=0.85,
        mutation_rate=0.04,
        alpha=0.92,  # Strong weight on discriminatory ROC-AUC performance
        tournament_size=3,
        random_state=42
    ):
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.alpha = alpha
        self.tournament_size = tournament_size
        self.random_state = random_state
        self.history = []
        self.best_chromosome = None
        self.best_fitness = -1.0
        
    def _evaluate_fitness(self, chromosome, X_sample, y_sample, cv):
        selected_indices = np.where(chromosome == 1)[0]
        n_selected = len(selected_indices)
        total_features = len(chromosome)
        
        # Severe penalty for empty chromosome
        if n_selected == 0:
            return 0.0, 0.0, 0
            
        X_sub = X_sample.iloc[:, selected_indices]
        clf = ExtraTreesClassifier(
            n_estimators=25, max_depth=6, class_weight="balanced", random_state=self.random_state, n_jobs=1
        )
        scores = cross_val_score(clf, X_sub, y_sample, cv=cv, scoring="roc_auc", n_jobs=1)
        auc_cv = float(np.mean(scores))
        
        # Parsimony ratio: reward fewer selected features
        parsimony = 1.0 - (n_selected / total_features)
        
        fitness = (self.alpha * auc_cv) + ((1.0 - self.alpha) * parsimony)
        return float(fitness), float(auc_cv), n_selected

    def fit(self, X_search, y_search, feature_names=None):
        np.random.seed(self.random_state)
        n_features = X_search.shape[1]
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=self.random_state)
        
        # Initialize population with random binary chromosomes
        population = np.random.randint(0, 2, size=(self.population_size, n_features))
        for i in range(self.population_size):
            if np.sum(population[i]) == 0:
                population[i, np.random.choice(n_features, 3, replace=False)] = 1
                
        self.history = []
        self.best_fitness = -1.0
        self.best_chromosome = None
        
        start_time = time.time()
        
        for gen in range(self.generations):
            fitness_scores = []
            f1_scores = []
            feature_counts = []
            
            for ind in population:
                fit_val, f1_val, n_feat = self._evaluate_fitness(ind, X_search, y_search, cv)
                fitness_scores.append(fit_val)
                f1_scores.append(f1_val)
                feature_counts.append(n_feat)
                
            fitness_scores = np.array(fitness_scores)
            gen_best_idx = np.argmax(fitness_scores)
            gen_best_fit = fitness_scores[gen_best_idx]
            gen_best_chrom = population[gen_best_idx].copy()
            gen_mean_fit = np.mean(fitness_scores)
            
            if gen_best_fit > self.best_fitness:
                self.best_fitness = gen_best_fit
                self.best_chromosome = gen_best_chrom.copy()
                
            self.history.append({
                "generation": gen + 1,
                "best_fitness": float(self.best_fitness),
                "generation_best_fitness": float(gen_best_fit),
                "generation_mean_fitness": float(gen_mean_fit),
                "best_feature_count": int(np.sum(self.best_chromosome)),
                "best_f1_cv": float(f1_scores[gen_best_idx])
            })
            
            # Tournament Selection
            selected_parents = []
            for _ in range(self.population_size):
                participants_idx = np.random.choice(self.population_size, self.tournament_size, replace=False)
                best_p_idx = participants_idx[np.argmax(fitness_scores[participants_idx])]
                selected_parents.append(population[best_p_idx].copy())
            selected_parents = np.array(selected_parents)
            
            # Uniform Crossover
            next_generation = []
            for i in range(0, self.population_size, 2):
                parent1 = selected_parents[i]
                parent2 = selected_parents[(i + 1) % self.population_size]
                
                if np.random.rand() < self.crossover_rate:
                    mask = np.random.randint(0, 2, size=n_features).astype(bool)
                    child1 = np.where(mask, parent1, parent2)
                    child2 = np.where(mask, parent2, parent1)
                else:
                    child1 = parent1.copy()
                    child2 = parent2.copy()
                    
                next_generation.append(child1)
                next_generation.append(child2)
                
            next_generation = np.array(next_generation[:self.population_size])
            
            # Bit-flip Mutation
            for i in range(self.population_size):
                mutation_mask = np.random.rand(n_features) < self.mutation_rate
                next_generation[i] = np.bitwise_xor(next_generation[i], mutation_mask.astype(int))
                if np.sum(next_generation[i]) == 0:
                    next_generation[i, np.random.choice(n_features, 2, replace=False)] = 1
                    
            # Elitism: preserve top 2 chromosomes
            sorted_indices = np.argsort(fitness_scores)[::-1]
            next_generation[0] = population[sorted_indices[0]].copy()
            next_generation[1] = population[sorted_indices[1]].copy()
            
            population = next_generation
            
        optimization_time = time.time() - start_time
        return optimization_time

    def evaluate_on_full_test(self, X_train_full, y_train_full, X_test_full, y_test_full, feature_names):
        selected_idx = np.where(self.best_chromosome == 1)[0]
        selected_feature_names = [feature_names[i] for i in selected_idx]
        
        X_train_sub = X_train_full.iloc[:, selected_idx]
        X_test_sub = X_test_full.iloc[:, selected_idx]
        
        fit_start = time.time()
        final_clf = RandomForestClassifier(
            n_estimators=80, max_depth=10, class_weight="balanced", random_state=self.random_state, n_jobs=-1
        )
        final_clf.fit(X_train_sub, y_train_full)
        training_time = time.time() - fit_start
        
        # Infer on full test set
        infer_start = time.time()
        y_pred = final_clf.predict(X_test_sub)
        inference_time = time.time() - infer_start
        
        y_proba = final_clf.predict_proba(X_test_sub)[:, 1]
        fpr, tpr, _ = roc_curve(y_test_full, y_proba)
        
        acc = float(accuracy_score(y_test_full, y_pred))
        f1_macro = float(f1_score(y_test_full, y_pred, average="macro"))
        f1_weighted = float(f1_score(y_test_full, y_pred, average="weighted"))
        prec = float(precision_score(y_test_full, y_pred, average="macro"))
        rec = float(recall_score(y_test_full, y_pred, average="macro"))
        roc_auc = float(roc_auc_score(y_test_full, y_proba))
        cm = confusion_matrix(y_test_full, y_pred).tolist()
        
        importances = {}
        for feat, imp in zip(selected_feature_names, final_clf.feature_importances_):
            importances[feat] = float(imp)
            
        return {
            "model_name": "MutationHunter NIC (Genetic Algorithm)",
            "algorithm": "GA",
            "chromosome": self.best_chromosome.tolist(),
            "selected_features": selected_feature_names,
            "feature_count": len(selected_feature_names),
            "total_features_available": len(feature_names),
            "reduction_percentage": round((1.0 - len(selected_feature_names) / len(feature_names)) * 100, 2),
            "test_accuracy": acc,
            "test_f1_macro": f1_macro,
            "test_f1_weighted": f1_weighted,
            "test_precision": prec,
            "test_recall": rec,
            "roc_auc": roc_auc,
            "training_time_sec": training_time,
            "inference_time_sec": inference_time,
            "confusion_matrix": cm,
            "roc_curve": {"fpr": [float(x) for x in fpr], "tpr": [float(x) for x in tpr]},
            "feature_importances": importances,
            "convergence_history": self.history
        }


class ParticleSwarmFeatureSelector:
    def __init__(
        self,
        num_particles=20,
        iterations=15,
        w=0.729,
        c1=1.494,
        c2=1.494,
        alpha=0.92,
        random_state=42
    ):
        self.num_particles = num_particles
        self.iterations = iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.alpha = alpha
        self.random_state = random_state
        self.history = []
        self.gbest_position = None
        self.gbest_fitness = -1.0
        
    def _evaluate_fitness(self, position, X_sample, y_sample, cv):
        selected_indices = np.where(position == 1)[0]
        n_selected = len(selected_indices)
        total_features = len(position)
        
        if n_selected == 0:
            return 0.0, 0.0, 0
            
        X_sub = X_sample.iloc[:, selected_indices]
        clf = ExtraTreesClassifier(
            n_estimators=25, max_depth=6, class_weight="balanced", random_state=self.random_state, n_jobs=1
        )
        scores = cross_val_score(clf, X_sub, y_sample, cv=cv, scoring="roc_auc", n_jobs=1)
        auc_cv = float(np.mean(scores))
        parsimony = 1.0 - (n_selected / total_features)
        fitness = (self.alpha * auc_cv) + ((1.0 - self.alpha) * parsimony)
        return float(fitness), float(auc_cv), n_selected

    def fit(self, X_search, y_search, feature_names=None):
        np.random.seed(self.random_state)
        n_features = X_search.shape[1]
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=self.random_state)
        
        positions = np.random.randint(0, 2, size=(self.num_particles, n_features))
        velocities = np.random.uniform(-2.0, 2.0, size=(self.num_particles, n_features))
        pbest_positions = positions.copy()
        pbest_fitness = np.zeros(self.num_particles)
        
        self.gbest_position = None
        self.gbest_fitness = -1.0
        self.history = []
        
        start_time = time.time()
        
        for i in range(self.num_particles):
            fit_val, _, _ = self._evaluate_fitness(positions[i], X_search, y_search, cv)
            pbest_fitness[i] = fit_val
            if fit_val > self.gbest_fitness:
                self.gbest_fitness = fit_val
                self.gbest_position = positions[i].copy()
                
        for it in range(self.iterations):
            for i in range(self.num_particles):
                r1 = np.random.rand(n_features)
                r2 = np.random.rand(n_features)
                cognitive = self.c1 * r1 * (pbest_positions[i] - positions[i])
                social = self.c2 * r2 * (self.gbest_position - positions[i])
                velocities[i] = (self.w * velocities[i]) + cognitive + social
                velocities[i] = np.clip(velocities[i], -4.0, 4.0)
                
                s_v = 1.0 / (1.0 + np.exp(-velocities[i]))
                positions[i] = np.where(np.random.rand(n_features) < s_v, 1, 0)
                if np.sum(positions[i]) == 0:
                    positions[i, np.random.choice(n_features, 2, replace=False)] = 1
                    
                fit_val, f1_val, n_feat = self._evaluate_fitness(positions[i], X_search, y_search, cv)
                if fit_val > pbest_fitness[i]:
                    pbest_fitness[i] = fit_val
                    pbest_positions[i] = positions[i].copy()
                    
                if fit_val > self.gbest_fitness:
                    self.gbest_fitness = fit_val
                    self.gbest_position = positions[i].copy()
                    
            self.history.append({
                "iteration": it + 1,
                "best_fitness": float(self.gbest_fitness),
                "feature_count": int(np.sum(self.gbest_position))
            })
            
        opt_time = time.time() - start_time
        return opt_time

    def evaluate_on_full_test(self, X_train_full, y_train_full, X_test_full, y_test_full, feature_names):
        selected_idx = np.where(self.gbest_position == 1)[0]
        selected_feature_names = [feature_names[i] for i in selected_idx]
        
        X_train_sub = X_train_full.iloc[:, selected_idx]
        X_test_sub = X_test_full.iloc[:, selected_idx]
        
        fit_start = time.time()
        final_clf = RandomForestClassifier(
            n_estimators=80, max_depth=10, class_weight="balanced", random_state=self.random_state, n_jobs=-1
        )
        final_clf.fit(X_train_sub, y_train_full)
        training_time = time.time() - fit_start
        
        infer_start = time.time()
        y_pred = final_clf.predict(X_test_sub)
        inference_time = time.time() - infer_start
        
        y_proba = final_clf.predict_proba(X_test_sub)[:, 1]
        fpr, tpr, _ = roc_curve(y_test_full, y_proba)
        
        acc = float(accuracy_score(y_test_full, y_pred))
        f1_macro = float(f1_score(y_test_full, y_pred, average="macro"))
        f1_weighted = float(f1_score(y_test_full, y_pred, average="weighted"))
        prec = float(precision_score(y_test_full, y_pred, average="macro"))
        rec = float(recall_score(y_test_full, y_pred, average="macro"))
        roc_auc = float(roc_auc_score(y_test_full, y_proba))
        cm = confusion_matrix(y_test_full, y_pred).tolist()
        
        return {
            "model_name": "MutationHunter NIC (Particle Swarm Optimization)",
            "algorithm": "PSO",
            "chromosome": self.gbest_position.tolist(),
            "selected_features": selected_feature_names,
            "feature_count": len(selected_feature_names),
            "total_features_available": len(feature_names),
            "reduction_percentage": round((1.0 - len(selected_feature_names) / len(feature_names)) * 100, 2),
            "test_accuracy": acc,
            "test_f1_macro": f1_macro,
            "test_f1_weighted": f1_weighted,
            "test_precision": prec,
            "test_recall": rec,
            "roc_auc": roc_auc,
            "training_time_sec": training_time,
            "inference_time_sec": inference_time,
            "confusion_matrix": cm,
            "roc_curve": {"fpr": [float(x) for x in fpr], "tpr": [float(x) for x in tpr]}
        }
