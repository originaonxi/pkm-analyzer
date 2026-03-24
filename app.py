import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pkm_engine import analyze, DEFENSE_MODES

load_dotenv()

app = FastAPI(title="PKM Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str | None = None
    url: str | None = None


def fetch_linkedin_profile(linkedin_url: str) -> str:
    """Fetch LinkedIn profile via RapidAPI. Placeholder — swap in a working API."""
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="RAPIDAPI_KEY not configured. Use text input instead.")

    # TODO: Replace with a working LinkedIn profile API endpoint
    # The endpoint below is a placeholder — update the URL and host when you subscribe to a working API
    response = requests.get(
        "https://linkedin-data-api.p.rapidapi.com/get-profile-data-by-url",
        params={"url": linkedin_url},
        headers={
            "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com",
            "x-rapidapi-key": api_key,
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="LinkedIn API request failed.")

    data = response.json()
    if not data.get("success", True) or not data.get("data", data):
        raise HTTPException(
            status_code=502,
            detail="LinkedIn API is unavailable. Paste profile text instead.",
        )

    # Adapt field extraction to whichever API you use
    d = data.get("data", data)
    parts = []
    if d.get("firstName"):
        parts.append(f"Name: {d.get('firstName', '')} {d.get('lastName', '')}")
    if d.get("headline"):
        parts.append(f"Headline: {d['headline']}")
    if d.get("summary"):
        parts.append(f"Bio: {d['summary']}")
    if d.get("location"):
        loc = d["location"]
        if isinstance(loc, dict):
            loc = loc.get("default", str(loc))
        parts.append(f"Location: {loc}")

    experiences = d.get("experiences", d.get("position", []))
    if experiences and isinstance(experiences, list):
        current = experiences[0] if experiences else {}
        title = current.get("title", "")
        company = current.get("companyName", current.get("company", ""))
        if title or company:
            parts.append(f"Current role: {title} at {company}")
        past = [
            e.get("companyName", e.get("company", ""))
            for e in experiences[1:5]
            if e.get("companyName") or e.get("company")
        ]
        if past:
            parts.append(f"Past companies: {', '.join(past)}")

    if not parts:
        raise HTTPException(status_code=502, detail="Could not parse LinkedIn profile. Paste text instead.")

    return "\n".join(parts)


@app.post("/analyze")
async def analyze_profile(req: AnalyzeRequest):
    if not req.text and not req.url:
        raise HTTPException(status_code=400, detail="Provide 'text' or 'url'.")

    if req.url:
        profile_text = fetch_linkedin_profile(req.url)
    else:
        profile_text = req.text

    if not profile_text or len(profile_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Profile text too short.")

    result = analyze(profile_text)
    return result


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


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
