#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 -m job_market_intel demo
python3 -m pytest
