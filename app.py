from __future__ import annotations

import json
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pkm_cache import get_cached, make_cache_key, store_result
from pkm_engine import DEFENSE_MODES, analyze

load_dotenv()

app = FastAPI(title="PKM Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from typing import Optional


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


def fetch_netrows(linkedin_url: str) -> str:
    key = os.getenv("NETROWS_API_KEY")
    if not key:
        raise HTTPException(500, "Netrows API key not configured")
    r = requests.get(
        "https://api.netrows.com/v1/linkedin/profile",
        headers={"Authorization": f"Bearer {key}"},
        params={"url": linkedin_url},
        timeout=15,
    )
    if not r.ok:
        raise HTTPException(502, f"Netrows error: {r.status_code}")
    d = r.json()
    parts = []
    name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
    if name:
        parts.append(f"Name: {name}")
    if d.get("headline"):
        parts.append(f"Headline: {d['headline']}")
    if d.get("summary"):
        parts.append(f"Bio: {d['summary']}")
    title = d.get("current_title", "")
    company = d.get("current_company", "")
    if title or company:
        role = f"{title} at {company}".strip(" at")
        parts.append(f"Current role: {role}")
    if d.get("location"):
        parts.append(f"Location: {d['location']}")
    if not parts:
        raise HTTPException(502, "Could not parse LinkedIn profile")
    return "\n".join(parts)


@app.post("/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    if not req.text and not req.url:
        raise HTTPException(400, "Provide 'text' or 'url'.")

    linkedin_url = ""
    source = "text_paste"

    if req.url:
        profile_text = fetch_netrows(req.url)
        linkedin_url = req.url
        source = "netrows"
    else:
        profile_text = req.text

    if not profile_text or len(profile_text.strip()) < 10:
        raise HTTPException(400, "Profile text too short.")

    # Check cache
    cache_key = make_cache_key(req.url if req.url else profile_text)
    cached = get_cached(cache_key)
    if cached:
        fp = cached.get("forbidden_phrases", "[]")
        try:
            fp = json.loads(fp)
        except (json.JSONDecodeError, TypeError):
            fp = []
        mode_key = cached.get("detected_mode", "")
        mode_data = DEFENSE_MODES.get(mode_key, {})
        return {
            "detected_mode": mode_key,
            "label": mode_data.get("label", mode_key.replace("_", " ").title()),
            "confidence": cached.get("confidence", 0),
            "reasoning": cached.get("reasoning", ""),
            "awareness_score": cached.get("awareness_score", 0),
            "bypass_strategy": cached.get("bypass_strategy", ""),
            "forbidden_phrases": fp,
            "who_they_are": mode_data.get("who", ""),
            "description": mode_data.get("description", ""),
            "generated_message": cached.get("generated_message", ""),
            "from_cache": True,
        }

    # Fresh analysis
    result = analyze(profile_text)

    # Store in Airtable
    try:
        store_result(cache_key, result, linkedin_url, profile_text, source)
    except Exception:
        pass

    return {**result, "from_cache": False}


@app.get("/modes")
async def get_modes():
    return {
        key: {
            "label": v["label"],
            "who": v["who"],
            "description": v["description"],
            "bypass_strategy": v["bypass_strategy"],
            "forbidden_phrases": v["forbidden_phrases"],
        }
        for key, v in DEFENSE_MODES.items()
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def root():
        return FileResponse("static/index.html")
