#!/usr/bin/env bash
set -euo pipefail
python3 scripts/generate_telemetry.py "${1:-30}"
