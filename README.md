# PKM Analyzer

Paste a LinkedIn profile. Get the defense mode, bypass strategy, and a message that works.

Built on the Persuasion Knowledge Model (Friestad & Wright, 1994) — 30 years of psychology research that most sales tools have never heard of.

## What it detects

10 defense modes:

1. **MOTIVE_INFERENCE** — VCs, ex-GTM execs
2. **TACTIC_RECOGNITION** — repeat founders, serial operators
3. **OVERLOAD_AVOIDANCE** — busy SMB CEOs
4. **SOCIAL_PROOF_SKEPTICISM** — CTOs, engineers
5. **AUTHORITY_DEFERENCE** — mid-level managers
6. **LOSS_AVERSION** — risk-aware buyers
7. **IDENTITY_THREAT** — proud operators, bootstrapped founders
8. **TIMING_SKEPTICISM** — perpetually "not ready"
9. **COMPLEXITY_FEAR** — non-technical operators
10. **PRICE_ANCHORING** — budget-constrained buyers

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY
uvicorn app:app --reload
```

Open http://localhost:8000

## API

**POST /analyze**
```json
{"text": "LinkedIn bio or profile text"}
```
Returns: detected_mode, confidence, reasoning, awareness_score, bypass_strategy, forbidden_phrases, who_they_are, generated_message

**GET /modes**
Returns all 10 defense modes with descriptions.

## LinkedIn URL mode

LinkedIn URL fetching requires a working RapidAPI LinkedIn subscription. Set `RAPIDAPI_KEY` in `.env` and update the endpoint in `app.py` when you have a working API.

## Part of the Aonxi stack

AROS uses PKM for customer outreach.
ARIA uses PKM for investor outreach.
This tool exposes the engine publicly.

Built by Anmol Sam — [github.com/originaonxi](https://github.com/originaonxi)
