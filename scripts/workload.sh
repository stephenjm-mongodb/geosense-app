#!/usr/bin/env bash
set -euo pipefail
mode="${1:-local}"
workload="${2:-mixed}"
seconds="${3:-30}"
"$(dirname "$0")/workload-$mode.sh" "$workload" "$seconds"
