#!/bin/bash

set -e

echo "======================================"
echo "AI-SMC Autonomous Robot Project"
echo "Running full experiment pipeline"
echo "======================================"

echo ""
echo "Step 1: Generate CNN dataset"
python src/data_generation/generate_dataset.py

echo ""
echo "Step 2: Split dataset"
python src/data_generation/split_dataset.py

echo ""
echo "Step 3: Train CNN"
python src/cnn/train_cnn.py

echo ""
echo "Step 4: Test CNN"
python src/cnn/test_cnn.py

echo ""
echo "Step 5: Run classical SMC scenarios"
python src/simulation/simulate_classical_smc_with_issues.py

echo ""
echo "Step 6: Run CNN-adaptive SMC scenarios"
python src/simulation/simulate_adaptive_smc.py

echo ""
echo "Step 7: Compare classical SMC vs CNN-adaptive SMC"
python src/evaluation/compare_classical_vs_adaptive.py

echo ""
echo "Step 8: Compute adaptive improvement"
python src/evaluation/compute_adaptive_improvement.py

echo ""
echo "Step 9: Generate comparison plots"
python src/visualization/plot_controller_comparison.py

echo ""
echo "Step 10: Generate metric bar charts"
python src/visualization/plot_metric_bars.py

echo ""
echo "Step 11: Generate report tables"
python src/evaluation/create_report_tables.py

echo ""
echo "======================================"
echo "Full experiment pipeline completed."
echo "Results saved in:"
echo "- results/metrics/"
echo "- results/plots/"
echo "- results/tables/"
echo "======================================"