# Agentic DecisionOps Workbench

## 결론

Bike-share 운영 ML 산출물과 traffic incident decision surface를 AI agent가 읽고, 위험한 자동 실행·공개 배포·근거 부족 요청을 refusal 또는 human review queue로 분기하는 평가 가능한 DecisionOps workbench를 만들었다.

## 핵심 수치

| 항목 | 값 | 의미 |
|---|---:|---|
| Task set | 60 | station, deploy, incident, review queue, cross-domain task |
| Domains | 2 | bike-share operations와 traffic incident decision surface |
| Incident source | NY 511 open data 120 rows | public historical events sample |
| Tool contract | 8 | read-only MCP-style tools/resources/prompts |
| Guarded success | 1.000 | action, tool, review, guardrail, evidence 일치율 |
| Holdout success | 1.000 | main task와 분리한 adversarial prompt 검증 |
| Invalid action | 0.000 | 거부해야 할 요청을 잘못 권고한 비율 |
| Review queue | 42 | 사람이 확인해야 하는 운영 의사결정 건수 |
| Prepublish gate | public_ready | unique prompt, holdout, real/open incident source 통과 |

## 무엇을 만들었나

| 구성 | 설명 |
|---|---|
| Domain adapters | bike-share 산출물과 NY 511 public event sample을 decision surface로 변환 |
| MCP-style tools | risk, readiness, evidence, incident, review queue를 read-only로 노출 |
| Guarded agent | `NO_GO`, 미확인 incident 공개, source conflict, high uncertainty를 차단 |
| Eval harness | baseline과 guarded agent를 metric, failure taxonomy, trace로 비교 |

## 얻은 인사이트

- Agent demo의 핵심은 답변 품질이 아니라 invalid action rate와 evidence citation이다.
- Forecast나 incident score만 있으면 자동화가 아니라 위험한 추천이 된다. 실행 전 guardrail과 reviewer handoff가 필요하다.
- Review queue는 UX 부가기능이 아니라 운영 자동화의 안전 경계다.

## 방법 선택 이유

| 선택 | 이유 |
|---|---|
| Deterministic evaluator | LLM 연결 전에도 회귀 검증과 실패 분석 가능 |
| Cross-domain adapter | 한 도메인 전용 demo가 아니라 DecisionOps 패턴의 일반화 검증 |
| Human review queue | agent 판단을 실제 운영 승인 workflow로 변환 |
| Static trace report | API 배포 전에도 reviewer가 근거와 실패 유형을 확인 |

## 대표 시각화

| 산출물 | 확인 위치 |
|---|---|
| Trace report | `reports/trace_report.html` |
| Eval metrics | `reports/eval_metrics.csv` |
| Guardrail coverage | `reports/guardrail_coverage.csv` |
| Human review queue | `reports/human_review_queue.csv` |

설계 문서는 [docs/system_design.md](docs/system_design.md), 데이터 흐름은 [docs/data_flow_diagram.md](docs/data_flow_diagram.md)에서 확인한다.

## 현재 상태

- Stage: pre-weekend hardening pass
- 의사결정 표면: CLI + reports + review queue
- Quality gate: internal eval/holdout과 prepublish audit 통과
- Next: LLM-backed planner ablation 또는 Stage 3 Control Tower hosted demo hardening

## 실행 방법

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OUTPUT_ROOT=/tmp/agentic-decisionops-workbench
scripts/run_all.sh
```

CLI:

```bash
OUTPUT_ROOT=/tmp/agentic-decisionops-workbench scripts/decisionops eval
```

## 산출물 확인 방법

| 보고 싶은 것 | 명령 | 위치 |
|---|---|---|
| Full run | `scripts/run_all.sh` | `reports/` |
| Tool contract | `scripts/run_all.sh` | `reports/mcp_contract.json` |
| Review queue | `scripts/run_all.sh` | `reports/human_review_queue.csv` |
| Failure taxonomy | `scripts/run_all.sh` | `reports/failure_taxonomy.csv` |

## 한계

- LLM API 호출은 아직 연결하지 않았다.
- Traffic incident surface는 raw CCTV가 아니라 NY 511 공개 historical event sample이다.
- Review queue persistence와 dashboard approval action은 Stage 3 `decisionops-control-tower`에서 제공한다.
- Incident source는 live dispatch authority가 아니므로 출동·공개 action은 계속 human review가 필요하다.
