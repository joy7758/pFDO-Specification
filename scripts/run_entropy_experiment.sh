#!/bin/bash
set -e

echo "Starting Digital Metabolism Entropy Control Experiment..."

# Ensure python path
export PYTHONPATH=$PYTHONPATH:.

# Run the experiment
python3 -m product_api.metabolism.experiment

echo "Experiment completed successfully."
echo "Results saved to:"
echo "- JSON: docs/paper/outputs/"
echo "- Figures: docs/paper/figures/"
