# Job Market Intelligence for DS Career Transition

[![ci](https://github.com/zodia8393/data-scientist-career/actions/workflows/job-market-intelligence-ci.yml/badge.svg)](https://github.com/zodia8393/data-scientist-career/actions/workflows/job-market-intelligence-ci.yml)

[핵심 수치](#핵심-수치) · [대표 결과](#대표-시각화와-결과) · [Quick Start](#설치) · [공식 API](#공식-api-현황) · [검증](#검증)

## 결론

공식 채용공고 API와 fixture fallback을 이용해 Data Scientist / Applied AI / ML Engineer / Product Data Scientist 이직 시장을 수집, 표준화, 분석하고 개인 profile 기반 지원 우선순위를 산출하는 재현 가능한 포트폴리오 프로젝트다.

> **Demo snapshot · 2026-07-16** — Official API boundary · No unauthorized scraping · Fixture 6→5→4 · Explainable scoring · 11 tests passed

## 핵심 수치

| 항목 | 값 | 의미 |
|---|---:|---|
| Provider 구조 | 4개 고려 | Saramin, 고용24/워크넷, Wanted, JobKorea를 공식 API 기준으로 분리 |
| 실제 collector | 1개 | Saramin API는 `SARAMIN_ACCESS_KEY`가 있으면 실제 호출 가능 |
| Fixture demo | 지원 | API key 없이 end-to-end 검증 가능 |
| Demo funnel | 6 → 5 → 4 | raw → DS/AI target → deduplicated/scored jobs |
| 표준 schema | 16+ fields | 공고 출처가 달라도 같은 분석/점수화 파이프라인 사용 |
| Score components | 7개 | role, skill, domain, experience, location, evidence, risk penalty |
| Verified tests | 11 passed | provider, normalization, scoring, reporting 회귀 확인 |

## 무엇을 만들었나

| 구성 | 설명 |
|---|---|
| `collect` | provider별 raw response 수집, retry, timeout, raw 보존 |
| `normalize` | 채용공고 표준 schema 변환, DS/AI 직무 필터, 중복 제거 |
| `score` | `profile.yaml` 기반 fit score, skill gap, 지원 우선순위 계산 |
| `resume_match` | profile에 등록된 프로젝트 evidence만 사용해 JD별 bullet 초안 생성 |
| `report` | 시장 요약, 추천 공고, skill gap, action list를 Markdown/HTML로 출력 |

## 얻은 인사이트

- 이직 포트폴리오에서 중요한 것은 공고를 많이 긁는 것이 아니라, 합법적 source와 재현 가능한 판단 기준이다.
- JD별 fit score는 자기소개서 자동 작성보다 먼저 와야 한다. 지원할 공고와 보완할 skill gap을 먼저 결정해야 한다.
- 잡플래닛 리뷰/평점은 공개 API가 확인되지 않아 제외했다. 이 프로젝트는 무단 scraping 없이 공식 API와 fixture만 사용한다.

## 방법 선택 이유

| 선택 | 이유 |
|---|---|
| SQLite | 별도 서버 없이 raw/normalized/scored row count 검증 가능 |
| Fixture fallback | API key가 없는 평가 환경에서도 demo와 test가 통과 |
| Saramin 우선 구현 | 공개 문서에 `GET /job-search`, JSON 응답, access-key 방식이 명확함 |
| Rule-based scoring | 이력서 포트폴리오에서는 설명 가능한 점수 근거가 black-box 추천보다 강함 |
| Static report | 배포 없이도 README와 산출물만으로 평가자가 확인 가능 |

## 대표 시각화와 결과

```text
official API / fixture
          |
          v
6 raw jobs → 5 DS/AI targets → 4 deduplicated jobs
          |
          v
explainable fit score → skill gap → resume bullet draft → next action
```

| 먼저 볼 것 | 확인할 내용 |
|---|---|
| [Markdown report](reports/job_market_report.md) | 시장 요약, 추천 공고, skill gap, 다음 action |
| [HTML report](reports/job_market_report.html) | 평가자가 바로 열어볼 수 있는 static presentation |
| [Run summary](reports/run_summary.json) | row count와 machine-readable artifact contract |
| [Quality checks](reports/quality_gate_checks.csv) | 설명 가능성·row completeness pass/fail gate |
| [Portfolio story](docs/portfolio_story.md) | 문제 정의부터 career decision으로 이어지는 설명 |
| [API source notes](docs/api_sources.md) | provider별 공식 문서와 인증·scraping 경계 |

## 설치

```bash
git clone https://github.com/zodia8393/data-scientist-career.git
cd data-scientist-career/job-market-intelligence
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

API key를 쓸 경우:

```bash
cp .env.example .env
# .env에 SARAMIN_ACCESS_KEY 등 필요한 값 입력
```

`.env` 값은 출력하거나 commit하지 않는다.

## 실행

API key 없이 전체 demo:

```bash
python3 -m job_market_intel demo
```

요구된 기본 명령:

```bash
python3 -m job_market_intel collect --provider saramin --limit 100
python3 -m job_market_intel normalize
python3 -m job_market_intel score --profile profile.yaml
python3 -m job_market_intel report
python3 -m job_market_intel providers
python3 -m pytest
```

`profile.yaml`이 없으면 example profile을 fallback으로 사용한다. 실제 이직 준비에서는 `profile.example.yaml`을 복사해 개인 profile로 수정한다.

```bash
cp profile.example.yaml profile.yaml
```

## 산출물

| 산출물 | 위치 |
|---|---|
| Raw response | `data/raw/<provider>/*.json` |
| SQLite store | `data/job_market.sqlite` |
| Markdown report | `reports/job_market_report.md` |
| HTML report | `reports/job_market_report.html` |
| 표준 실행 요약 | `reports/run_summary.json` |
| Artifact quality gate | `reports/quality_gate_checks.csv` |
| System/data contract | `reports/model_card.md`, `reports/data_source_and_contract.md` |
| API source notes | `docs/api_sources.md` |
| Portfolio story | `docs/portfolio_story.md` |

## 공식 API 현황

| Provider | 상태 | 인증 |
|---|---|---|
| Saramin | 구현됨 | `SARAMIN_ACCESS_KEY` |
| 고용24/워크넷 | provider 확장 대상 | `WORK24_AUTH_KEY` |
| Wanted | provider 확장 대상 | `WANTED_CLIENT_ID`, `WANTED_CLIENT_SECRET` |
| JobKorea | 승인형 provider 확장 대상 | `JOBKOREA_API_KEY` 또는 발급 호출 링크 |

상세는 [docs/api_sources.md](docs/api_sources.md)를 본다.

## 검증

```bash
python3 -m py_compile job_market_intel/*.py job_market_intel/providers/*.py
python3 -m job_market_intel demo
python3 -m pytest
```

검증 시 확인할 것:

- raw latest item 수와 normalized/scored row 수가 출력된다.
- fixture 6건 중 DS/AI target 5건, 중복 제거 후 4건이 남는다.
- Top 추천 공고마다 score breakdown, skill gap, resume bullet 초안이 생성된다.

## Repository Guide

| 경로 | 역할 |
|---|---|
| [`job_market_intel`](job_market_intel) | collector, normalization, scoring, reporting package |
| [`job_market_intel/providers`](job_market_intel/providers) | provider별 공식 API adapter와 fixture fallback |
| [`tests`](tests) | provider·schema·score·report regression |
| [`docs`](docs) | API source, data contract, portfolio story |
| [`reports`](reports) | 재현 가능한 Markdown/HTML demo output |

## 한계

- Saramin 외 provider는 공식 문서와 인증 구조만 정리했고 collector는 확장 지점으로 남겼다.
- salary parsing은 원문 보존 중심이며, 정량 salary score는 아직 보수적으로 제외했다.
- resume bullet은 profile evidence만 사용하므로 profile이 빈약하면 초안도 제한된다.
