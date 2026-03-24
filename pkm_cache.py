import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

import requests

AIRTABLE_URL = "https://api.airtable.com/v0"


def _get_config():
    return (
        os.getenv("AIRTABLE_API_KEY"),
        os.getenv("AIRTABLE_BASE_ID"),
        os.getenv("AIRTABLE_PKM_TABLE", "PKM_Cache"),
    )


def _headers():
    api_key, _, _ = _get_config()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _table_url():
    _, base_id, table = _get_config()
    return f"{AIRTABLE_URL}/{base_id}/{table}"


def make_cache_key(text: str) -> str:
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]


def get_cached(cache_key: str) -> Optional[dict]:
    url = _table_url()
    params = {
        "filterByFormula": f'{{cache_key}}="{cache_key}"',
        "maxRecords": 1,
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=10)
    r.raise_for_status()
    records = r.json().get("records", [])
    if not records:
        return None
    fields = records[0]["fields"]
    record_id = records[0]["id"]
    _increment_hit(record_id, fields.get("hit_count", 0))
    return fields


def store_result(
    cache_key: str,
    result: dict,
    linkedin_url: str = "",
    profile_text: str = "",
    source: str = "text_paste",
) -> str:
    url = _table_url()
    body = {
        "fields": {
            "cache_key": cache_key,
            "linkedin_url": linkedin_url,
            "profile_text": profile_text,
            "detected_mode": result.get("detected_mode", ""),
            "confidence": result.get("confidence", 0),
            "reasoning": result.get("reasoning", ""),
            "awareness_score": result.get("awareness_score", 0),
            "bypass_strategy": result.get("bypass_strategy", ""),
            "forbidden_phrases": json.dumps(result.get("forbidden_phrases", [])),
            "generated_message": result.get("generated_message", ""),
            "hit_count": 0,
            "source": source,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
    }
    r = requests.post(url, headers=_headers(), json=body, timeout=10)
    r.raise_for_status()
    return r.json()["id"]


def _increment_hit(record_id: str, current: int):
    url = f"{_table_url()}/{record_id}"
    try:
        requests.patch(
            url,
            headers=_headers(),
            json={"fields": {"hit_count": current + 1}},
            timeout=5,
        )
    except Exception:
        pass


def _feedback_url():
    api_key, base_id, _ = _get_config()
    return f"{AIRTABLE_URL}/{base_id}/PKM_Feedback"


def store_feedback(
    cache_key: str,
    detected_mode: str,
    rating: str,
    correct_mode: str = "",
    profile_preview: str = "",
):
    body = {
        "fields": {
            "cache_key": cache_key,
            "detected_mode": detected_mode,
            "correct_mode": correct_mode,
            "rating": rating,
            "profile_preview": profile_preview[:200],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    }
    try:
        r = requests.post(_feedback_url(), headers=_headers(), json=body, timeout=10)
        r.raise_for_status()
    except Exception:
        pass


def get_correction_patterns() -> list:
    """Fetch recent corrections (thumbs down + correct_mode provided) to inject into prompts."""
    try:
        r = requests.get(
            _feedback_url(),
            headers=_headers(),
            params={
                "filterByFormula": 'AND({rating}="down",{correct_mode}!="")',
                "sort[0][field]": "created_at",
                "sort[0][direction]": "desc",
                "maxRecords": 50,
            },
            timeout=10,
        )
        r.raise_for_status()
        records = r.json().get("records", [])
        return [
            {
                "profile": r["fields"].get("profile_preview", ""),
                "detected_as": r["fields"].get("detected_mode", ""),
                "actually_was": r["fields"].get("correct_mode", ""),
            }
            for r in records
            if r["fields"].get("correct_mode")
        ]
    except Exception:
        return []


def get_stats() -> dict:
    """Get aggregate stats: total analyses, per-mode counts, accuracy from feedback."""
    stats = {"total_analyses": 0, "total_feedback": 0, "modes": {}, "accuracy": 0}
    try:
        # Count total analyses
        r = requests.get(
            _table_url(),
            headers=_headers(),
            params={"fields[]": "detected_mode", "pageSize": 100},
            timeout=10,
        )
        r.raise_for_status()
        records = r.json().get("records", [])
        stats["total_analyses"] = len(records)
        for rec in records:
            mode = rec["fields"].get("detected_mode", "UNKNOWN")
            stats["modes"][mode] = stats["modes"].get(mode, 0) + 1

        # Count feedback
        r2 = requests.get(
            _feedback_url(),
            headers=_headers(),
            params={"fields[]": ["rating", "correct_mode"], "pageSize": 100},
            timeout=10,
        )
        r2.raise_for_status()
        fb = r2.json().get("records", [])
        stats["total_feedback"] = len(fb)
        ups = sum(1 for f in fb if f["fields"].get("rating") == "up")
        if fb:
            stats["accuracy"] = round(ups / len(fb) * 100)
    except Exception:
        pass
    return stats
