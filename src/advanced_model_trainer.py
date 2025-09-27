"""
Advanced VM Placement AI Model Trainer

This module implements sophisticated AI techniques for VM placement optimization:
- Multi-objective optimization
- Ensemble methods 
- Specialized models for different objectives
- Advanced feature engineering
- Hyperparameter optimization with multiple algorithms
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif, RFE
import xgboost as xgb
import joblib
import json
from typing import Dict, Tuple, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AdvancedVMPlacementModelTrainer:
    def __init__(self, dataset_path: str = "data/vm_placement_dataset.csv"):
        """Initialize the advanced model trainer"""
        self.dataset_path = dataset_path
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        self.feature_columns = None
        self.models = {}
        self.best_models = {}
        self.feature_importance = {}
        self.multi_objective_models = {}
        
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
        """Load and preprocess data with enhanced feature engineering"""
        print("Loading and preprocessing dataset...")
        df = pd.read_csv(self.dataset_path)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Positive samples (optimal placements): {df['is_optimal'].sum()}")
        
        # Remove target-related columns for training
        feature_cols_to_remove = ['composite_score', 'is_optimal']
        self.feature_columns = [col for col in df.columns if col not in feature_cols_to_remove]
        
        X = df[self.feature_columns].copy()
        y = df['is_optimal'].values
        
        # Create target variables for multi-objective optimization
        objectives_df = df[['energy_consumption', 'cost', 'cpu_utilization', 
                          'ram_utilization', 'sla_violation_risk']].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        objectives_df = objectives_df.fillna(objectives_df.mean())
        
        return X, y, objectives_df
    
    def advanced_feature_engineering(self, X: pd.DataFrame, objectives_df: pd.DataFrame) -> pd.DataFrame:
        """Apply advanced feature engineering techniques"""
        print("Applying advanced feature engineering...")
        
        X_engineered = X.copy()
        
        # 1. Enhanced efficiency features
        X_engineered['cpu_efficiency_quadratic'] = (1 - abs(X['cpu_util_after_placement'] - 0.7)) ** 2
        X_engineered['ram_efficiency_quadratic'] = (1 - abs(X['ram_util_after_placement'] - 0.7)) ** 2
        
        # 2. Resource utilization balance and patterns
        X_engineered['resource_balance_score'] = 1 - abs(X['cpu_util_after_placement'] - X['ram_util_after_placement'])
        X_engineered['total_utilization'] = X['cpu_util_after_placement'] + X['ram_util_after_placement']
        X_engineered['utilization_product'] = X['cpu_util_after_placement'] * X['ram_util_after_placement']
        
        # 3. Advanced cost and energy features
        if 'cost' in X.columns and 'energy_consumption' in X.columns:
            X_engineered['cost_efficiency'] = X['cost'] / (X['vm_cpu_required'] + X['vm_ram_required'])
            X_engineered['energy_efficiency'] = X['energy_consumption'] / (X['host_cpu_cores'] + X['host_ram_gb'] / 10)
            X_engineered['cost_energy_ratio'] = X['cost'] / (X['energy_consumption'] + 1e-6)
        
        # 4. Host capacity and load features
        X_engineered['host_total_capacity'] = X['host_cpu_cores'] + X['host_ram_gb'] / 10
        X_engineered['host_load_density'] = (X['host_current_cpu_util'] + X['host_current_ram_util']) / 2
        X_engineered['remaining_capacity'] = (
            (X['host_cpu_cores'] * (1 - X['host_current_cpu_util'])) + 
            (X['host_ram_gb'] * (1 - X['host_current_ram_util'])) / 10
        )
        
        # 5. VM complexity and priority features
        X_engineered['vm_resource_intensity'] = X['vm_cpu_required'] * X['vm_ram_required']
        if 'vm_runtime_hours' in X.columns:
            X_engineered['vm_total_demand'] = X_engineered['vm_resource_intensity'] * X['vm_runtime_hours']
        
        # 6. SLA and risk features
        if 'sla_violation_risk' in X.columns:
            X_engineered['sla_safety_margin'] = 1 - X['sla_violation_risk']
            X_engineered['risk_adjusted_efficiency'] = X_engineered['resource_balance_score'] * X_engineered['sla_safety_margin']
        
        # 7. Ratio and interaction features
        X_engineered['cpu_to_ram_ratio'] = X['vm_cpu_required'] / (X['vm_ram_required'] + 1e-6)
        X_engineered['host_cpu_to_ram_ratio'] = X['host_cpu_cores'] / (X['host_ram_gb'] + 1e-6)
        X_engineered['resource_match_score'] = 1 - abs(X_engineered['cpu_to_ram_ratio'] - X_engineered['host_cpu_to_ram_ratio'])
        
        # 8. Multi-objective composite features
        if not objectives_df.empty:
            # Normalize objectives for composite features
            energy_norm = (objectives_df['energy_consumption'] - objectives_df['energy_consumption'].min()) / (objectives_df['energy_consumption'].max() - objectives_df['energy_consumption'].min() + 1e-6)
            cost_norm = (objectives_df['cost'] - objectives_df['cost'].min()) / (objectives_df['cost'].max() - objectives_df['cost'].min() + 1e-6)
            
            X_engineered['energy_cost_composite'] = 0.5 * energy_norm + 0.5 * cost_norm
            X_engineered['utilization_composite'] = 0.5 * objectives_df['cpu_utilization'] + 0.5 * objectives_df['ram_utilization']
        
        # 9. Polynomial features for key metrics
        key_features = ['cpu_util_after_placement', 'ram_util_after_placement', 'host_load_density']
        for feature in key_features:
            if feature in X_engineered.columns:
                X_engineered[f'{feature}_squared'] = X_engineered[feature] ** 2
                X_engineered[f'{feature}_cubed'] = X_engineered[feature] ** 3
        
        print(f"Feature engineering complete. New feature count: {len(X_engineered.columns)}")
        return X_engineered
    
    def create_multi_objective_targets(self, objectives_df: pd.DataFrame, y: np.ndarray) -> Dict[str, np.ndarray]:
        """Create specialized targets for multi-objective optimization"""
        print("Creating multi-objective targets...")
        
        targets = {'main': y}  # Original optimal placement target
        
        # Create percentile-based targets for each objective
        energy_threshold = objectives_df['energy_consumption'].quantile(0.3)  # Bottom 30% for energy
        cost_threshold = objectives_df['cost'].quantile(0.3)  # Bottom 30% for cost
        cpu_util_optimal = abs(objectives_df['cpu_utilization'] - 0.7) < 0.15  # Within 15% of 70%
        ram_util_optimal = abs(objectives_df['ram_utilization'] - 0.7) < 0.15
        sla_threshold = objectives_df['sla_violation_risk'].quantile(0.3)  # Bottom 30% for SLA risk
        
        targets['energy_efficient'] = (objectives_df['energy_consumption'] <= energy_threshold).astype(int)
        targets['cost_efficient'] = (objectives_df['cost'] <= cost_threshold).astype(int)
        targets['cpu_optimal'] = cpu_util_optimal.astype(int)
        targets['ram_optimal'] = ram_util_optimal.astype(int)
        targets['sla_safe'] = (objectives_df['sla_violation_risk'] <= sla_threshold).astype(int)
        
        # Create balanced composite targets
        targets['balanced'] = ((targets['energy_efficient'] + targets['cost_efficient'] + 
                              targets['cpu_optimal'] + targets['ram_optimal'] + targets['sla_safe']) >= 3).astype(int)
        
        return targets
    
    def optimize_advanced_models(self, X_train: pd.DataFrame, y_train: np.ndarray) -> Dict[str, Any]:
        """Train and optimize advanced models with extensive hyperparameter tuning"""
        print("Training advanced models with optimized hyperparameters...")
        
        models_config = {
            'XGBoost': {
                'model': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
                'params': {
                    'n_estimators': [100, 200, 300, 500],
                    'max_depth': [3, 4, 5, 6, 8],
                    'learning_rate': [0.01, 0.05, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0],
                    'reg_alpha': [0, 0.1, 0.5],
                    'reg_lambda': [1, 1.5, 2]
                }
            },
            'RandomForest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [200, 300, 500],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', 0.8, 1.0],
                    'class_weight': [None, 'balanced']
                }
            },
            'ExtraTrees': {
                'model': ExtraTreesClassifier(random_state=42),
                'params': {
                    'n_estimators': [200, 300, 500],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2', 0.8],
                    'class_weight': [None, 'balanced']
                }
            },
            'GradientBoosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 4, 5, 6],
                    'learning_rate': [0.05, 0.1, 0.15, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'max_features': ['sqrt', 'log2', None]
                }
            },
            'MLP': {
                'model': MLPClassifier(random_state=42, max_iter=1000),
                'params': {
                    'hidden_layer_sizes': [(100,), (200,), (100, 50), (200, 100), (300, 150, 75)],
                    'activation': ['relu', 'tanh'],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate': ['constant', 'adaptive'],
                    'learning_rate_init': [0.001, 0.01, 0.1]
                }
            }
        }
        
        optimized_models = {}
        
        for model_name, config in models_config.items():
            print(f"\nOptimizing {model_name}...")
            
            # Use RandomizedSearchCV for faster optimization
            search = RandomizedSearchCV(
                config['model'],
                config['params'],
                n_iter=50,  # Reduced for faster execution
                cv=3,
                scoring='f1',
                n_jobs=-1,
                random_state=42,
                verbose=0
            )
            
            search.fit(X_train, y_train)
            
            optimized_models[model_name] = {
                'model': search.best_estimator_,
                'best_params': search.best_params_,
                'best_score': search.best_score_,
                'cv_results': search.cv_results_
            }
            
            print(f"{model_name} - Best CV Score: {search.best_score_:.4f}")
        
        return optimized_models
    
    def create_ensemble_models(self, optimized_models: Dict) -> Dict[str, Any]:
        """Create ensemble models combining the best individual models"""
        print("Creating ensemble models...")
        
        # Select top 3 models for ensembling
        sorted_models = sorted(optimized_models.items(), 
                             key=lambda x: x[1]['best_score'], reverse=True)
        top_models = sorted_models[:3]
        
        print(f"Top models for ensemble: {[name for name, _ in top_models]}")
        
        # Create voting classifier (soft voting for probability-based decisions)
        voting_models = [(name, model_data['model']) for name, model_data in top_models]
        
        ensemble_models = {
            'VotingClassifier_Soft': VotingClassifier(
                estimators=voting_models,
                voting='soft'
            ),
            'VotingClassifier_Hard': VotingClassifier(
                estimators=voting_models,
                voting='hard'
            )
        }
        
        return ensemble_models
    
    def train_multi_objective_models(self, X_train: pd.DataFrame, targets: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Train specialized models for each objective"""
        print("Training multi-objective specialized models...")
        
        specialized_models = {}
        
        # Use the best performing algorithm (from previous optimization) for each objective
        base_model = xgb.XGBClassifier(
            random_state=42,
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            eval_metric='logloss'
        )
        
        for objective, target in targets.items():
            if objective == 'main':
                continue
                
            print(f"Training model for {objective}...")
            
            # Clone and train model for this objective
            model = xgb.XGBClassifier(
                random_state=42,
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                eval_metric='logloss'
            )
            
            model.fit(X_train, target)
            
            specialized_models[objective] = {
                'model': model,
                'target_distribution': np.bincount(target)
            }
        
        return specialized_models
    
    def evaluate_comprehensive(self, models: Dict, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        """Comprehensive evaluation of all models"""
        print("Performing comprehensive evaluation...")
        
        results = {}
        
        for model_name, model_data in models.items():
            model = model_data['model'] if isinstance(model_data, dict) else model_data
            
            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            results[model_name] = {
                'accuracy': accuracy,
                'f1_score': f1,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
            # Feature importance if available
            if hasattr(model, 'feature_importances_'):
                results[model_name]['feature_importance'] = dict(zip(self.feature_columns, model.feature_importances_))
            
            print(f"{model_name} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        
        return results
    
    def create_hybrid_ai_predictor(self, optimized_models: Dict, specialized_models: Dict) -> Dict:
        """Create a hybrid AI predictor that combines multiple models"""
        print("Creating hybrid AI predictor...")
        
        # Select best main model
        best_main_model = max(optimized_models.items(), key=lambda x: x[1]['best_score'])
        
        hybrid_predictor = {
            'main_model': best_main_model[1]['model'],
            'specialized_models': {k: v['model'] for k, v in specialized_models.items()},
            'model_weights': {
                'energy_efficiency': 0.25,
                'cost_efficiency': 0.25,
                'resource_optimization': 0.25,
                'sla_compliance': 0.25
            }
        }
        
        return hybrid_predictor
    
    def save_advanced_models(self, models: Dict, hybrid_predictor: Dict):
        """Save all advanced models and configurations"""
        print("Saving advanced models...")
        
        # Save best individual model
        best_model_name = max(models.items(), key=lambda x: x[1]['accuracy'])[0]
        best_model = models[best_model_name]
        
        joblib.dump(best_model, 'models/advanced_best_model.pkl')
        
        # Save hybrid predictor
        joblib.dump(hybrid_predictor, 'models/hybrid_ai_predictor.pkl')
        
        # Save scalers
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/scaler_{name}.pkl')
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'best_model_name': best_model_name,
            'best_model_accuracy': best_model['accuracy'],
            'best_model_f1': best_model['f1_score'],
            'model_comparison': {name: {'accuracy': data['accuracy'], 'f1': data['f1_score']} 
                               for name, data in models.items()}
        }
        
        with open('models/advanced_models_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Best model: {best_model_name} (Accuracy: {best_model['accuracy']:.4f})")
    
    def train_advanced_pipeline(self) -> Dict:
        """Complete advanced training pipeline"""
        print("Starting advanced AI training pipeline...")
        
        # Load and preprocess data
        X, y, objectives_df = self.load_and_preprocess_data()
        
        # Advanced feature engineering
        X_engineered = self.advanced_feature_engineering(X, objectives_df)
        self.feature_columns = list(X_engineered.columns)
        
        # Scale features with multiple scalers
        X_scaled_dict = {}
        for scaler_name, scaler in self.scalers.items():
            X_scaled_dict[scaler_name] = pd.DataFrame(
                scaler.fit_transform(X_engineered),
                columns=X_engineered.columns
            )
        
        # Use standard scaler for main training
        X_scaled = X_scaled_dict['standard']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Create multi-objective targets
        _, _, objectives_train, objectives_test = train_test_split(
            X_scaled, objectives_df, test_size=0.2, random_state=42
        )
        multi_targets = self.create_multi_objective_targets(objectives_train, y_train)
        
        # Train advanced models
        optimized_models = self.optimize_advanced_models(X_train, y_train)
        
        # Create ensemble models
        ensemble_models = self.create_ensemble_models(optimized_models)
        
        # Train ensemble models
        for name, ensemble in ensemble_models.items():
            ensemble.fit(X_train, y_train)
            optimized_models[name] = {'model': ensemble, 'best_score': 0}
        
        # Train specialized models
        specialized_models = self.train_multi_objective_models(X_train, multi_targets)
        
        # Comprehensive evaluation
        all_models = {**optimized_models, **{f"Specialized_{k}": {'model': v['model']} for k, v in specialized_models.items()}}
        results = self.evaluate_comprehensive(all_models, X_test, y_test)
        
        # Create hybrid predictor
        hybrid_predictor = self.create_hybrid_ai_predictor(optimized_models, specialized_models)
        
        # Save models
        self.save_advanced_models(results, hybrid_predictor)
        
        print("\nAdvanced training pipeline completed!")
        return results

def main():
    """Main training function"""
    trainer = AdvancedVMPlacementModelTrainer()
    results = trainer.train_advanced_pipeline()
    return results

if __name__ == "__main__":
    main()