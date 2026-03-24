# PKM Analyzer

**A self-improving persuasion intelligence system. Every analysis makes the next one smarter. Every correction trains the model. The more people use it, the more accurate it gets.**

[![Live App](https://img.shields.io/badge/Try_it_live-PKM_Analyzer-blue?style=for-the-badge)](https://originaonxi.github.io/pkm-analyzer/)
[![Self-Improving](https://img.shields.io/badge/Self--Improving-Every_Analysis-purple?style=for-the-badge)]()
[![API](https://img.shields.io/badge/API-Render-46E3B7?style=for-the-badge)](https://pkm-analyzer.onrender.com/modes)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[Try it free](https://originaonxi.github.io/pkm-analyzer/)** — no API key, no install. Your feedback directly trains the next classification.

---

## Why PKM matters for AGI agents

Every AI agent that talks to humans has the same problem: **people have defenses.**

A VC who spent 10 years at Gong reads your email differently than a home care owner in Ohio. The VC detects your selling intent before finishing the first sentence. The home care owner doesn't distrust you — they're just drowning in 60 vendor pitches a week and anything over 3 sentences gets archived.

Same product. Same traction. Completely different resistance patterns. If your agent sends the same message to both, it fails on both.

In 1994, psychologists Marian Friestad and Peter Wright published the **[Persuasion Knowledge Model](https://doi.org/10.1086/209380)** — a framework explaining how people develop, activate, and deploy defenses against persuasion attempts. Three decades of behavioral research followed. The entire sales industry ignored it. They optimized for volume instead of understanding.

**PKM Analyzer operationalizes that research for machines.** It gives any AI agent the ability to read a person's digital profile — their role, their background, their company, their experience — and understand *how that person will resist* before generating a single word.

This is not personalization. Personalization is "Hey {first_name}, I saw you work at {company}." That's string interpolation.

This is **defense-mode classification** — understanding that a bootstrapped founder who built everything themselves will hear "let us automate that" as "you're not good enough," and writing around it.

## The self-improvement loop

This is not a static classifier. Every interaction makes it better:

```
User analyzes a profile
         │
         v
Claude classifies → defense mode + bypass message
         │
         v
User rates: thumbs up (correct) or thumbs down (wrong)
         │
    ┌────┴─────┐
    │          │
  correct    wrong → user selects actual mode
    │          │
    v          v
Both stored in Airtable PKM_Feedback table
         │
         v
Next classification pulls recent corrections
and injects them into the Claude prompt:
"Profile like X was detected as Y but was actually Z"
         │
         v
Claude adjusts — same mistake never repeated
         │
         v
The more people use it, the smarter it gets
```

**This is RLHF running live in production.** Not on a training cluster. In the product. Every day.

## How it works

```
Profile text or LinkedIn URL
         |
         v
   ┌─────────────────────────────────┐
   │  Airtable PKM_Cache             │
   │  (check if analyzed before)      │
   ├──────┬──────────────────────────┤
   │ HIT  │         MISS             │
   │      │          |               │
   │      │    Pull corrections       │
   │      │    from PKM_Feedback      │
   │      │          |               │
   │      │    Claude Haiku           │
   │      │    Classify → 1 of 10    │
   │      │    (with learned fixes)   │
   │      │          |               │
   │      │    Claude Haiku           │
   │      │    Generate bypass msg    │
   │      │          |               │
   │      │    Store in Airtable      │
   └──┬───┴──────────┬───────────────┘
      │              │
      v              v
   Return result (cached or fresh)
```

**Cache hit:** instant, $0, no API calls.
**Cache miss:** ~3 seconds, ~$0.001, stored forever.

Every profile analyzed once is cached permanently. The system gets cheaper over time.

## The 10 defense modes

| # | Mode | Who | How they defend | Bypass strategy |
|---|------|-----|-----------------|-----------------|
| 1 | **MOTIVE_INFERENCE** | VCs, ex-GTM execs (Gong, HubSpot, Salesforce) | Decode your intent before reading your words | **PURE_DATA** — lead with a number, never open with "I" |
| 2 | **TACTIC_RECOGNITION** | Repeat founders, serial operators | Pattern-match your tactic in sentence one | **SIGNAL_HOOK** — reference specific public activity, prove research is real |
| 3 | **OVERLOAD_AVOIDANCE** | SMB CEOs, operators wearing 5 hats | Archive anything that looks like effort | **ULTRA_SHORT** — under 60 words, one specific calendar slot |
| 4 | **SOCIAL_PROOF_SKEPTICISM** | CTOs, engineers, technical leads | Name-dropping triggers distrust | **CREDIBILITY_FIRST** — exact numbers, public verifiable proof |
| 5 | **AUTHORITY_DEFERENCE** | Directors, VPs, mid-level managers | Won't act without cover from above | **PEER_PROOF** — name peers who use it, give ammo to forward up |
| 6 | **LOSS_AVERSION** | Risk-aware buyers, regulated industries | Fear of loss > desire for gain | **COST_OF_INACTION** — frame what they lose by NOT acting |
| 7 | **IDENTITY_THREAT** | Self-made founders, bootstrapped builders | Your pitch implies they need help | **AMPLIFICATION** — they run the system, they're still the decision maker |
| 8 | **TIMING_SKEPTICISM** | Perpetually "not ready" buyers | Timing is their permanent objection | **TRIGGER_EVENT** — name a specific reason NOW is different |
| 9 | **COMPLEXITY_FEAR** | Non-technical owners, first-time founders | Complexity = risk in their mind | **SIMPLICITY_PROOF** — show the one action needed, nothing else |
| 10 | **PRICE_ANCHORING** | Budget-constrained buyers, procurement | Anchor to the cheapest alternative | **ROI_INVERSION** — cost per outcome, not cost per month |

Each mode includes **forbidden phrases** — words and patterns that activate the defense. The agent never uses them.

## Why this matters for AROS and ARIA

PKM Analyzer is not a standalone tool. It is the **perception layer** of the Aonxi autonomous agent stack — the system that reads humans before any agent talks to them.

### The Aonxi agent architecture

```
                    ┌─────────────────────────────────┐
                    │         PKM Analyzer             │
                    │   (defense mode classification)  │
                    │   10 modes × bypass strategies   │
                    │   Airtable cache (permanent)     │
                    └────────┬──────────┬──────────────┘
                             │          │
                    ┌────────┴──┐  ┌────┴────────────┐
                    │   AROS    │  │      ARIA        │
                    │  Revenue  │  │   Fundraising    │
                    │   Agent   │  │     Agent        │
                    └───────────┘  └──────────────────┘
                             │          │
                    ┌────────┴──────────┴──────────────┐
                    │          Airtable                 │
                    │   (single source of truth)        │
                    │   Every contact, every message,   │
                    │   every outcome, every score      │
                    └──────────────────────────────────┘
```

### [AROS](https://github.com/originaonxi/aros-agent) — Autonomous Revenue Operating System

AROS finds customers, scores them, researches their real-time signals (hiring, struggling, expanding), and sends cold emails. Before PKM, it used the same tone for everyone. Now:

- A **CTO** gets SOCIAL_PROOF_SKEPTICISM bypass — exact numbers, verifiable claims, no "trusted by" language
- A **busy SMB owner** gets OVERLOAD_AVOIDANCE bypass — under 60 words, one calendar slot, zero fluff
- A **bootstrapped founder** gets IDENTITY_THREAT bypass — "your judgment runs this" framing, never "let us fix"

**Result:** $199K collected. $8K peak day. $2.9M ARR velocity. $0.50/day to run.

### [ARIA](https://github.com/originaonxi/ARIA) — Autonomous Relationship Intelligence Agent

ARIA raises money. It finds investors, verifies emails, scores by thesis fit, researches public activity, writes cold emails, sends via Instantly, classifies replies, and prepares for meetings. VCs are the hardest defense mode:

- **MOTIVE_INFERENCE** — they decode persuasion for a living
- ARIA bypasses with PURE_DATA — opens with a number, never with "I'm excited to"
- Every message is under 100 words with zero banned phrases

**Status:** 19 investor emails sent. $250K pre-seed raise. General Catalyst, Bessemer, Antler, Blume, Kae Capital.

### The vision: two super-agents, everything else feeds in

AROS and ARIA are the two permanent agents. Every new capability — PKM analysis, LinkedIn scraping, email verification, signal detection, reply classification — plugs into one of them. They are the brains. Airtable is the memory. Every contact ever analyzed, every message ever sent, every response ever received — stored permanently, deduplicated, scored.

New agents don't create new databases. They write to the same Airtable. New capabilities don't create new workflows. They become modules inside AROS (revenue) or ARIA (fundraising).

PKM Analyzer is the first module built as a standalone tool that feeds both.

## Production stack

| Layer | Service | Cost |
|-------|---------|------|
| **Frontend** | [GitHub Pages](https://originaonxi.github.io/pkm-analyzer/) | Free |
| **API** | [Render](https://pkm-analyzer.onrender.com) (FastAPI) | Free tier |
| **Classification** | Claude Haiku (Anthropic) | ~$0.001/analysis |
| **LinkedIn fetch** | Netrows API | Per-call |
| **Cache/storage** | Airtable (PKM_Cache table) | Free tier |

Users pay nothing. The backend handles all API calls. Results are cached permanently — the same profile never costs twice.

## API

**POST /analyze**
```json
{"text": "Sarah Chen, Partner at Bessemer, previously VP Sales at Gong"}
```
or
```json
{"url": "https://linkedin.com/in/username"}
```

**Response:**
```json
{
  "detected_mode": "MOTIVE_INFERENCE",
  "label": "Motive Inference",
  "confidence": 92,
  "reasoning": "Ex-GTM exec from Gong now in VC — decodes persuasion tactics instinctively",
  "awareness_score": 9,
  "bypass_strategy": "Lead with transparent motive. No disguised pitches.",
  "forbidden_phrases": ["I'd love to pick your brain", "Quick question", "No agenda"],
  "who_they_are": "VCs, ex-GTM execs",
  "generated_message": "...",
  "from_cache": true
}
```

**GET /modes** — returns all 10 defense modes with descriptions and bypass strategies.

**GET /health** — service health check.

## Run locally

```bash
git clone https://github.com/originaonxi/pkm-analyzer.git
cd pkm-analyzer
pip install -r requirements.txt
cp .env.example .env
# Add your keys to .env
uvicorn app:app --reload
```

## The research

- Friestad, M., & Wright, P. (1994). *The Persuasion Knowledge Model: How people cope with persuasion attempts.* Journal of Consumer Research, 21(1), 1-31. [DOI](https://doi.org/10.1086/209380)
- Campbell, M. C., & Kirmani, A. (2000). *Consumers' use of persuasion knowledge.* Journal of Consumer Research, 27(1), 69-83.
- Ham, C. D., Nelson, M. R., & Das, S. (2015). *How to measure persuasion knowledge.* International Journal of Advertising, 34(1), 17-53.
- Kirmani, A., & Zhu, R. (2007). *Vigilant against manipulation: The effect of regulatory focus on the use of persuasion knowledge.* Journal of Marketing Research, 44(4), 688-701.

The 10 defense modes are derived from the interaction between three knowledge structures in Friestad & Wright's model: **agent knowledge** (what the target knows about persuasion tactics), **topic knowledge** (domain expertise), and **persuasion knowledge** (awareness of being persuaded). PKM Analyzer maps these theoretical constructs to observable signals in digital profiles — job titles, company backgrounds, career trajectories — and classifies the dominant defense pattern.

---

**Built by [Anmol Sam](https://github.com/originaonxi)** — CTO, Aonxi

AROS: [github.com/originaonxi/aros-agent](https://github.com/originaonxi/aros-agent)
ARIA: [github.com/originaonxi/ARIA](https://github.com/originaonxi/ARIA)

$0.50/day to run the entire autonomous revenue stack.
