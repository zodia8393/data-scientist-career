from __future__ import annotations

import re
from collections.abc import Iterable


SKILL_PATTERNS: dict[str, tuple[str, ...]] = {
    "Python": (r"\bpython\b", "파이썬"),
    "SQL": (r"\bsql\b",),
    "R": (r"\bR\b", " R "),
    "pandas": (r"\bpandas\b",),
    "NumPy": (r"\bnumpy\b",),
    "scikit-learn": (r"scikit[- ]?learn", r"\bsklearn\b"),
    "PyTorch": (r"\bpytorch\b",),
    "TensorFlow": (r"\btensorflow\b",),
    "ML": (r"\bmachine learning\b", r"\bml\b", "머신러닝", "기계학습"),
    "MLOps": (r"\bmlops\b", "모델 운영"),
    "LLM": (r"\bllm\b", "대규모 언어", "생성ai", "생성 ai"),
    "RAG": (r"\brag\b",),
    "FastAPI": (r"\bfastapi\b",),
    "Docker": (r"\bdocker\b",),
    "Kubernetes": (r"\bkubernetes\b", r"\bk8s\b"),
    "Airflow": (r"\bairflow\b",),
    "Spark": (r"\bspark\b",),
    "DuckDB": (r"\bduckdb\b",),
    "dbt": (r"\bdbt\b",),
    "MLflow": (r"\bmlflow\b",),
    "AWS": (r"\baws\b",),
    "GCP": (r"\bgcp\b", r"google cloud"),
    "Azure": (r"\bazure\b",),
    "BigQuery": (r"\bbigquery\b",),
    "Tableau": (r"\btableau\b",),
    "Power BI": (r"power\s*bi",),
    "A/B testing": (r"\ba/b\b", r"ab test", "실험 설계"),
    "causal inference": (r"causal inference", "인과추론"),
    "time series": (r"time series", "시계열"),
    "forecasting": (r"forecast", "예측"),
    "optimization": (r"optimization", "최적화"),
    "geospatial": (r"geospatial", "공간", "gis"),
    "dashboard": (r"dashboard", "대시보드"),
}


def normalize_token(value: str) -> str:
    return " ".join(value.strip().split())


def extract_skills(text: str | Iterable[str]) -> list[str]:
    if not isinstance(text, str):
        text = " ".join(str(item) for item in text)
    haystack = f" {text} "
    found: list[str] = []
    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, haystack, flags=re.IGNORECASE):
                found.append(skill)
                break
    return sorted(set(found), key=str.lower)


def canonical_skill_set(values: Iterable[str]) -> set[str]:
    aliases = {skill.lower(): skill for skill in SKILL_PATTERNS}
    canonical: set[str] = set()
    for value in values:
        token = normalize_token(str(value))
        canonical.add(aliases.get(token.lower(), token))
    return canonical
