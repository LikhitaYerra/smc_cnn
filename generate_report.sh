#!/bin/bash
# Generate full project report: metrics, plots, tables, PDF
set -e
cd "$(dirname "$0")"

echo "=== Metrics & tables ==="
python3 src/evaluation/compare_classical_vs_adaptive.py 2>/dev/null || true
python3 src/evaluation/compute_adaptive_improvement.py 2>/dev/null || true
python3 src/evaluation/compare_all_controllers.py
python3 src/evaluation/create_report_tables.py 2>/dev/null || true
python3 src/evaluation/create_multi_controller_report_tables.py

echo "=== Plots ==="
python3 src/visualization/plot_controller_comparison.py
python3 src/visualization/plot_summary_dashboard.py
python3 src/visualization/plot_metric_bars.py 2>/dev/null || true
python3 src/visualization/plot_all_controllers_bars.py
python3 src/data_generation/preview_realistic_dataset.py

echo "=== PDF report ==="
python3 src/visualization/generate_project_report_pdf.py

echo ""
echo "Report saved to: results/reports/project_report.pdf"
