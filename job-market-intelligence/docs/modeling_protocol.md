# Modeling Protocol

## Baseline

Baseline은 모든 target 공고를 동일 우선순위로 보는 방식이다. 현재 rule-based model은 role, skill, domain, experience, location, profile evidence와 risk penalty를 합산해 설명 가능한 fit score를 만든다.

## Split

현재 fixture demo는 학습 모델이 아니므로 train/test split을 주장하지 않는다. 실제 지원 결과가 축적되면 지원 시점을 기준으로 chronological split을 사용한다.

## Metric

현재 gate는 raw·normalized·scored row count, 전체 공고 scoring 여부, score breakdown과 resume evidence 완전성을 측정한다. 향후 calibration metric은 ranking precision과 application outcome을 분리해 기록한다.
