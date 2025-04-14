#!/bin/bash
# Script to run the SimZ Engine Socket.IO server with environment variables

# Set default environment variables
export SIMZ_HOST=${SIMZ_HOST:-0.0.0.0}
export SIMZ_PORT=${SIMZ_PORT:-5000}
export SIMZ_PROJECT_DIR=${SIMZ_PROJECT_DIR:-./projects}
export SIMZ_DEBUG=${SIMZ_DEBUG:-false}
export SIMZ_CORS_ALLOWED_ORIGINS=${SIMZ_CORS_ALLOWED_ORIGINS:-*}

# Print environment variables
echo "=== SimZ Engine Server Environment ==="
echo "SIMZ_HOST: $SIMZ_HOST"
echo "SIMZ_PORT: $SIMZ_PORT"
echo "SIMZ_PROJECT_DIR: $SIMZ_PROJECT_DIR"
echo "SIMZ_DEBUG: $SIMZ_DEBUG"
echo "SIMZ_CORS_ALLOWED_ORIGINS: $SIMZ_CORS_ALLOWED_ORIGINS"
echo "======================================"

# Run the server
python server.py "$@" 