#!/bin/bash
# Major new experiments: fuzzy-SMC, oracle adaptive, RL-adaptive, realistic CNN
set -e
cd "$(dirname "$0")"

echo "=== Step 1: Train RL policy ==="
python3 src/rl/train_rl_policy.py

echo "=== Step 2: Run all controller simulations ==="
python3 src/experiments/run_major_experiments.py

echo "=== Step 3: Generate realistic CNN dataset ==="
python3 src/data_generation/generate_realistic_dataset.py

echo "=== Step 4: Train realistic CNN ==="
python3 src/cnn/train_realistic_cnn.py

echo "=== Step 5: Aggregate multi-controller metrics ==="
python3 src/evaluation/compare_all_controllers.py

echo "Done. See results/metrics/all_controllers_metrics.csv"
