# Data Contract

## Source와 license

입력은 provider가 허용한 공식 API response 또는 repository의 synthetic fixture만 사용한다. 각 provider의 license와 이용 조건은 `api_sources.md`에서 확인하며 무단 scraping은 허용하지 않는다.

## Join과 정규화

Provider별 raw field를 공통 job schema로 변환하고, fingerprint로 중복을 제거한 뒤 profile evidence와 join한다. Raw response는 원형을 보존한다.

## Leakage 경계

Fixture 결과를 실제 시장 통계로 해석하지 않는다. 개인 application outcome을 향후 calibration에 사용할 경우 시간 순서 split을 적용하고 미래 합격 결과가 과거 ranking feature로 누수되지 않게 한다.
