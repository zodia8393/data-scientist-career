# Reproducibility

## Run all

```bash
bash scripts/run_all.sh
```

`OUTPUT_ROOT`를 지정하면 raw data, SQLite, report와 JUnit을 해당 artifact root에 생성한다. 기본 실행은 workspace 밖의 프로젝트 artifact root를 사용한다.

## Test

```bash
python3 -m pytest
python3 -m py_compile job_market_intel/*.py job_market_intel/providers/*.py tests/*.py
```

성공 시 fixture 6건에서 target 5건, deduplicated/scored 4건을 재현하고 `reports/run_summary.json`과 `quality_gate_checks.csv`가 pass를 기록한다.
