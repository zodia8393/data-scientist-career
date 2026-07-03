from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    status: str
    docs_url: str
    credential_env: tuple[str, ...]
    response_format: str
    implementation_note: str


PROVIDER_SPECS: dict[str, ProviderSpec] = {
    "saramin": ProviderSpec(
        name="saramin",
        status="implemented",
        docs_url="https://oapi.saramin.co.kr/guide/job-search",
        credential_env=("SARAMIN_ACCESS_KEY",),
        response_format="JSON/XML",
        implementation_note="GET /job-search collector implemented with fixture fallback.",
    ),
    "work24": ProviderSpec(
        name="work24",
        status="planned",
        docs_url="https://www.work24.go.kr/cm/e/a/0110/selectOpenApiIntro.do",
        credential_env=("WORK24_AUTH_KEY",),
        response_format="XML",
        implementation_note="고용24/워크넷 채용정보 XML adapter target.",
    ),
    "wanted": ProviderSpec(
        name="wanted",
        status="planned",
        docs_url="https://openapi.wanted.jobs/",
        credential_env=("WANTED_CLIENT_ID", "WANTED_CLIENT_SECRET"),
        response_format="JSON",
        implementation_note="Wanted Jobs/Companies adapter target after OpenAPI key issuance.",
    ),
    "jobkorea": ProviderSpec(
        name="jobkorea",
        status="approval_required",
        docs_url="https://www.jobkorea.co.kr/service/api",
        credential_env=("JOBKOREA_API_KEY",),
        response_format="XML/call-link",
        implementation_note="공공기관/학교 우선 승인형 호출 링크 adapter target.",
    ),
    "ionejob": ProviderSpec(
        name="ionejob",
        status="optional",
        docs_url="https://www.ibkonejob.co.kr/api/apiService.do",
        credential_env=("IONEJOB_AUTH_KEY",),
        response_format="XML",
        implementation_note="중소기업 채용 보조 provider target.",
    ),
}
