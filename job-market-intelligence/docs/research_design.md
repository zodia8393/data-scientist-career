# Research Design

## 연구 질문

공식 API만 사용하면서도 서로 다른 채용공고를 공통 schema로 정규화하고, 개인 profile 근거에 따라 다음 지원 action을 설명 가능하게 정렬할 수 있는가?

## Ablation

향후 실제 데이터에서는 role match, skill match, evidence match를 하나씩 제거해 ranking 변화와 지원 결과의 차이를 비교한다. 현재 fixture는 pipeline contract 검증용이므로 성능 우위를 주장하지 않는다.

## Uncertainty

급여·경력·공고 본문 누락, provider coverage 차이, fixture와 실제 시장의 분포 차이를 uncertainty source로 기록한다. 정보가 부족한 공고는 자동 지원하지 않고 monitoring 대상으로 남긴다.
