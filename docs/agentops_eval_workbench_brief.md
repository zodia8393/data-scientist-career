# Agentic DecisionOps Workbench Project Brief

Decision date: 2026-07-02 KST

## Decision

Use the next weekend portfolio slot for `agentic-decisionops-workbench`.

This is the second representative weekend portfolio project. It should sit between `bike-share-demand-resilience` and a general AgentOps platform: use bike-share as the first operational domain, then evaluate how safely and correctly an AI agent turns model outputs into decisions.

This project is not expected to finish in one weekend. The weekend objective is to create a durable research/product seed that can continue across later runs without losing context.

## Working Title

Agentic DecisionOps Workbench: bike-share operational decision agent with MCP-style tools, guardrails, evaluation, and trace observability

## Why This Project

The portfolio needs a project that connects the first project's concrete operations ML system to current AI engineering trends. A standalone agent demo is too abstract; a standalone bike-share forecast is not current enough. The strongest second project is a bridge: an agentic decision workflow that reads bike-share forecasts, uncertainty, inventory snapshots, readiness reports, and deployment decisions, then produces auditable operational recommendations.

This keeps the portfolio story coherent:

- Project 1: `bike-share-demand-resilience` proves operations ML, uncertainty, rebalancing optimization, live snapshots, and deployment gating.
- Project 2: `agentic-decisionops-workbench` proves AI agent engineering on top of that real decision surface: tools, guardrails, human review, traces, and evals.
- Later generalization: the same workbench can add more domain adapters beyond bike-share.

Evidence anchors:

- OpenAI Agents SDK exposes agents, tools, handoffs, guardrails, and tracing as first-class concepts.
- MCP standardizes tools, resources, and prompts as context/tool interfaces for AI applications.
- LangGraph emphasizes durable execution, persistence, streaming, and human-in-the-loop patterns for agent workflows.
- SWE-bench, GAIA, AgentBench, and BFCL show that agent evaluation now focuses on tool use, multi-step task success, action validity, and failure modes rather than only answer accuracy.

## Problem Statement

Operations ML systems often produce forecasts, uncertainty intervals, priority queues, and readiness reports. Human operators still need to interpret them safely. AI agents can help, but teams need a reproducible way to answer:

- Did the agent choose the right operational tool or artifact?
- Did it avoid overconfident action when uncertainty or deployment readiness says `NO_GO`?
- Did it ask for human review when the decision is unsafe or under-evidenced?
- Which bike-share operations scenarios fail, and why?
- Can a reviewer inspect traces and reproduce the agent's recommendation?

This project builds a local workbench that evaluates those questions with bike-share-derived public-safe fixtures plus synthetic tasks.

## Saturday Seed Goal

Create a runnable seed, not a finished product.

Required:

- Evaluate at least 5 bridge-project candidates and document why this one was chosen.
- Define an MCP-style tool contract for bike-share artifacts: forecast, uncertainty, rebalancing priority, inventory snapshot, snapshot readiness, and deployment decision.
- Create 30-50 public-safe tasks covering station prioritization, uncertainty-aware recommendation, deployment refusal, human-review escalation, and report summarization.
- Implement a minimal CLI such as `decisionops run --task <id>` and `decisionops eval`.
- Produce first metrics: task success, tool-call validity, invalid action rate, guardrail hit rate, review-required accuracy, evidence citation rate, latency/cost estimate placeholder.
- Pass the Saturday structural validator.

## Sunday Hardening Goal

Improve quality if time allows. Completion is optional.

Target:

- Implement baseline single-agent and at least one improved workflow, such as guarded tool router, planner-operator-critic, or decision-review agent.
- Add trace records for LLM calls, bike-share artifact reads, tool calls, guardrails, retries, and human-review decisions.
- Add a small dashboard/API or static HTML report for trace and failure inspection.
- Add failure taxonomy and controlled ablation: unguarded agent vs guarded agent, with and without uncertainty/readiness tools.
- Add privacy/publication gate that blocks secrets, local absolute paths in public README, internal raw data, and unsafe tool writes.
- Run tests, smoke command, validator, and quality gate.

## Preferred Architecture

- `src/agentic_decisionops_workbench/`
  - `agents.py`: agent definitions and workflow orchestration.
  - `domain_adapters/bike_share.py`: adapter over bike-share public-safe artifacts.
  - `tools.py`: safe decision tools for forecasts, uncertainty, priority, readiness, and reporting.
  - `mcp_contract.py`: MCP-style tool/resource/prompt schema.
  - `guardrails.py`: policy checks and human-review gates.
  - `evals.py`: deterministic evaluation harness.
  - `tracing.py`: trace event model and local writer.
  - `reports.py`: metrics and dashboard/report generation.
- `tasks/`: bike-share operations scenarios and synthetic/public-safe task set.
- `scripts/run_all.sh`: end-to-end smoke and tests.
- `docs/`: topic selection, data/tool contract, research design, system design, privacy gate, reproducibility, gap report.

## Public-Safety Boundary

Public repo must not contain:

- raw internal files
- secrets, `.env` values, tokens, cookies
- private chat/session contents
- raw user identifiers
- local absolute paths in public README
- destructive write tools

Allowed:

- synthetic task fixtures
- public-safe bike-share derived metrics and schemas
- tool schemas
- anonymized trace examples
- deterministic fake tools
- public documentation citations
- eval metrics and failure taxonomy

## Proposed Quality Signals

- Domain-to-agent bridge: bike-share operations ML artifacts become agent-readable tools.
- Agent/tool-use engineering: MCP-style contract, tool router, guardrails, traces.
- Evaluation engineering: task suite, baseline vs improved workflow, failure taxonomy.
- Product engineering: CLI plus trace dashboard/API/static report.
- Research rigor: ablation, reproducibility, privacy gate, documented limitations.
- Hiring signal: AI Engineer, Agent Engineer, LLM Evaluation Engineer, ML/Product Engineer, Research Engineer.

## First Domain Adapter

Use `bike-share-demand-resilience` as the first domain adapter.

Inputs should be public-safe derived artifacts, not raw private data:

- model metrics and uncertainty summaries
- station rebalancing priority output
- station inventory snapshot fields
- snapshot readiness report
- public deploy readiness report
- final report/model card snippets if needed

Representative tasks:

- Recommend the top station interventions, but cite uncertainty and inventory evidence.
- Refuse deployment when readiness is `NO_GO`.
- Escalate to human review when coverage or uncertainty breaches a threshold.
- Summarize what changed since the previous snapshot.
- Identify when an operator asks for an unsupported or unsafe action.

## Initial Source List

- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- Model Context Protocol specification: https://modelcontextprotocol.io/specification/2025-06-18
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- SWE-bench: https://www.swebench.com/
- Berkeley Function Calling Leaderboard: https://gorilla.cs.berkeley.edu/leaderboard.html
- GAIA benchmark paper: https://arxiv.org/abs/2311.12983
- AgentBench paper: https://arxiv.org/abs/2308.03688

## Non-Goal

Do not spend the weekend chasing a fully deployed SaaS product. The first useful outcome is a strong, reproducible seed with enough architecture and evaluation depth to continue.
