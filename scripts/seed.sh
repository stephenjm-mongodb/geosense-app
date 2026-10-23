#!/usr/bin/env bash
set -euo pipefail
mode="${1:-local}"
"$(dirname "$0")/seed-$mode.sh"
