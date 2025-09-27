"""
VM Placement Optimization - Model Training Module

This module handles feature engineering, model training, and hyperparameter optimization
for the VM placement prediction system.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
from typing import Dict, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

class VMPlacementModelTrainer:
    def __init__(self, dataset_path: str = "data/vm_placement_dataset.csv"):
        """
        Initialize the model trainer
        
        Args:
            dataset_path: Path to the training dataset CSV file
        """
        self.dataset_path = dataset_path
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.models = {}
        self.best_model = None
        self.feature_importance = {}
        
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Load and preprocess the training data"""
        print("Loading dataset...")
        df = pd.read_csv(self.dataset_path)
        
        print(f"Dataset shape: {df.shape}")
        print(f"Positive samples (optimal placements): {df['is_optimal'].sum()}")
        print(f"Negative samples: {len(df) - df['is_optimal'].sum()}")
        
        # Remove unnecessary columns for training
        feature_cols_to_remove = ['composite_score']  # This is used to generate labels, not for prediction
        
        # Define feature columns (all except target and composite_score)
        self.feature_columns = [col for col in df.columns 
                               if col not in ['is_optimal'] + feature_cols_to_remove]
        
        print(f"Using {len(self.feature_columns)} features for training")
        print("Feature columns:", self.feature_columns[:10], "..." if len(self.feature_columns) > 10 else "")
        
        # Prepare features and target
        X = df[self.feature_columns].copy()
        y = df['is_optimal'].values
        
        # Handle any missing values
        X = X.fillna(X.mean())
        
        return X, y
    
    def feature_engineering(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering techniques"""
        print("Applying feature engineering...")
        
        X_engineered = X.copy()
        
        # Create efficiency ratios
        X_engineered['cpu_efficiency_score'] = 1 - abs(X['cpu_util_after_placement'] - 0.7)  # Optimal around 70%
        X_engineered['ram_efficiency_score'] = 1 - abs(X['ram_util_after_placement'] - 0.7)
        
        # Resource availability features
        X_engineered['total_available_resources'] = (
            (X['host_cpu_cores'] * (1 - X['host_current_cpu_util'])) + 
            (X['host_ram_gb'] * (1 - X['host_current_ram_util'])) / 10  # Scale RAM to similar range as CPU
        )
        
        # Cost efficiency feature
        if 'cost' in X.columns:
            X_engineered['cost_per_cpu'] = X['cost'] / (X['vm_cpu_required'] * X['vm_runtime_hours'])
            X_engineered['cost_per_ram'] = X['cost'] / (X['vm_ram_required'] * X['vm_runtime_hours'])
        
        # Power efficiency feature
        if 'energy_consumption' in X.columns:
            X_engineered['power_per_cpu'] = X['energy_consumption'] / X['host_cpu_cores']
        
        # SLA risk score
        X_engineered['total_sla_risk'] = X['host_sla_risk'] + X['sla_violation_risk']
        
        # Resource utilization balance
        X_engineered['utilization_balance'] = abs(X['cpu_util_after_placement'] - X['ram_util_after_placement'])
        
        # VM complexity score
        X_engineered['vm_complexity'] = X['vm_cpu_required'] * X['vm_ram_required'] * X['vm_sla_requirement']
        
        print(f"Feature engineering complete. New feature count: {len(X_engineered.columns)}")
        return X_engineered
    
    def train_multiple_models(self, X_train: pd.DataFrame, y_train: np.ndarray) -> Dict[str, Any]:
        """Train multiple models and compare performance"""
        print("Training multiple models...")
        
        models = {
            'RandomForest': RandomForestClassifier(random_state=42),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'DecisionTree': DecisionTreeClassifier(random_state=42),
            'SVM': SVC(random_state=42, probability=True),
            'MLP': MLPClassifier(random_state=42, max_iter=500)
        }
        
        model_scores = {}
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            
            # Fit the model
            model.fit(X_train, y_train)
            
            model_scores[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"{name} - CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.models = model_scores
        return model_scores
    
    def optimize_random_forest(self, X_train: pd.DataFrame, y_train: np.ndarray) -> RandomForestClassifier:
        """Optimize Random Forest hyperparameters using Grid Search"""
        print("Optimizing Random Forest hyperparameters...")
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
        
        # Initialize base model
        rf = RandomForestClassifier(random_state=42)
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def evaluate_model(self, model, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        """Evaluate model performance"""
        print("Evaluating model performance...")
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Test Accuracy: {accuracy:.4f}")
        print("\\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance (for tree-based models)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(self.feature_columns, model.feature_importances_))
            self.feature_importance = feature_importance
            
            # Sort features by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            print("\\nTop 10 Most Important Features:")
            for feature, importance in sorted_features[:10]:
                print(f"{feature}: {importance:.4f}")
        
        return {
            'accuracy': accuracy,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'feature_importance': feature_importance,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def plot_feature_importance(self, top_n: int = 15):
        """Plot feature importance"""
        if not self.feature_importance:
            print("Feature importance not available")
            return
        
        # Get top features
        sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:top_n]
        
        features, importance = zip(*top_features)
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(features)), importance)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Feature Importance')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig('results/feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_model(self, model, model_name: str = "vm_placement_model"):
        """Save the trained model"""
        model_path = f"models/{model_name}.pkl"
        scaler_path = f"models/{model_name}_scaler.pkl"
        
        # Save model
        joblib.dump(model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        # Save feature columns and metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'feature_importance': self.feature_importance,
            'model_type': type(model).__name__
        }
        
        with open(f"models/{model_name}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
        print(f"Metadata saved to models/{model_name}_metadata.json")
    
    def train_and_evaluate(self) -> RandomForestClassifier:
        """Complete training and evaluation pipeline"""
        print("Starting VM placement model training pipeline...")
        
        # Load and preprocess data
        X, y = self.load_and_preprocess_data()
        
        # Apply feature engineering
        X_engineered = self.feature_engineering(X)
        
        # Update feature columns list
        self.feature_columns = list(X_engineered.columns)
        
        # Scale features
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_engineered),
            columns=X_engineered.columns
        )
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Train multiple models for comparison
        model_scores = self.train_multiple_models(X_train, y_train)
        
        # Find best model based on CV scores
        best_model_name = max(model_scores.keys(), key=lambda x: model_scores[x]['cv_mean'])
        print(f"\\nBest performing model: {best_model_name}")
        
        # Optimize Random Forest (typically performs well for this type of problem)
        optimized_rf = self.optimize_random_forest(X_train, y_train)
        
        # Evaluate both the best general model and optimized RF
        print("\\n" + "="*50)
        print("OPTIMIZED RANDOM FOREST RESULTS:")
        print("="*50)
        rf_results = self.evaluate_model(optimized_rf, X_test, y_test)
        
        # Set as best model
        self.best_model = optimized_rf
        
        # Save the model
        self.save_model(optimized_rf, "optimized_random_forest")
        
        # Plot feature importance
        self.plot_feature_importance()
        
        print("\\nTraining pipeline completed successfully!")
        return optimized_rf

def main():
    """Main training function"""
    trainer = VMPlacementModelTrainer()
    model = trainer.train_and_evaluate()
    return model

if __name__ == "__main__":
    main()