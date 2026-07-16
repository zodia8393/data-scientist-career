# DecisionOps readiness 동기화 작업기록

- 작업일: 2026-07-15 KST
- 대상: `bike-share-demand-resilience`, `agentic-decisionops-workbench`, `decisionops-control-tower`
- 목적: frozen prospective cohort 완료 이후 Stage 1/2/3의 readiness, public claim, endpoint deployment 상태를 실제 산출물과 일치시키고 회귀를 차단한다.

## 방법과 파라미터

1. Citi Bike station snapshot을 cutoff `2026-07-13T14:15:03+09:00`으로 고정해 snapshot analysis를 재생성했다.
2. Frozen cohort의 prospective validation과 public deploy readiness를 실제 `/DATA/HJ` 산출물로 재실행했다.
3. Control Tower와 Workbench를 순서대로 재생성해 최신 Bike/Seoul 상태를 반영했다.
4. Workbench task 기대값과 guardrail을 `blocked`와 `ready_for_claim`, Bike deploy `NO_GO`와 `GO` 양쪽 상태에서 평가하도록 확장했다.
5. Suite verifier가 guarded main/holdout success와 Stage 간 artifact contract를 확인하고, upstream claim readiness와 hosted/public endpoint deployment를 분리해 보고하도록 보강했다.

## 결과

| 항목 | 결과 | 판단 |
|---|---:|---|
| Frozen station snapshots | 340 / 336 | 14.01일 readiness 충족 |
| Source / cutoff 이후 제외 | 361 / 21 | 원본은 보존하고 검증 cohort만 고정 |
| Prospective labels | 817,668 | time-based validation 입력 |
| Prospective validation | `PASS` | persistence baseline F1 0.8286, AP 0.7102, Brier 0.0478 |
| Rolling-origin / drift / failure audit | 3 folds / 4·4 PASS / 6 segments | fold-best F1 평균 0.8477, 최저 segment는 night F1 0.7960 |
| Feature ablation | 3 variants | temporal-only 성능 하락을 확인하고 current-state feature 기여를 분리 |
| Night calibration | `KEEP_PERSISTENCE_BASELINE` | final 전체/night F1 0.8275/0.7953으로 baseline 0.8286/0.7960 미달 |
| Post-cutoff monitoring | 21 snapshots, 4/4 PASS | frozen cohort와 분리, 자동 model 변경 없음 |
| Bike quality floor | 96.0 | 최신 JUnit과 advanced artifact가 있을 때만 10개 category를 96.0으로 승격 |
| Seoul validation | 319 snapshots, 317 evaluated | `READY` |
| Workbench guarded main / holdout | 1.000 / 1.000 | 상태 전이 후 회귀 없음 |
| Workbench claim state | `ready_for_claim` | 자동 공개가 아니라 reviewer approval 대상 |
| Control upstream claim | `GO` | evidence 기반 claim 검토 가능 |
| Control hosted/public endpoint | `NO_GO` | write auth credential 미설정 |
| Suite verifier | errors 0, warnings 3, pending 1 | warning은 세 repo dirty, pending은 write auth |

## 검증

- Root default/explicit tests: `python3 -m pytest -q`, `python3 -m pytest tests -q` → 각각 16 passed
- Bike `scripts/run_all.sh` → 63 tests passed, quality minimum 96.0, verified JUnit freshness `true`
- Workbench tests: `PYTHONPATH=src python3 -m pytest tests -q` → 18 passed
- Control Tower tests: `PYTHONPATH=src python3 -m pytest tests -q` → 31 passed
- Job Market tests: `PYTHONPATH=src python3 -m pytest tests -q` → 11 passed
- Control Tower `scripts/run_all.sh` → API/dashboard/monitoring/deployment readiness와 31 tests 통과
- Workbench `scripts/run_all.sh` → guarded success lift 1.000과 18 tests 통과
- `python3 scripts/verify_decisionops_suite.py` → error 0, warning 3, pending 1
- Docker daemon/Compose read-only preflight → Docker client 29.6.1, server 29.1.3, Compose v5.2.0 확인 및 `docker compose config --quiet` 통과
- Docker resource baseline → 기존 기본 Compose service 1개가 healthy로 실행 중이고 named volume은 없음; smoke는 고유 container/project/image로 격리하도록 보강
- Control write auth preflight → `CONTROL_TOWER_ROLE_TOKENS`, `CONTROL_TOWER_API_TOKEN` 모두 미설정(값은 출력하지 않음)
- Root/Bike/Control 각 `git diff --check` → 통과
- Bike Sunday floor validator (`--ratchet-mode floor`) → minimum 96.0 ≥ active floor 96.0, presentation minimum 96.0, 통과

## 판단과 남은 작업

- Upstream evidence/claim readiness와 외부 endpoint deployment는 별도 상태다. 문서와 registry에서 이를 분리해 표현한다.
- Bike에는 rolling-origin validation, drift/failure EDA, feature ablation, fresh JUnit 근거를 추가했고 quality floor를 95.8에서 96.0으로 ratchet했다. 근거가 사라지면 점수는 기존 92~95 범위로 보수적으로 복귀한다.
- Night calibrated candidate는 final 전체/night F1이 모두 persistence보다 낮아 baseline threshold 0.5를 유지했다. Night 상태 전이율 6.40%는 non-night 4.18%보다 높아 후속 feature/data 리스크로 관리한다.
- Post-cutoff 21 snapshots은 frozen cohort에 합치지 않았고 drift 4/4 PASS를 확인했다. 자동 재학습이나 threshold 변경은 하지 않는다.
- Sunday validator의 strict ratchet mode는 active floor 96.0 초과 개선을 요구하므로 `ratchet_required`이며, 현재 floor 준수 여부는 `--ratchet-mode floor`로 통과했다. 근거 없는 self-score 상향은 하지 않았다.
- Docker/Compose CLI, daemon, 정적 Compose 구성은 실행 가능 상태다. 기존 `decisionops-control-tower` Compose service는 healthy 상태로 보존한다. Smoke는 고유 container/project와 ephemeral image를 사용하지만 container, network, image, 임시 파일 cleanup을 수행하므로 `/workspace` 승인 게이트에 따라 실행하지 않았다. explicit operator approval 이후 `DOCKER_CLEANUP=1 scripts/verify_docker_deployment.sh`와 `COMPOSE_CLEANUP=1 scripts/verify_compose_deployment.sh`를 실행해야 한다. Shared build cache는 다른 build 보호를 위해 prune하지 않는다.
- Control Tower의 local/container demo는 `GO`, hosted/private와 public endpoint는 write auth credential 미설정으로 `NO_GO`다. credential을 임의 생성하거나 외부 배포하지 않았다.
- Commit, push, 외부 배포는 수행하지 않았다.

## 2026-07-16 재개 감사

- `decisionops-control-tower` 기본 Compose service가 외부에서 재생성되어 image ID가 이전 감사와 달라졌고, `2026-07-16T08:30:16+09:00`부터 loopback `127.0.0.1:8093`에서 healthy 상태다.
- `/health`와 `/api/ops-metrics`는 `status=ok`, `demo_mode_ready=true`, `public_deploy_decision=GO`를 반환했다. Runtime write auth는 `auth_required=false`, configured role 0개다.
- 해당 service에는 ephemeral smoke script 실행·cleanup provenance가 없으므로 Docker/Compose smoke 완료 근거로 사용하지 않는다. Registry의 두 smoke 상태는 `approval_pending`을 유지한다.
- 기존 service를 중지·재시작하거나 image를 변경하지 않았으며, 실제 격리 smoke는 explicit operator approval 이후에만 실행한다.
- `2026-07-16T09:25:13+09:00` Seoul validation 319 snapshots/317 evaluated를 기준으로 Workbench→Control을 재생성했다. Workbench 18 tests, Control 31 tests, suite error 0을 재확인했고 각 stage의 실제 modeled units는 Workbench 885, Control 1,007이다.
- `2026-07-16T09:49:50+09:00` 사용자가 격리 Docker/Compose smoke 명령 실행 완료를 보고했다. Post-run 감사에서 ephemeral smoke container/image/network/volume/temp는 0개였고, 기존 기본 Compose service와 `decisionops-control-tower_default` network만 healthy 상태로 보존됐다.
- Smoke 실행 stdout/stderr의 persistent log는 생성되지 않았으므로 실행 성공은 사용자 완료 보고를 근거로 하고, cleanup과 기존 service 무변경은 Docker runtime metadata로 독립 검증했다.

## 최종 완료 감사

- Root default/explicit 16 tests, Bike 63, Workbench 18, Control 31, Job Market 11 tests가 모두 통과했다.
- Bike frozen cutoff public readiness는 340 snapshots, 817,668 labels, blocker 0으로 `GO`; Sunday floor는 minimum 96.0으로 통과했다.
- DecisionOps suite는 error 0, warning 3(existing dirty repos), pending 1(write auth)이다.
- Docker/Compose smoke는 사용자 실행 완료와 post-cleanup 감사로 `PASS` 처리했다. 기존 service는 loopback bind와 healthy 상태를 유지한다.
- Write auth credential은 미설정이므로 hosted/private와 public endpoint는 `NO_GO`를 유지한다. Credential 제공 전에는 추가 실행이 필수가 아니며, 설정 후 `verify_private_demo.py`와 `write_deployment_readiness.py --require-auth --require-docker`를 재실행한다.
- Commit, push, external deploy, 원본 데이터 변경은 수행하지 않았다.
