# PKM Analyzer

**Detect how people defend against persuasion. Generate messages that bypass those defenses.**

[![Live App](https://img.shields.io/badge/Live_App-GitHub_Pages-blue?style=for-the-badge)](https://originaonxi.github.io/pkm-analyzer/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Built with Claude](https://img.shields.io/badge/Built_with-Claude_Haiku-orange?style=for-the-badge)](https://anthropic.com)

**[Try it live](https://originaonxi.github.io/pkm-analyzer/)** — no install, no backend, runs entirely in your browser.

---

## Why this exists

Every sales tool optimizes for volume. Send more emails. Automate more sequences. Personalize at scale.

None of them ask the only question that matters: **how does this specific person defend against being sold to?**

In 1994, Marian Friestad and Peter Wright published the [Persuasion Knowledge Model](https://doi.org/10.1086/209380) — a framework explaining how people develop defenses against persuasion attempts. Three decades of behavioral research followed. The sales industry ignored all of it.

PKM Analyzer operationalizes that research. It classifies any prospect into one of 10 empirically-derived defense modes, then generates outreach that doesn't trigger that defense.

## How it works

1. **Paste** any text about a prospect — LinkedIn bio, headline, job title, or a paragraph describing them
2. **Classify** — Claude Haiku analyzes the text and maps the person to one of 10 defense modes
3. **Bypass** — a second Claude call generates a cold message using the mode-specific bypass strategy

Two API calls. ~3 seconds. ~$0.001 per analysis.

Your Anthropic API key stays in your browser's localStorage. Never touches a server.

## The 10 defense modes

| # | Mode | Who | Defense trigger |
|---|------|-----|-----------------|
| 1 | **MOTIVE_INFERENCE** | VCs, ex-GTM execs (Gong, HubSpot, Salesforce) | Decodes your intent before reading your words |
| 2 | **TACTIC_RECOGNITION** | Repeat founders, serial operators | Pattern-matches your tactic in the first sentence |
| 3 | **OVERLOAD_AVOIDANCE** | SMB CEOs, operators wearing 5 hats | Anything that looks like effort gets archived |
| 4 | **SOCIAL_PROOF_SKEPTICISM** | CTOs, engineers, technical leads | Name-dropping triggers distrust |
| 5 | **AUTHORITY_DEFERENCE** | Directors, VPs, mid-level managers | Won't act without cover from above |
| 6 | **LOSS_AVERSION** | Risk-aware buyers, regulated industries | Fear of loss > desire for gain |
| 7 | **IDENTITY_THREAT** | Self-made founders, bootstrapped builders | Your pitch implies they need help |
| 8 | **TIMING_SKEPTICISM** | Perpetually "not ready" buyers | Timing is their permanent objection |
| 9 | **COMPLEXITY_FEAR** | Non-technical owners, first-time founders | Complexity = risk in their mind |
| 10 | **PRICE_ANCHORING** | Budget-constrained buyers, procurement | Anchor to the cheapest alternative |

Each mode has a specific **bypass strategy**, a set of **forbidden phrases** that trigger the defense, and a **message generation template** tuned to that mode.

## How AROS and ARIA use PKM

This isn't a standalone experiment. PKM is the persuasion layer inside two production systems at [Aonxi](https://github.com/originaonxi):

### AROS (Autonomous Revenue Operating System)
AROS runs customer outreach end-to-end. When AROS identifies a lead, PKM classifies their defense mode before any message is sent. Every cold email, follow-up, and re-engagement is generated through the mode-specific bypass strategy. This is why AROS hit **$199K collected**, **$8K peak day**, and **$2.9M ARR velocity** — it never triggers the defense that makes people delete.

### ARIA (Autonomous Revenue Intelligence Agent)
ARIA handles investor outreach. VCs are the hardest defense mode to bypass (MOTIVE_INFERENCE — they literally decode persuasion for a living). ARIA uses PKM to generate investor messages that lead with data, not pitch language. No "excited to share," no "love to connect." Just numbers.

### This tool
PKM Analyzer exposes the same engine publicly. Open-source the classification. Let anyone see how it works. The competitive advantage isn't the model — it's the system that acts on it.

## Architecture

```
Browser (index.html)
  │
  ├── localStorage: API key + feedback data
  │
  ├── Call 1: Claude Haiku → classify defense mode
  │     System prompt: PKM classification (10 modes)
  │     Returns: {mode, confidence, reasoning, awareness_score}
  │
  └── Call 2: Claude Haiku → generate bypass message
        System prompt: mode-specific bypass strategy
        Returns: plain text message (<80 words)
```

No backend. No database. No server costs. Single HTML file.

Shareable results via URL hash encoding — send anyone a link to see the analysis.

## Run locally

```bash
git clone https://github.com/originaonxi/pkm-analyzer.git
open pkm-analyzer/static/index.html
```

That's it. Enter your Anthropic API key when prompted.

### Optional: Run with the FastAPI backend

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn app:app --reload
```

The backend provides a REST API at `http://localhost:8000` if you want to integrate PKM into other systems.

**POST /analyze**
```json
{"text": "VP Engineering at Stripe, previously Staff at Google, built internal ML platform"}
```

**GET /modes**
Returns all 10 defense modes with descriptions and bypass strategies.

## The research

- Friestad, M., & Wright, P. (1994). *The Persuasion Knowledge Model: How people cope with persuasion attempts.* Journal of Consumer Research, 21(1), 1-31. [DOI](https://doi.org/10.1086/209380)
- Campbell, M. C., & Kirmani, A. (2000). *Consumers' use of persuasion knowledge.* Journal of Consumer Research, 27(1), 69-83.
- Ham, C. D., Nelson, M. R., & Das, S. (2015). *How to measure persuasion knowledge.* International Journal of Advertising, 34(1), 17-53.

PKM Analyzer maps these theoretical constructs to practical outreach categories. The 10 modes are derived from the interaction between **agent knowledge** (what the target knows about persuasion tactics), **topic knowledge** (domain expertise), and **persuasion knowledge** (awareness of being persuaded).

---

**Built by [Anmol Sam](https://github.com/originaonxi)** — Aonxi

$0.50/day to run the entire revenue stack. Code: [github.com/originaonxi/aros-agent](https://github.com/originaonxi/aros-agent)
