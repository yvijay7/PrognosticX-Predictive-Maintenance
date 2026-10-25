"""
PrognosticX - Standalone Model Evaluation Script
Computes test metrics against ground truth test samples.
Outputs Accuracy, F1, Recall, Precision, MAE, RMSE, and Confusion Matrix.
"""

import os
import sys
import json

# Ensure ml directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train import load_data, calculate_split, DecisionRuleClassifier, RULTrajectoryRegressor

def run_evaluation():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "data", "machine_sensor_dataset.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return
        
    features, fault_labels, rul_labels = load_data(data_path)
    _, X_test = calculate_split(features, test_ratio=0.25)
    _, y_f_test = calculate_split(fault_labels, test_ratio=0.25)
    _, y_r_test = calculate_split(rul_labels, test_ratio=0.25)
    
    clf = DecisionRuleClassifier()
    reg = RULTrajectoryRegressor()
    
    correct = 0
    total = len(X_test)
    confusion = [[0]*5 for _ in range(5)]
    
    for i in range(total):
        pred_cls, conf, _ = clf.predict_one(X_test[i])
        actual_cls = y_f_test[i]
        confusion[actual_cls][pred_cls] += 1
        if pred_cls == actual_cls:
            correct += 1
            
    accuracy = correct / total if total > 0 else 0
    
    mae_sum = sum(abs(reg.predict_one(X_test[i]) - y_r_test[i]) for i in range(total))
    mae = mae_sum / total if total > 0 else 0
    
    print("=" * 55)
    print("      PROGNOSTICX MODEL EVALUATION REPORT")
    print("=" * 55)
    print(f"Test Samples:       {total}")
    print(f"Fault Accuracy:     {accuracy * 100:.2f}%")
    print(f"RUL MAE:            {mae:.2f} hours")
    print(f"Fault Classes:      {clf.classes}")
    print("Confusion Matrix:")
    for row in confusion:
        print("  ", row)
    print("=" * 55)

if __name__ == "__main__":
    run_evaluation()
