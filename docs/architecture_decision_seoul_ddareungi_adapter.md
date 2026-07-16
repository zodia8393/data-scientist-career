# Architecture Decision: 서울 따릉이 DecisionOps Adapter

결정일: 2026-07-02 KST  
상태: Accepted

## 결정

DecisionOps AI Suite의 최종 포지셔닝은 다음 구조로 확정한다.

> 기존 미국 bike-share benchmark에서 시작해, 한국 서울 따릉이 공개데이터로 확장 가능한 adapter 구조를 만들고, 실제 공공자전거 운영 문제인 대여 불가, 반납 포화, 재배치 우선순위를 의사결정 제품으로 구현한다.

즉, 최종 산출물은 단순 수요 예측이나 dashboard가 아니라 **서울 따릉이 재배치 의사결정 Control Tower**다.

## 맥락

현재 Stage 1 `bike-share-demand-resilience`는 UCI/Citi Bike 기반으로 forecasting, uncertainty, station-level shortage risk, live snapshot readiness, public deploy gate를 갖춘다. 이 구조는 모델링과 검증의 기준선으로 유용하지만, 포트폴리오 임팩트 측면에서는 한국 도시 운영 문제와 직접 연결되는 설명이 더 강하다.

서울 따릉이는 공개 데이터 기반 확장 대상이 될 수 있다.

- 서울 열린데이터광장 `서울시 공공자전거 따릉이 실시간 대여정보`: 대여소별 대여 가능 자전거 수, 거치율, 위치, 대여소 ID 제공.
  - https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do
- 서울 열린데이터광장 `서울시 공공자전거 따릉이 대여이력 정보`: 년도별, 대여소별, 자전거별 대여이력 원천 데이터 제공.
  - https://data.seoul.go.kr/dataList/OA-15182/F/1/datasetView.do
- 공공데이터포털 `서울특별시 공공자전거 실시간 대여정보`: JSON OpenAPI 등록, 업데이트 주기 실시간으로 안내.
  - https://www.data.go.kr/data/15051891/openapi.do

API key와 인증 필요 여부는 Stage 1 문서 `/workspace/prj/personal/data-scientist-career/bike-share-demand-resilience/docs/seoul_ddareungi_api_keys.md`에 둔다.

## 목표 제품

최종 제품은 다음 질문에 답해야 한다.

- 지금 어떤 대여소가 대여 불가 위험이 큰가?
- 어떤 대여소가 반납 포화 위험이 큰가?
- 제한된 재배치 자원으로 어느 대여소를 먼저 조치해야 하는가?
- 이 추천은 기존 단순 기준보다 shortage hour 또는 overflow hour를 얼마나 줄이는가?
- 데이터가 부족하거나 stale하면 왜 자동화하면 안 되는가?
- 사람이 승인해야 할 action은 무엇이며, 승인 근거와 위험은 무엇인가?

## Architecture

```text
공통 DecisionOps engine
  -> benchmark adapter
       -> UCI system-level demand
       -> Citi Bike station-level demand and live snapshot
  -> seoul_ddareungi adapter
       -> 서울 따릉이 실시간 대여소 상태 snapshot
       -> 서울 따릉이 대여/반납 이력 station-hour 집계
       -> 날씨/공휴일/시간대 feature
       -> 대여 불가/반납 포화 risk 예측
  -> decision impact simulator
       -> baseline policy vs model policy
       -> 자전거/트럭/대여소 수 제약
       -> shortage/overflow 감소 추정
  -> agentic review
       -> evidence citation
       -> NO_GO, stale data, low confidence, unsafe action guardrail
  -> control tower
       -> impact card
       -> review queue
       -> approval history
       -> deployment readiness
```

## 구현 원칙

| 원칙 | 내용 |
|---|---|
| Benchmark first | UCI/Citi Bike는 폐기하지 않고 reproducible benchmark와 offline smoke 기준으로 유지한다. |
| Adapter boundary | 도시별 데이터 차이는 adapter에서 흡수하고, feature/eval/decision simulator/control tower는 공통 contract를 읽는다. |
| Impact before UI polish | 지도 UI보다 baseline 대비 의사결정 개선량을 먼저 만든다. |
| No premature public deploy | 따릉이 실시간 snapshot이 충분히 쌓이기 전에는 public deploy와 성과 claim을 막는다. |
| Human-in-the-loop | 추천 action은 승인 workflow를 거치며, 시스템은 현장 dispatch를 직접 실행하지 않는다. |

## 비목표

- 서울시 운영 시스템에 직접 write 또는 dispatch하지 않는다.
- 따릉이 공개 데이터만으로 실제 운영 성과를 단정하지 않는다.
- LLM chatbot을 먼저 붙이지 않는다.
- 데이터 소스만 늘려 임팩트를 포장하지 않는다.

## 영향

Stage 1은 `SeoulDdareungiAdapter`와 `DecisionImpactSimulator`를 추가하는 방향으로 확장한다.

Stage 2는 agent가 단순 설명이 아니라 `impact`, `evidence`, `NO_GO`, `review_required`를 함께 판단하도록 확장한다.

Stage 3는 review queue에 다음 필드를 노출하는 impact card를 추가한다.

- 추천 action
- 예상 shortage/overflow 감소
- baseline 대비 개선량
- confidence
- evidence
- blocker
- approval/rejection reason

## 수용 기준

최소 수용 기준은 다음과 같다.

- 서울 따릉이 실시간 대여정보 snapshot collector가 존재한다.
- 따릉이 대여이력을 station-hour demand frame으로 변환한다.
- 대여 불가와 반납 포화 위험을 구분한다.
- baseline policy와 model policy를 비교하는 impact report를 생성한다.
- Control Tower가 impact card를 표시한다.
- `NO_GO` 상태에서는 public deploy claim을 차단한다.
