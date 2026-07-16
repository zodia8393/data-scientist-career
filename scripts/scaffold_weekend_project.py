#!/usr/bin/env python3
"""Create a research/product-grade weekend portfolio project scaffold."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SOURCE_ROOT = Path("/workspace/prj/personal/data-scientist-career")
ARTIFACT_ROOT = Path("/DATA/HJ/prj/data-scientist-career/projects")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="kebab-case project directory name")
    parser.add_argument("--title", required=True, help="Korean project title")
    parser.add_argument("--problem", required=True, help="One-sentence Korean problem statement")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT))
    parser.add_argument("--artifact-root", default=str(ARTIFACT_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def validate_slug(slug: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit("slug must be kebab-case using lowercase letters, numbers, and hyphens")
    if slug in {".", ".."}:
        raise SystemExit("invalid slug")


def package_name(slug: str) -> str:
    return slug.replace("-", "_")


def render_files(slug: str, title: str, problem: str, artifact_path: Path) -> dict[str, str]:
    pkg = package_name(slug)
    return {
        "README.md": f"""# {title}

{problem}

## 결론

한 줄로 말하면, **TODO: 어떤 의사결정을 어떤 데이터/모델/제품 surface로 개선했는지 한 문장으로 적습니다.**

- 핵심 결과: TODO
- 의사결정 연결: TODO
- 검증 상태: TODO
- 공개/배포 상태: TODO

## 무엇을 만들었나

| 구성 | 한 줄 설명 |
|---|---|
| 데이터 파이프라인 | TODO: 수집, 정제, 결합, leakage 방지 단위를 설명 |
| 분석/모델 | TODO: baseline과 main method를 같은 split에서 비교 |
| 실패 구간 분석 | TODO: segment, drift, robustness, uncertainty 중 핵심 감사 결과 |
| Product surface | TODO: CLI, API, dashboard, batch, monitoring job 중 reviewer가 실행할 수 있는 표면 |
| 공개 게이트 | TODO: 내부 데이터, 개인정보, SNS 원문, 민감 좌표 공개 차단 기준 |

## 핵심 수치

| 항목 | 값 | 의미 |
|---|---:|---|
| 데이터 규모 | TODO | 분석 단위와 coverage를 한 줄로 설명 |
| 결합 데이터 | TODO | 한 가지 CSV가 아니라 어떤 데이터들이 연결됐는지 설명 |
| Baseline 성능 | TODO | 단순 기준선이 어느 정도인지 설명 |
| Main 성능 | TODO | 개선폭과 실무적으로 의미 있는 차이를 설명 |
| 검증 방식 | TODO | temporal/group/spatial/prospective split 중 왜 적절한지 설명 |
| 실패/불확실성 | TODO | 평균 점수에 가려진 위험 구간을 설명 |
| Product check | TODO | 실행 가능한 의사결정 surface가 있는지 설명 |
| CI/tests | TODO | 재현성과 회귀 방지 상태를 설명 |

## 얻은 인사이트

- TODO: 평균 성능만으로는 알 수 없던 첫 번째 결론.
- TODO: 데이터 결합을 통해 새로 드러난 두 번째 결론.
- TODO: 실제 운영/제품 판단에서 바뀌어야 할 세 번째 결론.

## 방법 선택 이유

| 선택 | 이유 |
|---|---|
| 데이터 결합 전략 | TODO: 왜 이 source와 join key가 문제 정의에 맞는지 설명 |
| 검증 전략 | TODO: 왜 random split이 아니라 leakage-safe split이 필요한지 설명 |
| Baseline | TODO: 복잡한 방법이 필요한지 판단하기 위한 기준 |
| Main method | TODO: 해석력, 성능, 운영 제약 중 무엇 때문에 선택했는지 설명 |
| 불확실성/실패 감사 | TODO: 평균 metric보다 reviewer가 신뢰해야 할 근거 |
| Product surface | TODO: 분석 결과가 실제 사용 흐름으로 이어지는 방식 |

## 대표 시각화

| 문제 구조 | 모델/시스템 결과 | 의사결정 |
|---|---|---|
| TODO | TODO | TODO |

## 현재 상태

- CI: TODO
- Quality gate: TODO
- 배포/공개: TODO
- 남은 blocker: TODO

## Repo 구조

```text
.
├── src/           # pipeline, modeling, product logic
├── scripts/       # one-shot run and checks
├── tests/         # regression and smoke tests
├── docs/          # research/product design docs
├── pyproject.toml
└── requirements.txt
```

대용량 데이터, 모델, report 산출물은 Git에 넣지 않습니다. 산출물 위치는 `OUTPUT_ROOT`로 지정하고, GitHub README에는 재현 명령과 `OUTPUT_ROOT` 기준 상대 위치만 남깁니다.

## 실행 방법

```bash
git clone <repo-url>
cd {slug}
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OUTPUT_ROOT=/tmp/{slug}
scripts/run_all.sh
```

테스트:

```bash
PYTHONPATH=src python3 -m pytest tests -q
```

## 산출물 확인 방법

| 보고 싶은 것 | 명령 | 위치 |
|---|---|---|
| 최종 보고서 | `scripts/run_all.sh` | `reports/final_report.md` |
| 모델/시스템 카드 | `scripts/run_all.sh` | `reports/model_card.md` |
| 데이터 계약 | `scripts/run_all.sh` | `reports/data_source_and_contract.md` |
| 실험 추적 | `scripts/run_all.sh` | `reports/experiment_tracker.csv` |

## 한계

- TODO: 현재 데이터와 검증에서 아직 말할 수 없는 것.
- TODO: 공개 배포 전 반드시 해소해야 할 것.
""",
        "KR_DOCS_POLICY.md": """# 문서 언어 정책

이 프로젝트의 사용자-facing 문서는 한국어를 기본으로 작성합니다. code identifier, command, model name, metric, path는 English를 유지합니다.

- `README.md`, `final_report.md`, `model_card.md`, `data_source_and_contract.md`는 한국어 설명 중심으로 작성합니다.
- 큰 데이터, 모델, 중간 산출물은 Git에 넣지 않고 `/DATA/HJ/prj/data-scientist-career/projects/<slug>`에 둡니다.
- 수치와 판단 근거는 파일 경로, row count, metric 단위와 함께 기록합니다.
- raw 내부 데이터, 개인정보, SNS 원문, 사용자 ID, token, `.env` 값은 공개 repo에 저장하지 않습니다.
""",
        ".github/workflows/ci.yml": f"""name: ci

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt

      - name: Syntax check
        run: python -m py_compile src/{pkg}/pipeline.py tests/test_pipeline.py

      - name: Unit and smoke tests
        env:
          OUTPUT_ROOT: /tmp/{slug}-ci
        run: scripts/run_all.sh
""",
        ".gitignore": """.venv/
__pycache__/
*.pyc
.pytest_cache/
data/
models/
reports/
figures/
""",
        "requirements.txt": """numpy
pandas
scikit-learn
matplotlib
seaborn
scipy
pyarrow
pytest
""",
        "pyproject.toml": f"""[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = "Weekend data science portfolio project."
requires-python = ">=3.10"
dependencies = [
  "numpy",
  "pandas",
  "scikit-learn",
  "matplotlib",
  "seaborn",
  "scipy",
  "pyarrow",
]

[project.optional-dependencies]
dev = ["pytest"]

[tool.setuptools.packages.find]
where = ["src"]
""",
        "docs/data_contract.md": f"""# 데이터 계약

## 목적

`{title}` pipeline이 기대하는 데이터 구조, 원천, 저장 정책을 기록합니다.

## 원천

- 데이터셋 후보: TODO: 최소 3개 후보를 기록합니다.
- 실제 결합 데이터: TODO: 일요일 기준 2개 이상 결합하거나 불가 사유를 남깁니다.
- 원천 URL 또는 위치: TODO
- 라이선스/사용 조건: TODO
- 분석 단위: TODO
- Target: TODO
- Join key: TODO: 시간/공간/엔티티 key, 일반화/익명화 정책
- Row count / 기간 / 단위: TODO

## 저장 정책

| 구분 | 위치 | Git 포함 여부 |
|---|---|---|
| raw data | `{artifact_path}/data/raw/` | 제외 |
| processed data | `{artifact_path}/data/processed/` | 제외 |
| reports | `{artifact_path}/reports/` | 제외 |
| figures | `{artifact_path}/figures/` | 필요 시 경량 사본만 포함 |

## 누수 위험

- TODO: target 이후 정보를 feature로 쓰지 않는지 확인합니다.
- TODO: split 기준과 전처리 적용 순서를 기록합니다.
- TODO: 내부 데이터와 공개 데이터의 join key가 재식별 위험을 만들지 않는지 확인합니다.
- TODO: SNS/웹 원문은 공개 repo에 저장하지 않고 집계 feature만 남깁니다.
""",
        "docs/modeling_protocol.md": """# 모델링 프로토콜

## 목표

TODO: 예측, 분류, 인과 추정, 최적화 중 어떤 문제인지 명시합니다.

## 연구 질문

1. TODO
2. TODO
3. TODO

## 분할 원칙

- TODO: 시간순, group, stratified 등 split 기준을 기록합니다.
- 랜덤 split을 쓰는 경우 누수나 운영 배치와 충돌하지 않는 이유를 남깁니다.

## 기준선과 모델

| 모델 | 역할 |
|---|---|
| TODO baseline | 비교 기준 |
| TODO model | 개선 후보 |

## Ablation

- TODO: base/calendar only
- TODO: public data added
- TODO: internal/web/SNS/event data added, 해당 시
- TODO: lag/rolling/spatial/product layer added

## 평가 지표

- TODO: metric과 단위를 적습니다.

## 불확실성 및 robustness

- TODO: confidence interval, bootstrap, conformal, calibration, drift, domain shift 중 적용 항목을 기록합니다.

## 오류 감사

- TODO: segment별 residual 또는 failure audit 기준을 적습니다.
""",
        "docs/topic_selection.md": f"""# 주제 선정 기록

## 선정된 주제

- 제목: {title}
- 문제: {problem}
- 대상 의사결정: TODO
- 최종 사용자/운영자: TODO

## 후보 평가

토요일 seed 단계에서 최소 5개 후보를 비교합니다.

| 후보 | 도메인 | 데이터 가능성 | 운영/제품 가치 | 연구 난이도 | 채용시장 신호 | 판단 |
|---|---|---|---|---|---|---|
| TODO 1 | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO 2 | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO 3 | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO 4 | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO 5 | TODO | TODO | TODO | TODO | TODO | TODO |

## 제외한 흔한 주제

- 단일 CSV EDA
- 단순 감성분석
- 일반 매출/집값 예측
- 튜토리얼형 benchmark 재현
""",
        "docs/research_design.md": """# 연구 설계

## Research Questions

1. TODO
2. TODO
3. TODO

## Evidence Plan

- 복합 데이터 결합: TODO
- Leakage-safe validation: TODO
- Baseline: TODO
- Main model/system: TODO
- Ablation: TODO
- Uncertainty/robustness: TODO
- Failure audit: TODO
- Decision impact: TODO

## 한계와 윤리

- TODO: 공개 불가 데이터, 개인정보, 내부 데이터, SNS 원문 제한을 명시합니다.
""",
        "docs/system_design.md": f"""# 시스템 설계

## Product Surface

초기 실행 surface는 `scripts/run_all.sh`가 제공하는 batch pipeline/CLI입니다. 프로젝트 성격에 따라 API, dashboard, web app, monitoring job, agent workflow 중 하나로 확장합니다.

## Architecture

```text
data sources -> contracts -> feature pipeline -> baseline/model/benchmark -> evaluation -> decision/product output
```

## Runtime

- Source root: `/workspace/prj/personal/data-scientist-career/{slug}`
- Artifact root: `{artifact_path}`
- Config/env: TODO
- Logging/error handling: TODO
- Deployment/runbook: TODO

## Operations

- Healthcheck: TODO
- Monitoring/drift: TODO
- Retraining or refresh cadence: TODO
""",
        "docs/privacy_publication_gate.md": """# Privacy / Publication Gate

## 공개 금지

- raw 내부 데이터
- 개인정보와 재식별 가능한 식별자
- SNS 원문, 사용자 ID, profile, 댓글 원문
- 민감 좌표 원본
- token, API key, cookie, `.env` 값

## 공개 허용

- 재현 가능한 코드
- schema contract
- public/synthetic sample
- 익명화·집계 feature
- metric, figure, model card, runbook

## Gate Result

| 항목 | 상태 | 근거 |
|---|---|---|
| 내부 데이터 원문 제외 | TODO | TODO |
| 개인정보/식별자 제외 | TODO | TODO |
| SNS 원문 제외 | TODO | TODO |
| secret scan | TODO | TODO |
| public-safe fallback | TODO | TODO |
""",
        "docs/hiring_market_alignment.md": """# Hiring Market Alignment

## 목표 역할

- Data Scientist
- ML/AI Engineer
- Data/Analytics Engineer
- Research Engineer
- Product/Backend Engineer

## 보여줄 역량

| 평가축 | 프로젝트 증거 |
|---|---|
| 문제 정의와 business/product/operation impact | TODO |
| SQL/Python/data engineering | TODO |
| 복합 데이터 수집·정제·결합 | TODO |
| 통계·실험·불확실성 | TODO |
| ML/AI 모델링 또는 system benchmark | TODO |
| API/backend/product delivery | TODO |
| cloud/deployment/runbook | TODO |
| privacy/security judgment | TODO |

## 시장 근거

- TODO: 최신 채용공고, 기술 블로그, 논문/benchmark 확인 결과를 링크와 날짜로 남깁니다.
""",
        "docs/research_gap_report.md": """# Research Gap Report

이 문서는 quality gate를 통과하지 못한 항목을 완료 처리하지 않기 위한 추적표입니다.

| Gate | 현재 상태 | 미달 근거 | 다음 작업 |
|---|---|---|---|
| topic candidates >= 5 | TODO | TODO | TODO |
| data sources explored >= 3 | TODO | TODO | TODO |
| data sources joined >= 2 or documented exception | TODO | TODO | TODO |
| leakage-safe validation | TODO | TODO | TODO |
| baseline/model/ablation or benchmark | TODO | TODO | TODO |
| uncertainty/robustness/failure audit | TODO | TODO | TODO |
| product surface | TODO | TODO | TODO |
| privacy publication gate | TODO | TODO | TODO |
| CI/tests/smoke | TODO | TODO | TODO |
| GitHub/deploy/runbook | TODO | TODO | TODO |
""",
        "docs/reproducibility.md": f"""# 재현 가이드

## 환경

- Python: 3.10 이상
- 산출물 root: `{artifact_path}`

## 실행

```bash
cd /workspace/prj/personal/data-scientist-career/{slug}
pip install -r requirements.txt
scripts/run_all.sh
```

## 검증

```bash
python3 /workspace/prj/personal/data-scientist-career/scripts/validate_weekend_project.py \\
  --project /workspace/prj/personal/data-scientist-career/{slug} \\
  --stage saturday
```

## 성공 기준

- `pytest`가 통과합니다.
- 산출물 root 아래 `reports/run_summary.json` 또는 동등한 실행 요약이 생성됩니다.
- README와 보고서가 실제 실행 결과 기준으로 갱신됩니다.
- 일요일 완료 기준에서는 `--stage sunday` validator와 quality gate를 통과하거나 `docs/research_gap_report.md`에 미달 항목이 남아 있습니다.
""",
        "scripts/run_all.sh": f"""#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
OUTPUT_ROOT="${{OUTPUT_ROOT:-{artifact_path}}}"

cd "$PROJECT_ROOT"
PYTHONPATH=src python3 -m {pkg}.pipeline --output-root "$OUTPUT_ROOT"
python3 -m pytest tests -q
""",
        f"src/{pkg}/__init__.py": '"""Weekend portfolio project package."""\n',
        f"src/{pkg}/pipeline.py": f'''"""Minimal reproducible scaffold pipeline for {title}."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True)
    return parser.parse_args()


def run(output_root: Path) -> Path:
    reports_dir = output_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary = {{
        "project": "{slug}",
        "title": "{title}",
        "status": "scaffold_only",
        "product_surface": "batch_pipeline_cli",
        "quality_gate_stage": "saturday_seed",
        "privacy_publication_gate": "pending",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "next_required_step": "Replace scaffold with real multi-source data contract, leakage-safe validation, baseline/model/ablation or benchmark, uncertainty/failure audit, and product decision output.",
    }}
    summary_path = reports_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary_path


def main() -> None:
    args = parse_args()
    summary_path = run(Path(args.output_root))
    print(f"wrote {{summary_path}}")


if __name__ == "__main__":
    main()
''',
        "tests/test_pipeline.py": f'''from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from {pkg}.pipeline import run


def test_scaffold_pipeline_writes_summary(tmp_path):
    summary_path = run(tmp_path)
    assert summary_path.exists()
    assert "scaffold_only" in summary_path.read_text(encoding="utf-8")
''',
    }


def ensure_project_dir(project_path: Path) -> None:
    if project_path.exists():
        if not project_path.is_dir():
            raise SystemExit(f"project path exists and is not a directory: {project_path}")
        if any(project_path.iterdir()):
            raise SystemExit(f"project path is not empty: {project_path}")


def main() -> None:
    args = parse_args()
    validate_slug(args.slug)
    source_root = Path(args.source_root)
    artifact_root = Path(args.artifact_root)
    project_path = source_root / args.slug
    artifact_path = artifact_root / args.slug
    ensure_project_dir(project_path)
    files = render_files(args.slug, args.title, args.problem, artifact_path)

    print(f"source: {project_path}")
    print(f"artifacts: {artifact_path}")
    print("files:")
    for relative_path in sorted(files):
        print(f"  - {project_path / relative_path}")

    if args.dry_run:
        return

    for directory in [
        project_path,
        artifact_path / "data" / "raw",
        artifact_path / "data" / "processed",
        artifact_path / "reports",
        artifact_path / "figures",
        artifact_path / "models",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    for relative_path, content in files.items():
        target = project_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if relative_path == "scripts/run_all.sh":
            target.chmod(0o755)

    print("created scaffold")


if __name__ == "__main__":
    main()
