import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

DEFENSE_MODES = {
    "MOTIVE_INFERENCE": {
        "label": "Motive Inference",
        "who": "VCs, ex-GTM execs (Gong, HubSpot, Salesforce alumni)",
        "description": "They decode your intent before reading your words. Every message is reverse-engineered for motive.",
        "bypass_strategy": "Lead with transparent motive. State exactly why you're reaching out and what you want. No disguised pitches.",
        "forbidden_phrases": ["I'd love to pick your brain", "Quick question", "Thought you might be interested", "No agenda, just wanted to connect"],
    },
    "TACTIC_RECOGNITION": {
        "label": "Tactic Recognition",
        "who": "Repeat founders, 2x+ raised, serial operators",
        "description": "They've seen every playbook. Pattern-match your tactic in the first sentence and delete.",
        "bypass_strategy": "Break the pattern. Use an unexpected format, an unusual hook, or raw honesty that doesn't fit any template.",
        "forbidden_phrases": ["I noticed you recently", "Congrats on the raise", "Fellow founder here", "I know you're busy"],
    },
    "OVERLOAD_AVOIDANCE": {
        "label": "Overload Avoidance",
        "who": "Busy SMB CEOs, operators wearing 5 hats",
        "description": "Not skeptical — just drowning. Anything that looks like effort gets archived.",
        "bypass_strategy": "Make it effortless. One sentence, one ask, zero friction. The message should take 5 seconds to process.",
        "forbidden_phrases": ["Would love to schedule a call", "Let me know when you're free", "I have a few ideas I'd like to share", "Can I send you a deck?"],
    },
    "SOCIAL_PROOF_SKEPTICISM": {
        "label": "Social Proof Skepticism",
        "who": "CTOs, senior engineers, technical decision-makers",
        "description": "Name-dropping triggers distrust. They want evidence, not endorsements.",
        "bypass_strategy": "Lead with technical specifics. Show what you built, how it works, what the numbers are. No logos, no testimonials.",
        "forbidden_phrases": ["Trusted by companies like", "Our customers include", "As seen in", "Award-winning"],
    },
    "AUTHORITY_DEFERENCE": {
        "label": "Authority Deference",
        "who": "Mid-level managers, directors, team leads",
        "description": "They defer decisions upward. Even if interested, they won't act without cover.",
        "bypass_strategy": "Give them ammunition for their boss. Frame your message as something they can forward up with a one-line summary.",
        "forbidden_phrases": ["Are you the decision-maker?", "Who handles this at your company?", "Can you loop in your manager?", "I'd love to get on your calendar"],
    },
    "LOSS_AVERSION": {
        "label": "Loss Aversion",
        "who": "Risk-aware buyers, regulated industries, cautious operators",
        "description": "Fear of loss > desire for gain. They won't move unless staying still feels more dangerous.",
        "bypass_strategy": "Frame the cost of inaction. Show what they're losing today, not what they'd gain tomorrow.",
        "forbidden_phrases": ["Unlock new revenue", "10x your growth", "Imagine if you could", "The upside is massive"],
    },
    "IDENTITY_THREAT": {
        "label": "Identity Threat",
        "who": "Self-made operators, proud builders, bootstrapped founders",
        "description": "Your pitch implies they need help. That threatens their identity as someone who figures things out.",
        "bypass_strategy": "Acknowledge their competence first. Position your offer as a tool for someone already winning, not a rescue.",
        "forbidden_phrases": ["You're probably struggling with", "Most companies like yours fail at", "You need", "Let me help you fix"],
    },
    "TIMING_SKEPTICISM": {
        "label": "Timing Skepticism",
        "who": "Perpetually 'not ready' buyers, long evaluation cycles",
        "description": "They agree it's interesting but never now. Timing is their permanent objection.",
        "bypass_strategy": "Remove the timing decision entirely. Make it about a 2-minute action today, not a commitment for next quarter.",
        "forbidden_phrases": ["When would be a good time?", "Planning for next quarter?", "Let's revisit in Q3", "No rush"],
    },
    "COMPLEXITY_FEAR": {
        "label": "Complexity Fear",
        "who": "Non-technical operators, first-time founders, small business owners",
        "description": "They assume your product is harder than it is. Complexity = risk in their mind.",
        "bypass_strategy": "Show the simplest possible version. One screenshot, one sentence about what it does. No architecture diagrams.",
        "forbidden_phrases": ["Our platform integrates with", "Powered by AI/ML", "Enterprise-grade solution", "Full-stack"],
    },
    "PRICE_ANCHORING": {
        "label": "Price Anchoring",
        "who": "Budget-constrained buyers, cost-conscious operators, procurement-heavy orgs",
        "description": "They anchor to the cheapest alternative and judge everything relative to that.",
        "bypass_strategy": "Reframe the comparison. Don't compete on price — change what they're comparing you to. Cost per outcome, not cost per seat.",
        "forbidden_phrases": ["Affordable pricing", "Cheaper than", "Starting at just", "Free trial"],
    },
}

CLASSIFICATION_SYSTEM = """You are a PKM (Persuasion Knowledge Model) analyst. Given a LinkedIn profile or bio, classify the person into exactly one of these 10 defense modes:

MOTIVE_INFERENCE — VCs, ex-GTM execs (Gong, HubSpot, Salesforce alumni)
TACTIC_RECOGNITION — repeat founders, 2x+ raised, serial operators
OVERLOAD_AVOIDANCE — busy SMB CEOs, operators wearing 5 hats
SOCIAL_PROOF_SKEPTICISM — CTOs, senior engineers, technical decision-makers
AUTHORITY_DEFERENCE — mid-level managers, directors, team leads
LOSS_AVERSION — risk-aware buyers, regulated industries, cautious operators
IDENTITY_THREAT — self-made operators, proud builders, bootstrapped founders
TIMING_SKEPTICISM — perpetually "not ready" buyers, long evaluation cycles
COMPLEXITY_FEAR — non-technical operators, first-time founders
PRICE_ANCHORING — budget-constrained buyers, cost-conscious operators

Return JSON only:
{
  "mode": "MODE_NAME",
  "confidence": 0-100,
  "reasoning": "one sentence why",
  "awareness_score": 0-10
}"""

MESSAGE_SYSTEM = """You write cold outreach messages using PKM bypass strategies.

Given a defense mode and bypass strategy, write a message that does NOT trigger that defense. Under 80 words. No sign-off needed.

AONXI FACTS (use if relevant):
$199K collected. $8K peak day.
$2.9M ARR velocity. $0.50/day to run.
Code: github.com/originaonxi/aros-agent

Return the message only. No JSON. No quotes."""


def analyze(profile_text: str) -> dict:
    client = anthropic.Anthropic()

    # Step 1: Classify
    classification_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=CLASSIFICATION_SYSTEM,
        messages=[{"role": "user", "content": f"Profile:\n{profile_text}"}],
    )

    raw = classification_response.content[0].text.strip()
    # Extract JSON from response
    if "```" in raw:
        raw = raw.split("```")[1].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

    classification = json.loads(raw)
    mode_key = classification["mode"]
    mode_data = DEFENSE_MODES.get(mode_key, DEFENSE_MODES["MOTIVE_INFERENCE"])

    # Step 2: Generate bypass message
    message_prompt = f"""Defense mode: {mode_key} — {mode_data['description']}
Bypass strategy: {mode_data['bypass_strategy']}
Forbidden phrases: {', '.join(mode_data['forbidden_phrases'])}

Profile:
{profile_text}

Write the bypass message."""

    message_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=MESSAGE_SYSTEM,
        messages=[{"role": "user", "content": message_prompt}],
    )

    generated_message = message_response.content[0].text.strip()

    return {
        "detected_mode": mode_key,
        "label": mode_data["label"],
        "confidence": classification.get("confidence", 0),
        "reasoning": classification.get("reasoning", ""),
        "awareness_score": classification.get("awareness_score", 5),
        "bypass_strategy": mode_data["bypass_strategy"],
        "forbidden_phrases": mode_data["forbidden_phrases"],
        "who_they_are": mode_data["who"],
        "description": mode_data["description"],
        "generated_message": generated_message,
    }
