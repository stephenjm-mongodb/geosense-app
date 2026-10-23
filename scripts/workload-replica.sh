#!/usr/bin/env bash
set -euo pipefail
python3 scripts/run_workload.py "${1:-mixed}" "${2:-30}"
