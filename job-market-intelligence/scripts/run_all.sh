#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_ARTIFACT_PARENT="${LOCAL_ARTIFACT_PARENT:-/DATA/HJ/prj/data-scientist-career/projects}"
if [[ -z "${OUTPUT_ROOT:-}" ]]; then
  if [[ -d "$LOCAL_ARTIFACT_PARENT" && -w "$LOCAL_ARTIFACT_PARENT" ]]; then
    OUTPUT_ROOT="$LOCAL_ARTIFACT_PARENT/job-market-intelligence"
  else
    OUTPUT_ROOT="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/job-market-intelligence"
  fi
fi

cd "$PROJECT_ROOT"
mkdir -p "$OUTPUT_ROOT/reports"
python3 -m job_market_intel --workspace "$OUTPUT_ROOT" demo --profile "$PROJECT_ROOT/profile.example.yaml"
python3 -m pytest --junitxml="$OUTPUT_ROOT/reports/pytest.xml"
