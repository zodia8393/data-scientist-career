# DecisionOps AI Suite Strategy

Decision date: 2026-07-02 KST

## Direction

Build a connected portfolio suite for Data Scientist, AI/ML Product DS, Applied AI, and ML Engineer roles.

Positioning:

> I build measurable AI decision systems: from operational forecasting to agentic review, guardrails, traceable evaluation, and deployable product workflows.

Final product thesis:

> Start from a reproducible US bike-share benchmark, add an adapter path for Seoul Ddareungi public data, and turn the real Korean public-bike operation problem of rental shortage, return overflow, and rebalancing priority into a DecisionOps product.

This is not a set of unrelated demos. The suite must show a progression from model quality to agentic decision quality to deployable product quality.

Architecture decision: [architecture_decision_seoul_ddareungi_adapter.md](architecture_decision_seoul_ddareungi_adapter.md)

## Portfolio Suite

| Stage | Project | Role | Portfolio signal |
|---:|---|---|---|
| 1 | `bike-share-demand-resilience` | Operations ML engine | Benchmark forecasting, Seoul adapter path, uncertainty, validation, impact simulation |
| 2 | `agentic-decisionops-workbench` | Agentic decision/evaluation layer | MCP-style tools, guardrails, human review, traces, agent evals |
| 3 | `decisionops-control-tower` | Deliverable product capstone | API, dashboard, impact card, review queue, monitoring, deployment runbook |

## Non-Generic Standard

Avoid:

- A notebook-only forecasting project.
- A chatbot that only summarizes tables.
- A dashboard that only displays charts.
- A generic agent demo without evaluation.
- A polished UI without reproducible pipelines, tests, and operational gates.

Require:

- Decision value: every output must answer what action changes.
- Evaluation: every model/agent/product layer must have measurable checks.
- Evidence: recommendations must cite data/tool outputs, not unsupported claims.
- Guardrails: unsafe action, weak evidence, and deployment `NO_GO` must block automation.
- Observability: traces, logs, metrics, and failure taxonomy must be inspectable.
- Delivery: final capstone must be runnable through documented commands, API smoke tests, auth boundary, and container packaging.

## Stage 1: Operations ML Engine

Project: `bike-share-demand-resilience`

Purpose:

Build the underlying decision signal.

Required maturity:

- Leakage-safe forecasting and validation.
- Uncertainty or conformal interval reporting.
- Segment/failure audit.
- Rebalancing priority or operating decision output.
- Live status/inventory snapshot readiness.
- Deploy readiness gate.
- Adapter boundary for Seoul Ddareungi public data.
- Decision impact simulator that compares baseline and model-driven rebalancing policies.

Role in suite:

This is the factual substrate. Later agents and dashboards must not invent signals; they read this project's derived public-safe artifacts. UCI/Citi Bike remain the reproducible benchmark path, while Seoul Ddareungi is the target Korean operations adapter.

## Stage 2: Agentic DecisionOps Workbench

Project: `agentic-decisionops-workbench`

Purpose:

Test whether an AI agent can safely interpret operations ML artifacts and make auditable recommendations.

Required maturity:

- Bike-share domain adapter as the first adapter.
- MCP-style contract for resources, tools, and prompts.
- Synthetic/public-safe task set.
- Baseline agent and guarded agent comparison.
- Guardrails for deployment `NO_GO`, high uncertainty, missing evidence, unsafe writes, and unsupported requests.
- Human-review escalation.
- Trace records for tool calls, evidence, guardrail hits, retries, and final decisions.
- Metrics: task success, tool-call validity, invalid action rate, guardrail hit rate, review-required accuracy, evidence citation rate.
- Impact-aware review: low-impact, stale, weak-evidence, or `NO_GO` recommendations must be escalated or refused.

Role in suite:

This proves modern Applied AI skill without becoming an empty agent demo. The agent is grounded in the real Stage 1 decision surface.

## Stage 3: DecisionOps Control Tower

Project: `decisionops-control-tower`

Purpose:

Package the model and agent layers into a deployable product-quality control surface.

Required maturity:

- FastAPI or equivalent API service.
- Dashboard or app for operating review.
- Endpoints for health, station risk, recommendations, traces, readiness, and review queue.
- Dockerfile, compose, `.env.example`, CI, smoke tests, OpenAPI docs, RBAC-lite writes, structured logs, monitoring snapshots, deployment readiness gate, and deployment runbook.
- Demo data mode that works without private credentials.
- Monitoring/logging for model freshness, snapshot freshness, agent failures, guardrail hits, and review queue status.
- Privacy/publication gate.
- Impact cards that show recommended action, expected shortage/overflow reduction, baseline comparison, confidence, evidence, blockers, and approval status.

Role in suite:

This is the deliverable capstone. It should look like a small product that could be handed to a stakeholder or hiring reviewer, not a collection of scripts.

## Architecture Narrative

Suite 전체 데이터 흐름도(DFD): [decisionops_suite_dfd.md](decisionops_suite_dfd.md)

```text
US bike-share benchmark + Seoul Ddareungi adapter
    -> demand, inventory, weather, calendar, station-hour features
    -> shortage/overflow risk, uncertainty, readiness artifacts
    -> baseline vs model policy impact simulation
    -> agentic decision tools, guardrails, trace/eval reports
    -> control tower API, impact cards, review queue, monitoring
```

## Hiring Narrative

For Data Scientist:

- Lead with Stage 1.
- Emphasize leakage-safe validation, uncertainty, interpretation, and operating decisions.

For AI/ML Product DS:

- Lead with the suite narrative.
- Emphasize the path from model output to product decision workflow.

For Applied AI / Agent Engineer:

- Lead with Stage 2.
- Emphasize MCP-style tools, guardrails, evals, traces, and human review.

For ML Engineer:

- Lead with Stage 3.
- Emphasize API, CI, deployment, monitoring, reproducibility, and runbooks.

## Quality Gates

The suite is acceptable only when:

- Each stage has a conclusion-first README.
- Each stage has `scripts/run_all.sh` or equivalent one-shot verification.
- Public README files avoid local absolute paths.
- Raw internal data and secrets are excluded.
- Stage 2 explicitly compares unguarded and guarded behavior.
- Stage 3 can run locally with demo data.
- Final documentation explains how the three projects connect.

## Near-Term Execution

1. Keep `bike-share-demand-resilience` in monitoring mode until current station snapshot readiness unblocks.
2. Add the Seoul Ddareungi adapter path: real-time station snapshot collector, trip-history station-hour aggregation, and shortage/overflow labels.
3. Add the Decision Impact Simulator: baseline policy vs model policy, limited rebalancing budget, expected shortage/overflow reduction, false-alarm cost.
4. Keep `agentic-decisionops-workbench` as the evaluated Stage 2 bridge and make it impact-aware before adding an LLM-backed planner.
5. Use `decisionops-control-tower` as the Stage 3 local product slice and add impact cards before UI polish or hosted demo hardening.
6. Keep public deploy `NO_GO` until upstream readiness, prospective validation, and production hardening are complete.
