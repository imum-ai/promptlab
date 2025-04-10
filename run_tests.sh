#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -e .
pip install pytest pytest-asyncio pytest-cov

# Run unit tests
echo "Running unit tests..."
pytest tests/unit -v --cov=src/promptlab
python -m unittest discover tests/unit

# Run integration tests
echo "Running integration tests..."
pytest tests/integration -v

# Run performance tests
echo "Running performance tests..."
pytest tests/performance -v

# Deactivate the virtual environment
deactivate
