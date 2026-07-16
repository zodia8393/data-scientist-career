# Privacy and Publication Gate

## 개인정보와 PII

공개 채용공고와 사용자가 직접 작성한 profile evidence만 처리한다. 지원자 연락처, 계정 credential, 비공개 지원 결과 같은 PII는 public artifact에 포함하지 않는다.

## Internal 경계

`.env`, 실제 API credential, 개인화된 `profile.yaml`, raw provider response는 internal/local 영역에 둔다. Repository에는 synthetic fixture와 비식별 example profile만 공개한다.

## SNS와 social publication

Fixture의 회사·공고·점수를 실제 시장 통계나 채용 가능성으로 SNS에 게시하지 않는다. 공개 가능한 claim은 pipeline 구조, row-count 재현, 공식 API boundary와 설명 가능한 scoring 방법에 한정한다.
