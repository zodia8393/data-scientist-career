# System Design

## Product surface

CLI batch가 `collect → normalize → score → report`를 실행하고 SQLite가 raw run, normalized jobs, scored jobs를 보존한다. Markdown/HTML dashboard 역할의 static report와 machine-readable JSON/CSV artifact를 함께 만든다.

## API boundary

Provider API adapter는 credential 이름과 timeout을 코드 경계로 관리하며 credential 값은 report와 log에 기록하지 않는다. Fixture provider는 network 없이 같은 interface를 재현한다.

## Deployment

현재 deployment 형태는 local batch와 GitHub CI다. 자동 지원·외부 메시지 전송·hosted write service는 범위 밖이며, 실제 운영 전에는 scheduler, secret store, monitoring runbook이 별도 필요하다.
