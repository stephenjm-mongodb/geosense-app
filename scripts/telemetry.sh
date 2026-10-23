#!/usr/bin/env bash
set -euo pipefail
mode="${1:-local}"
seconds="${2:-30}"
"$(dirname "$0")/telemetry-$mode.sh" "$seconds"
