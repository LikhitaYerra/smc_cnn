#!/bin/bash

set -e

echo "Running classical SMC simulations..."
python src/simulation/simulate_classical_smc_with_issues.py

echo "Running CNN-adaptive SMC simulations..."
python src/simulation/simulate_adaptive_smc.py

echo "Computing comparison metrics..."
python src/evaluation/compare_classical_vs_adaptive.py
python src/evaluation/compute_adaptive_improvement.py

echo "Generating comparison plots and tables..."
python src/visualization/plot_controller_comparison.py
python src/visualization/plot_metric_bars.py
python src/evaluation/create_report_tables.py

echo "Simulation and evaluation completed."