# Job Market Intelligence Final Report

## 결론

공식 API boundary와 fixture fallback 아래 raw 6건을 정규화·중복 제거해 4건을 만들고, 4건 모두에 설명 가능한 지원 우선순위를 부여했다.

## 운영 판단

현재 fixture 결과는 pipeline 재현 근거이며 실제 채용시장 통계가 아니다. 실제 지원 판단에는 공식 API로 다시 수집한 결과와 개인 application outcome을 함께 사용해야 한다.

## Artifact contract

- `job_market_report.md`와 `job_market_report.html`: 평가자용 결과
- `run_summary.json`: machine-readable 실행 요약
- `quality_gate_checks.csv`: 관측 가능한 pipeline gate
- `model_card.md`: rule-based ranking의 사용 범위와 한계
- `data_source_and_contract.md`: source·privacy·출력 경계
