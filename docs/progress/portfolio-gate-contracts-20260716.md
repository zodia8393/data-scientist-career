# Portfolio Gate Contracts — 2026-07-16

## 목적

README 최신화 뒤 발견된 Workbench·Control Tower quality floor 불일치, Control smoke token secret-scan false positive, Job Market artifact root 계약 오류를 근거 기반으로 해소한다.

## 방법과 파라미터

- Active quality floor: `96.0`
- JUnit freshness: `24시간 이내`, `tests > 0`, `failures = 0`, `errors = 0`
- Workbench evidence: main/holdout success, guardrail match, prepublish, impact claim boundary, 필수 report, README, JUnit
- Control evidence: upstream eval, 36-row robustness, fresh evidence bundle, audit integrity, action plan, 필수 report/dashboard, README, JUnit
- Job Market: 외부 artifact root 아래 표준 `final_report`, `model_card`, `data_source_and_contract`, `run_summary`, observable quality checks 생성

## 결과

| 프로젝트 | 결과 |
|---|---|
| Workbench | 19 tests, evidence checks 전체 true, quality minimum 96.0 |
| Control Tower | 32 tests, evidence checks 전체 true, quality minimum 96.0, secret scan false positive 제거 |
| Job Market | 11 tests, 6→5→4 fixture funnel, 표준 artifact contract pass |

## 판단 근거

정적 self-score를 올리지 않고 검증 근거가 모두 존재할 때만 active floor를 적용한다. JUnit 또는 필수 evidence가 누락되면 Workbench는 94.9, Control Tower는 95.8의 보수적 baseline으로 자동 복귀한다. Job Market은 DecisionOps Suite 밖의 career tool이므로 96점으로 승격하지 않고 관측 가능한 pass/fail artifact 계약만 추가했다.

## 남은 단계

Hosted/private 및 public endpoint는 role credential이 설정될 때까지 `NO_GO`를 유지한다. Credential 값은 repository, log, report에 기록하지 않는다.
