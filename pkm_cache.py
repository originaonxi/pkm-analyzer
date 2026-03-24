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
