# Portfolio Story

## 한 줄 설명

한국 채용공고 API를 이용해 이직 시장을 데이터 제품처럼 운영하고, 내 프로젝트 evidence와 JD를 연결해 지원 우선순위를 결정하는 시스템이다.

## 왜 만들었나

채용공고 검색은 대부분 수작업과 감에 의존한다. 이 프로젝트는 이 과정을 데이터 사이언스 문제로 재정의한다.

- 시장에는 어떤 DS/AI 직무가 많은가?
- 실제로 어떤 기술스택을 요구하는가?
- 내 포트폴리오가 어떤 공고에 가장 강하게 대응하는가?
- 부족한 skill gap은 무엇인가?
- 지금 지원해야 할 공고와 보류할 공고는 무엇인가?

## 평가자가 볼 수 있는 역량

| 역량 | 프로젝트에서 드러나는 근거 |
|---|---|
| Data engineering | provider 구조, raw 보존, normalized schema, SQLite 저장 |
| Analytics | role, skill, location, experience, deadline 분석 |
| ML/Product judgment | 설명 가능한 fit score와 지원 우선순위 |
| Compliance | 공식 API와 fixture fallback만 사용, 잡플래닛 scraping 제외 |
| Communication | Markdown/HTML report와 JD별 resume bullet 초안 |

## 면접에서 설명할 포인트

1. "채용공고를 단순히 모은 것이 아니라 raw-normalized-scored 계층으로 나눠 재현성을 확보했습니다."
2. "공식 API key가 없어도 fixture demo가 돌아가므로 평가자가 같은 결과를 재현할 수 있습니다."
3. "fit score는 black-box 추천이 아니라 role, skill, domain, experience, location, portfolio evidence, risk penalty로 분해됩니다."
4. "resume bullet은 생성 모델 환각을 피하기 위해 profile에 등록된 프로젝트 evidence만 사용합니다."

## 다음 확장

- 고용24/워크넷 XML provider 구현
- Wanted Jobs provider 구현
- salary parser와 seniority calibration 추가
- Streamlit 또는 FastAPI dashboard로 지원 backlog 운영
- 실제 지원 결과를 feedback label로 저장해 추천 기준 개선
