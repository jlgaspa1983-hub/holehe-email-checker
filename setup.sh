#!/bin/bash
# Setup script for holehe automation

echo "=== Holehe Email Checker Setup ==="
echo ""

# Check Python version
echo "Checking Python installation..."
python --version || python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install holehe httpx trio pytest pytest-trio

# Verify installation
echo ""
echo "Verifying holehe installation..."
holehe --help

echo ""
echo "✓ Setup complete! You can now run:"
echo "  python run_holehe_check.py"
echo "  python bulk_email_checker.py"
echo "  pytest test_holehe.py -v"
