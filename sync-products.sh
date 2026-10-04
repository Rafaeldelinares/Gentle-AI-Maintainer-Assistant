#!/usr/bin/env bash
# Thin wrapper. The pins and the implementation live in tools/vendor.py, because a pin in two
# places is a pin that drifts. Kept under this name so every existing document stays valid.
set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/tools/vendor.py" --full
