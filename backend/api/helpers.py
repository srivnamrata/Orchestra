"""Shared formatting helpers used across multiple routers."""

import json


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _concern_to_dict(concern) -> dict:
    severity = concern.severity.value
    if severity in ("safe", "low"):
        status = "✅ Pass"
    elif severity == "medium":
        status = "⚠️ Flag"
    else:
        status = "🚨 Fail"
    return {
        "status":         status,
        "severity":       severity,
        "detail":         concern.description,
        "evidence":       concern.evidence if isinstance(concern.evidence, list) else [str(concern.evidence)],
        "recommendation": concern.recommendation,
        "confidence":     round(concern.confidence_score, 2),
    }
