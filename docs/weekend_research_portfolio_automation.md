# 주말 Research/Product 포트폴리오 자동화

## 목적

주말 자동화는 단순 Data Scientist 튜토리얼 repo를 만드는 작업이 아니다. 매주 하나의 AI/Data/Product Engineering 포트폴리오 프로젝트를 만들고, 연구 설계와 실제 실행 surface를 함께 갖춘 상태로 고도화한다.

## 최소 품질 기준

현재 `bike-share-demand-resilience` 프로젝트가 모든 주말 포트폴리오 프로젝트의 하한선이다.

- Active quality score floor는 `92.0`에서 시작한다.
- quality score는 전 항목이 active floor를 초과해야 완료 처리한다. floor와 같은 점수면 한 번 더 고도화하고 재측정한다.
- 재측정 결과의 최소 점수가 active floor보다 높으면 그 점수가 새 floor가 된다. 예: `92.0`에서 최소 `94.0`을 달성하면 이후 floor는 `94.0`.
- 이 상향은 postcheck에서 `/workspace/prj/data-scientist-career/scripts/update_quality_floor.py`가 자동 적용한다.
- floor를 넘지 못하면 postcheck에서 `/workspace/prj/data-scientist-career/scripts/update_quality_gap_report.py`가 `docs/research_gap_report.md`의 `Quality Ratchet Gap` 자동 섹션을 갱신한다.
- README/presentation 항목은 최소 `max(94.0, active floor)` 이상이어야 한다.
- `100`점은 존재하지 않는다. 모든 점수는 `0 <= score < 100`이며, `99` 이상은 소수점 단위로 기록한다.
- GitHub `README.md`는 결론-first로 작성하고, 최소 `결론`, `무엇을 만들었나`, `핵심 수치`와 `의미` 열, `얻은 인사이트`, `방법 선택 이유`, `대표 시각화`, `현재 상태`, `실행 방법`, `산출물 확인 방법`, `한계`를 포함한다.
- README는 “무엇을 했고, 결론이 무엇이고, 왜 이 방법을 썼는지”가 바로 보여야 한다. 장황한 배경 설명이나 별도 `면접에서 설명할 포인트` 섹션으로 보완하지 않는다.
- GitHub README에는 `/workspace`, `/DATA/HJ`, `/home/ybs` 같은 로컬 절대경로를 쓰지 않고, `OUTPUT_ROOT`와 상대 경로, 재현 명령으로 안내한다.
- UI/가시성/가독성 기준도 quality gate에 포함한다.
  - 첫 20줄 안에 결론이 있어야 한다.
  - 평균 문단 길이는 180자 이하를 목표로 한다.
  - README 표는 4열 이하로 유지한다.
  - 핵심 수치 표에는 `의미` 열이 있어야 한다.
  - `결론`, `핵심 수치`, `얻은 인사이트`, `방법 선택 이유`, `대표 시각화`가 빠지면 완료 처리하지 않는다.
- 기준 미달이거나 floor와 동점이면 `docs/research_gap_report.md`와 state file에 남기고 완료 처리하지 않는다.

## 토요일 Seed Gate

토요일에는 새 프로젝트 또는 진행 중 seed를 research/product seed까지 만든다.

필수 산출물:

- 주제 후보 5개 이상 평가: `docs/topic_selection.md`
- 데이터 후보 3개 이상 탐색: `docs/data_contract.md`
- 연구 질문 3개 이상: `docs/research_design.md`
- 기본 product surface: `scripts/run_all.sh`, CLI/API/dashboard/batch 중 하나
- 시스템 설계: `docs/system_design.md`
- privacy/publication gate 초안: `docs/privacy_publication_gate.md`
- hiring alignment: `docs/hiring_market_alignment.md`
- 미달 항목 추적: `docs/research_gap_report.md`
- CI 초안: `.github/workflows/ci.yml`

검증:

```bash
python3 /workspace/prj/data-scientist-career/scripts/validate_weekend_project.py \
  --project /workspace/prj/data-scientist-career/<slug> \
  --stage saturday
```

## 일요일 Hardening Gate

일요일에는 seed를 research-grade 또는 production-grade에 가깝게 끌어올린다.

필수 조건:

- 복합 데이터 2개 이상 결합, 또는 불가 사유와 다음 join 계획 문서화
- live status/inventory/incident/price/queue/sensor feed가 있는 도메인은 timestamped snapshot을 저장하고 decision surface에 연결
- leakage-safe split
- baseline과 main model/system benchmark
- ablation 또는 명시적 비교 실험
- uncertainty, robustness, failure audit
- 운영 의사결정 또는 product workflow 연결
- 운영 우선순위 산출물이 있으면 API/dashboard/check mode 등 reviewer가 실행 가능한 product surface 제공
- tests, smoke run, CI
- privacy publication gate 통과
- quality gate 통과 또는 gap report 보강
- GitHub push 가능한 상태
- 배포 가능하면 deploy, 아니면 local production runbook

검증:

```bash
python3 /workspace/prj/data-scientist-career/scripts/validate_weekend_project.py \
  --project /workspace/prj/data-scientist-career/<slug> \
  --stage sunday
```

## 데이터 정책

허용:

- public/open dataset
- 정부/공공 API
- 사내 허가 데이터
- SNS/웹/뉴스/커뮤니티 공개 데이터
- synthetic fallback
- 기존 로컬 프로젝트 산출물

공개 repo 금지:

- raw 내부 데이터
- 개인정보와 재식별 가능한 식별자
- SNS 원문, 댓글 원문, 사용자 ID, profile
- 민감 좌표 원본
- token, API key, cookie, `.env` 값

공개 repo에는 code, schema contract, 익명화/집계 feature 설명, synthetic/public fallback, model card, runbook만 남긴다.

## 운영 및 보고

- Scheduled runner: `/workspace/_codex/scripts/weekend-ds-codex-run.sh`
- Schedule prompt: `/workspace/_codex/schedules/weekend-data-scientist-career-project.md`
- Health helper: `/workspace/_codex/scripts/weekend-ds-codex-health.py`
- Telegram sender: `/workspace/_codex/scripts/send-telegram-message.py`
- Durable state: `/DATA/HJ/prj/data-scientist-career/state/weekend-project-state.md`
- 대표 프로젝트 registry: `/workspace/prj/data-scientist-career/registry/projects.json`
- Notion 메인 포트폴리오 sync: `/workspace/_notion_remodel/scripts/sync_main_portfolio.py`
- GitHub 자동 업로드 hook: `/workspace/_codex/scripts/auto-push-weekend-ds-project.sh`

실행 스케줄:

- 평일 19:10 KST: `weekday-evening` profile로 짧은 증분 작업을 수행한다. 목표는 서울 따릉이 adapter, Decision Impact Simulator, impact-aware guardrail, Control Tower impact card 중 하나를 작은 단위로 전진시키는 것이다.
- 주말 09:00 KST: `weekend` profile로 기존처럼 깊은 E2E 구현, hardening, validation, presentation 개선을 수행한다.
- 평일 run은 22:00 workspace nightly clean과 충돌하지 않도록 timeout을 짧게 둔다.

실패 시 완료 처리하지 않는다. `docs/research_gap_report.md`, state file, Telegram report에 실패 gate와 다음 명령을 남긴다.

## 두 번째 대표 프로젝트 자동 승격

두 번째 대표 프로젝트는 이번 주말 생성/고도화될 research-grade 프로젝트가 실제 gate를 통과한 뒤에만 승격한다. 미리 placeholder를 만들지 않는다.

자동 승격 조건:

- 일요일 hardening gate 통과
- `quality_gate_scores.csv`가 active floor를 초과하거나 gap report로 미달이 명시됨
- public README가 결론-first 구조와 local path 금지 기준을 통과
- raw 내부 데이터, 개인정보, SNS 원문, token, `.env` 값이 공개 repo에 없음
- `registry/projects.json`에 `portfolio_ready`, `monitoring_pending_validation`, `deployment_pending`, `public_ready` 중 하나의 ready status로 등록

자동 반영 흐름:

1. 주말 Codex run이 프로젝트 repo와 `/DATA/HJ` 산출물을 만든다.
2. gate 통과 시 `registry/projects.json`에 두 번째 대표 프로젝트 항목을 추가한다.
3. `weekend-ds-codex-run.sh` postcheck 성공 후 `auto-push-weekend-ds-project.sh`가 registry의 ready 프로젝트를 commit/push한다.
4. 매일 20:20 Notion sync가 registry의 ready 프로젝트를 읽어 `Case Study · <title>` 하위 페이지를 자동 생성한다.
5. 대표 프로젝트가 2개 이상이면 Notion 품질 게이트의 공개 프로젝트 폭 감점이 제거된다.

## 현재 Bike-share 프로젝트 추가 자동화 Gate

`/workspace/prj/data-scientist-career/bike-share-demand-resilience`는 station-level 운영 프로젝트로 고도화되었기 때문에 주말 run 또는 후속 health check에서 아래가 통과해야 한다.

```bash
cd /workspace/prj/data-scientist-career/bike-share-demand-resilience
scripts/run_station_level.sh
scripts/run_station_snapshot_monitor.sh
PYTHONPATH=src python3 -m bike_share_resilience.station_service \
  --output-root /DATA/HJ/prj/data-scientist-career/projects/bike-share-demand-resilience \
  --check
python3 scripts/check_public_deploy_readiness.py \
  --output-root /DATA/HJ/prj/data-scientist-career/projects/bike-share-demand-resilience \
  --report-only
```

이 4개는 각각 station-hour 모델/priority, 2주 snapshot readiness 자동 축적, dashboard/API artifact contract, public deploy gate를 검증한다.
