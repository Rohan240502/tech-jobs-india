#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Starting Optimized Sequential Build Process ==="

# 1. Upgrade pip first
echo "[Build] Upgrading pip..."
pip install --upgrade pip --no-cache-dir

# 2. Install numpy (base dependency)
echo "[Build] Installing numpy..."
pip install "numpy>=1.24.0" --no-cache-dir

# 3. Install pandas
echo "[Build] Installing pandas..."
pip install "pandas>=2.0.0" --no-cache-dir

# 4. Install scipy (pre-requisite for scikit-learn)
echo "[Build] Installing scipy..."
pip install "scipy>=1.8.0" --no-cache-dir

# 5. Install scikit-learn
echo "[Build] Installing scikit-learn..."
pip install "scikit-learn>=1.3.0" --no-cache-dir

# 6. Install the remaining lightweight libraries
echo "[Build] Installing remaining requirements..."
pip install -r requirements.txt --no-cache-dir

echo "=== Build Completed Successfully! ==="
