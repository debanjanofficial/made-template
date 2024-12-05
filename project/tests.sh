#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running tests for the data pipeline..."


# Run pytest
pytest tests --disable-warnings

echo "All tests passed!"
