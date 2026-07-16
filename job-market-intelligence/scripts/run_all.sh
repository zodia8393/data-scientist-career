#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_ROOT="${OUTPUT_ROOT:-/DATA/HJ/prj/data-scientist-career/projects/job-market-intelligence}"

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT_ROOT/reports"
python3 -m job_market_intel --workspace "$OUTPUT_ROOT" demo --profile "$PROJECT_ROOT/profile.example.yaml"
python3 -m pytest --junitxml="$OUTPUT_ROOT/reports/pytest.xml"
