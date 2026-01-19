#!/bin/bash
# Setup script for Avatar Generation Application
# This script creates virtual environments and installs dependencies for all modules

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Avatar Generation Application Setup ==="
echo ""

# Initialize and update submodules
echo "[1/4] Initializing git submodules..."
git submodule update --init --recursive
echo "Submodules initialized."
echo ""

# Setup measurements_extraction_module
echo "[2/4] Setting up measurements_extraction_module..."
cd "$SCRIPT_DIR/measurements_extraction_module"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "measurements_extraction_module setup complete."
echo ""

# Setup mesh_generation_module
echo "[3/4] Setting up mesh_generation_module..."
cd "$SCRIPT_DIR/mesh_generation_module"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "mesh_generation_module setup complete."
echo ""

# Setup main application
echo "[4/4] Setting up main application..."
cd "$SCRIPT_DIR"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "Main application setup complete."
echo ""

echo "=== Setup Complete ==="
echo ""
echo "Virtual environments created:"
echo "  - .venv (main application)"
echo "  - measurements_extraction_module/.venv"
echo "  - mesh_generation_module/.venv"
