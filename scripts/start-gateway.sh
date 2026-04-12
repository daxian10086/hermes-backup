#!/bin/bash

# This script sets up environment variables and starts OpenClaw Gateway

# Set necessary environment variables from current environment or defaults
export OPENCLAW_STATE_DIR=/workspace/projects
export COZE_INTEGRATION_MODEL_BASE_URL="${COZE_INTEGRATION_MODEL_BASE_URL:-https://integration.coze.cn/api/v3}"
export COZE_WORKLOAD_IDENTITY_API_KEY="${COZE_WORKLOAD_IDENTITY_API_KEY}"

# Change to project directory
cd /workspace/projects

# Start gateway
exec openclaw gateway run --port 5000 --allow-unconfigured --force
