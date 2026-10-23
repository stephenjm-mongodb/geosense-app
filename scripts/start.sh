#!/usr/bin/env bash
set -euo pipefail
mode="${1:-local}"
"$(dirname "$0")/start-$mode.sh"
