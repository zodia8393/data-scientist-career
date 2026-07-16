# Data Scientist Career Portfolio

주말 단위로 데이터 사이언스 포트폴리오 프로젝트와 이직 준비용 개인 도구를 만들고 개선하는 로컬 Codex 작업 영역입니다. 완성된 소스 repo는 `/workspace/prj/personal/data-scientist-career/<project-slug>`에 두고, 데이터·모델·큰 산출물은 `/DATA/HJ/prj/data-scientist-career/projects/<project-slug>`에 둡니다.

## DecisionOps Suite

| slug | 상태 | 요약 |
|---|---|---|
| `bike-share-demand-resilience` | portfolio-ready | 시간대별 공공자전거 수요 예측, 시간순 검증, conformal interval, segment audit, 재배치 최적화 데모 |
| `agentic-decisionops-workbench` | portfolio-ready | 운영 ML 산출물과 NY 511 public incident sample을 MCP-style tools, FastAPI guardrail boundary, holdout eval, review queue로 연결 |
| `decisionops-control-tower` | product-slice-ready | Stage 1/2 산출물을 FastAPI, OpenAPI, SQLite approval history, reviewer dashboard로 묶는 최종 capstone |

2026-07-15 기준 upstream evidence와 claim gate는 `GO`이고, Workbench prepublish는 `public_ready`입니다. Control Tower의 hosted/public endpoint는 별도 운영 gate이며 write auth credential 미설정으로 `NO_GO`입니다. 최신 교차검증 결과는 `/DATA/HJ/prj/data-scientist-career/state/decisionops_suite_status.md`에서 확인합니다.

## 개인 이직 준비 도구

| slug | 상태 | 요약 |
|---|---|---|
| `job-market-intelligence` | demo-ready | 한국 채용공고 공식 API/fixture 기반 DS 이직 시장 분석, fit score, skill gap, resume bullet 추천 시스템. DecisionOps Suite에 묶지 않는다. |

상세 상태와 산출물 경로는 `registry/projects.json`를 기준으로 봅니다. Registry의 `portfolio_track`과 `decisionops_suite` 값으로 DecisionOps 묶음과 개인 이직 준비 도구를 구분합니다.

## 로컬 Codex Workflow

- 절차 문서: `docs/weekend_local_codex_workflow.md`
- Research/Product 자동화 기준: `docs/weekend_research_portfolio_automation.md`
- 프로젝트 registry: `registry/projects.json`
- 새 프로젝트 scaffold: `scripts/scaffold_weekend_project.py`
- checklist validator: `scripts/validate_weekend_project.py`
- DecisionOps suite verifier: `scripts/verify_decisionops_suite.py` (`job-market-intelligence` 제외)

새 프로젝트 dry-run:

```bash
cd /workspace/prj/personal/data-scientist-career
python3 scripts/scaffold_weekend_project.py \
  --slug example-demand-forecast \
  --title "예시 수요 예측 프로젝트" \
  --problem "공개 데이터로 수요 변동과 운영 리스크를 예측한다." \
  --dry-run
```

기존 프로젝트 checklist:

```bash
python3 scripts/validate_weekend_project.py \
  --project /workspace/prj/personal/data-scientist-career/bike-share-demand-resilience \
  --stage sunday
```

DecisionOps suite 상태 확인:

```bash
cd /workspace/prj/personal/data-scientist-career
scripts/verify_decisionops_suite.py
cat /DATA/HJ/prj/data-scientist-career/state/decisionops_suite_status.md
```

## 문서 정책

사용자-facing 문서와 보고서는 한국어를 기본으로 작성합니다. code identifier, command, model name, metric, path는 English를 유지합니다. 큰 생성물은 Git에 넣지 않고 `/DATA/HJ` 아래에 둡니다.

검토자 체크: 이 README/보고서가 사람이 쓴 문체로 읽히는가?(예/아니오)
