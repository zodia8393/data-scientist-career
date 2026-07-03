# API Sources

이 문서는 2026-07-03 기준 공식 문서에서 확인한 provider별 사용 계획이다.

## Saramin

- 공식 문서: https://oapi.saramin.co.kr/guide/job-search
- 인증: 이용신청 승인 후 `access-key` 발급
- 구현 상태: `job_market_intel.providers.saramin.SaraminProvider`
- 요청: `GET https://oapi.saramin.co.kr/job-search`
- 응답: `Accept: application/json` 또는 XML
- 주요 parameter:
  - `access-key`
  - `keywords`
  - `start`
  - `count`
  - `sort`
  - `fields`
- 현재 collector는 `fields=posting-date expiration-date count`, `sort=pd`를 사용한다.

## 고용24 / 워크넷

- 공식 문서: https://www.work24.go.kr/cm/e/a/0110/selectOpenApiIntro.do
- 인증: 고용24 기업회원 가입 후 Open API 인증키 신청, 담당자 심사 후 발급
- 응답: HTTP 기반 XML
- 주요 채용 API:
  - 채용정보
  - 채용행사
  - 공채속보
  - 공채기업정보
- 구현 상태: provider 확장 대상

## Wanted

- 공식 문서: https://openapi.wanted.jobs/
- 인증: OpenAPI 인증 신청 후 key 발급
- 주요 API:
  - Companies
  - Jobs
  - Tags
  - Search
  - Stat
- 구현 상태: provider 확장 대상

## JobKorea

- 공식 문서: https://www.jobkorea.co.kr/service/api
- 제공 대상: 공공기관/학교 우선, 개인 또는 일반 기업은 내부 검토 대상
- 내용:
  - 채용정보 API
  - 신입공채 API
  - 공채달력 iframe
- 구현 상태: 승인형 provider 확장 대상
- 주의: 호출 링크 발급 방식이라 일반 API key provider와 다르게 adapter가 필요하다.

## Excluded: Jobplanet

잡플래닛 기업리뷰, 연봉, 평점 데이터는 공개 API가 확인되지 않았다. 공식 서비스 하단에는 무단 전재, 무단 수집, 재배포, AI 학습 이용 금지 문구가 있으므로 이 프로젝트의 수집 대상에서 제외한다.
