# 주말 Research/Product 포트폴리오 로컬 Codex Workflow

이 문서는 `OpenClaw` 예약 실행에 의존하지 않고, 로컬 Codex가 주말마다 AI/Data/Product Engineering 포트폴리오 프로젝트를 생성하고 개선하기 위한 기준 절차입니다. 기본 문서 언어는 한국어이며, code identifier, command, metric, model name, path는 English를 유지합니다.

상세 quality gate는 `docs/weekend_research_portfolio_automation.md`를 기준으로 합니다.

## 실행 스케줄

- 평일: 19:10 KST 이후 `weekday-evening` profile로 짧은 증분 작업을 수행합니다.
- 주말: 09:00 KST에 기존 `weekend` profile로 깊은 구현과 hardening을 수행합니다.
- 현재 승인된 방향은 서울 따릉이 adapter, Decision Impact Simulator, Control Tower impact card입니다.

## 운영 원칙

- 소스 repo는 `/workspace/prj/data-scientist-career/<project-slug>`에 둡니다.
- 데이터, 모델, 큰 그림, 실행 보고서는 `/DATA/HJ/prj/data-scientist-career/projects/<project-slug>`에 둡니다.
- Git에는 재현 코드, 테스트, 경량 문서, 작은 예시 그림만 둡니다.
- `/workspace/.env` 값은 출력하지 않습니다. 필요한 경우 환경 변수 이름만 문서화합니다.
- `sudo`, cron/systemd 변경, 파일 삭제, force-push, 1GB 이상 파일 조작은 하지 않습니다.
- 새 프로젝트는 baseline, validation split, error analysis, reproducibility check가 생기기 전에는 완료로 보지 않습니다.
- 단일 데이터셋 튜토리얼형 프로젝트는 research-grade로 보지 않습니다. 최소 3개 데이터 후보를 조사하고, 가능한 경우 2개 이상 결합합니다.
- raw 내부 데이터, SNS 원문, 사용자 ID, 민감 좌표, token, `.env` 값은 공개 repo에 저장하지 않습니다.

## 주말 실행 흐름

1. `registry/projects.json`에서 직전 프로젝트 상태와 다음 후보를 확인합니다.
2. 새 프로젝트를 시작할 경우 scaffold를 dry-run으로 먼저 확인합니다.
   ```bash
   cd /workspace/prj/data-scientist-career
   python3 scripts/scaffold_weekend_project.py \
     --slug example-demand-forecast \
     --title "예시 수요 예측 프로젝트" \
     --problem "공개 데이터로 수요 변동과 운영 리스크를 예측한다." \
     --dry-run
   ```
3. dry-run 경로가 맞으면 scaffold를 생성합니다.
   ```bash
   python3 scripts/scaffold_weekend_project.py \
     --slug example-demand-forecast \
     --title "예시 수요 예측 프로젝트" \
     --problem "공개 데이터로 수요 변동과 운영 리스크를 예측한다."
   ```
4. 프로젝트 repo 안에서 `README.md`, `docs/topic_selection.md`, `docs/data_contract.md`, `docs/research_design.md`, `docs/modeling_protocol.md`, `docs/system_design.md`, `docs/privacy_publication_gate.md`, `docs/hiring_market_alignment.md`, `docs/reproducibility.md`를 실제 데이터와 실험 기준으로 갱신합니다.
5. 가장 작은 E2E slice를 구현합니다. 최소 요구사항은 다음과 같습니다.
   - 후보 주제 5개 이상 비교
   - 데이터 후보 3개 이상 탐색
   - raw data 보존 및 data contract 기록
   - 복합 데이터 결합 또는 미결합 사유 기록
   - leakage를 피한 train/valid/test split
   - naive 또는 historical baseline
   - 최소 1개 비교 모델 또는 통계 방법
   - ablation 또는 system benchmark
   - uncertainty/robustness/failure audit
   - 운영 의사결정 또는 product workflow 연결
   - holdout metric, segment error audit, limitation 기록
   - `scripts/run_all.sh` 한 번으로 pipeline과 test 실행
6. checklist validator를 실행합니다.
   ```bash
python3 scripts/validate_weekend_project.py \
  --project /workspace/prj/data-scientist-career/example-demand-forecast \
  --stage saturday
```
7. 프로젝트별 테스트를 실행합니다.
   ```bash
   cd /workspace/prj/data-scientist-career/example-demand-forecast
   scripts/run_all.sh
   ```
8. 일요일 hardening 후에는 `--stage sunday` validator를 실행합니다. 결과가 research/product-grade가 되면 `registry/projects.json`에 status, quality gate, 핵심 산출물 경로를 갱신합니다. 미달 항목은 `docs/research_gap_report.md`에 남기고 완료 처리하지 않습니다.

## 로컬 Codex 시작 Prompt

다음 prompt를 새 Codex 세션에 붙여 넣으면 됩니다.

```text
You are local Codex running in /workspace. Take over the weekend research/product portfolio project workflow locally, without OpenClaw runtime dependencies.

Read:
- /workspace/AGENTS.md
- /workspace/_codex/CURRENT_STATE_20260610.md
- /workspace/.workspace-map.json
- /workspace/README.md
- /workspace/prj/data-scientist-career/docs/weekend_local_codex_workflow.md
- /workspace/prj/data-scientist-career/docs/weekend_research_portfolio_automation.md
- /workspace/prj/data-scientist-career/registry/projects.json

Use Korean for user-facing docs/reports. Keep identifiers, commands, model names, metrics, and paths in English.
Keep generated data/artifacts under /DATA/HJ/prj/data-scientist-career/projects/<slug>.
Do not expose /workspace/.env values. Do not delete files, use sudo, change cron/systemd, force-push, or manipulate >1GB files.

Task:
1. Inspect the registry and current project structure.
2. If starting a new project, run scripts/scaffold_weekend_project.py with --dry-run first.
3. On Saturday, create a research/product seed with 5 topic candidates, 3 data candidates, data contract, research design, system design, privacy gate, gap report, CI, and one runnable product surface.
4. On Sunday, harden the project with multi-source data join or documented exception, leakage-safe validation, baseline/model/ablation or benchmark, uncertainty/robustness/failure audit, decision workflow, tests, quality gate, and GitHub-ready docs.
5. Run scripts/validate_weekend_project.py with --stage saturday or --stage sunday, then project tests.
6. Report Done, Verification, Notes, Suggested Next Steps and send the concise result through the configured Telegram sender.
```

## Portfolio-Grade Checklist

| 영역 | 통과 기준 |
|---|---|
| 문제 정의 | target user, decision, metric이 README에 명시됨 |
| 데이터 계약 | source, license/terms, raw path, target, grain, leakage risks 기록 |
| 데이터 결합 | 후보 3개 이상, 결합 2개 이상 또는 합리적 미결합 사유 |
| Baseline | naive 또는 domain baseline이 모델과 같은 split에서 비교됨 |
| Split | random split 금지 대상이면 시간순/group split 등 근거가 있음 |
| Metrics | MAE/RMSE/WAPE/R2 등 문제에 맞는 metric과 단위가 있음 |
| Error analysis | segment별 residual 또는 failure audit이 있음 |
| Uncertainty | CI/bootstrap/conformal/calibration 등 문제에 맞는 불확실성 검증 |
| Product surface | CLI/API/dashboard/web app/batch/monitoring job 중 하나가 실행 가능 |
| Privacy gate | 내부 데이터/SNS/개인정보/secret 공개 위험을 통과 또는 gap 처리 |
| Reproducibility | `scripts/run_all.sh`와 test가 같은 환경에서 재실행 가능 |
| Korean docs | README와 final/model/data 문서는 한국어 설명 중심 |
| Git hygiene | 큰 데이터/모델/중간 산출물은 Git 밖 `/DATA/HJ`에 있음 |
| Review | 한계와 다음 실험이 과장 없이 기록됨 |

## 현재 기준 프로젝트

`bike-share-demand-resilience`는 첫 완료 예제입니다. 다음 프로젝트는 이 repo의 구조를 기준으로 삼되, 주제와 데이터에 맞지 않는 최적화나 conformal interval을 기계적으로 복사하지 않습니다. 새 프로젝트는 먼저 baseline과 검증 설계를 세우고, 분석 가치가 확인된 뒤에 고급 방법을 추가합니다.
