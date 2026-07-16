# Data Scientist Career Portfolio

[![Workbench CI](https://github.com/zodia8393/agentic-decisionops-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/zodia8393/agentic-decisionops-workbench/actions/workflows/ci.yml)
[![Bike CI](https://github.com/zodia8393/bike-share-demand-resilience/actions/workflows/ci.yml/badge.svg)](https://github.com/zodia8393/bike-share-demand-resilience/actions/workflows/ci.yml)
[![Control CI](https://github.com/zodia8393/decisionops-control-tower/actions/workflows/ci.yml/badge.svg)](https://github.com/zodia8393/decisionops-control-tower/actions/workflows/ci.yml)

예측 모델을 만드는 데서 끝내지 않고, **검증 가능한 evidence → guarded decision → human approval**로 이어지는 운영형 Data Science 포트폴리오입니다.

> **Release snapshot · 2026-07-16** — Upstream evidence/claim `GO` · Workbench `public_ready` · Local/container demo `GO` · Hosted/public endpoint `NO_GO` (write auth 필요)

## 한눈에 보기

| 프로젝트 | 역할 | 현재 증거 |
|---|---|---|
| [Bike-Share Demand Resilience](https://github.com/zodia8393/bike-share-demand-resilience) | Stage 1 · 예측/검증 | frozen 340 snapshots, F1 0.8286, quality 96.0 |
| [Agentic DecisionOps Workbench](https://github.com/zodia8393/agentic-decisionops-workbench) | Stage 2 · agent/eval/guardrail | main·holdout success 1.000, invalid action 0.000 |
| [DecisionOps Control Tower](https://github.com/zodia8393/decisionops-control-tower) | Stage 3 · reviewer product | 12 impact cards, audit integrity `PASS`, container `GO` |
| [Job Market Intelligence](job-market-intelligence) | Career tool · 공고 분석 | fixture 6→5→4, explainable fit score, 11 tests |

## DecisionOps Suite

| Stage | 입력 → 출력 | 안전 경계 |
|---|---|---|
| 1 · Bike | 수요·inventory → shortage risk와 재배치 후보 | frozen prospective validation 전에는 `NO_GO` |
| 2 · Workbench | ML artifact → evidence-cited guarded decision | dispatch·public posting은 refuse/escalate |
| 3 · Control | review queue → approval history와 deployment gate | write auth 없이는 hosted/public `NO_GO` |

`GO`는 하나의 의미가 아닙니다. 현재 upstream evidence는 공개 검토가 가능하지만, 외부 endpoint 배포는 별도 인증 gate를 통과해야 합니다. 이 구분을 suite verifier와 각 README에서 동일하게 유지합니다.

## 평가자 추천 읽기 순서

1. [Bike 핵심 수치](https://github.com/zodia8393/bike-share-demand-resilience#핵심-수치)에서 모델·cohort·drift 근거를 확인합니다.
2. [Workbench guardrail](https://github.com/zodia8393/agentic-decisionops-workbench#현재-상태)에서 자동 실행을 막는 평가 계약을 봅니다.
3. [Control dashboard](https://github.com/zodia8393/decisionops-control-tower#대표-시각화)에서 reviewer workflow와 audit trail을 확인합니다.
4. [Job Market Intelligence](job-market-intelligence#핵심-수치)에서 포트폴리오와 실제 지원 우선순위의 연결을 봅니다.

## 빠른 검증

```bash
python3 -m pytest -q
python3 scripts/verify_decisionops_suite.py
```

최신 registry는 [registry/projects.json](registry/projects.json), suite 구조는 [docs/decisionops_suite_dfd.md](docs/decisionops_suite_dfd.md), 전체 완료 기록은 [docs/progress/decisionops-readiness-sync-20260715.md](docs/progress/decisionops-readiness-sync-20260715.md)에 있습니다.

<details>
<summary><strong>Portfolio automation과 scaffold</strong></summary>

- 실행 절차: [docs/weekend_local_codex_workflow.md](docs/weekend_local_codex_workflow.md)
- Research/Product 기준: [docs/weekend_research_portfolio_automation.md](docs/weekend_research_portfolio_automation.md)
- Project validator: `scripts/validate_weekend_project.py`

```bash
python3 scripts/scaffold_weekend_project.py \
  --slug example-demand-forecast \
  --title "예시 수요 예측 프로젝트" \
  --problem "공개 데이터로 수요 변동과 운영 리스크를 예측한다." \
  --dry-run
```

</details>

## 문서와 데이터 경계

- 사용자-facing 문서는 한국어를 기본으로 하고 identifier, API, metric은 English를 유지합니다.
- Raw data, model, 대형 생성물은 source repository와 분리하며 Git에는 재현 코드와 경량 evidence만 둡니다.
- Credential, `.env`, 개인 profile 값은 README, report, screenshot에 남기지 않습니다.
