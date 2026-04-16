# System Architecture & Prompt Evaluation Plan

Following a critical evaluation of how the system processes data—particularly analyzing why the legendary AirBnb pitch deck scored a 57 with high penalties—I have uncovered several structural flaws within the LLM prompts and scoring logic that are actively misguiding the analysis.

## Critical Flaws Identified in Prompts & Logic

1. **The "Banker vs. Angel Investor" Bias (`evaluator.py`)**
   Your `evaluator.py` prompt directs the AI to *"penalize if unverified or red flags found"*. Right beneath this, our Python script manually loops through red flags and subtracts points (`base_score - penalties`). This results in **double-penalization**. The AI lowers the 0-100 pillar scores, and then the script slaps a massive secondary flat point deduction on top. Furthermore, an Angel Investor focuses on asymmetric upside, whereas this prompt acts like a loan officer demanding verified traction from pre-seed founders.

2. **Chronological Hallucination (`verifier.py`)**
   The fact-checker prompt has zero concept of time. The AI pulls 2026 data from the internet to evaluate a deck from 2008. If the deck says the market is "2 million users," and the web search says "100 million users," the AI triggers a "Discrepancy Red Flag." 

3. **Binary Fact-Checking on Projections (`verifier.py`)**
   The prompt commands: *"Focus strictly on facts."* This is misguided for early-stage startups where pitch decks are comprised of forward-looking projections and "secret sauce" claims. Forcing the AI into a binary True/False fact-check causes it to wrongly flag visionary claims as "unverifiable errors."

4. **Rigid Extraction & Hallucinated Metrics (`extractor.py`)**
   The extraction prompt forces data into a strict JSON schema (e.g., `current_revenue`). Since early-stage startups often omit traction or financials, the AI might hallucinate or extract irrelevant user counts into the revenue bucket. We need to explicitly tell the AI: *"If a metric is missing, state 'Not Provided' instead of guessing."*

### 1. Contextualize Time & Enhance Search Vectors in the Verifier
We will update the prompt in `app/verifier.py` with two major additions:
- **Historical Context:** Instruct the AI to look for the historical context of the pitch deck to prevent penalizing 2008 data against 2026 outcomes.
- **Trend & Sentiment Analysis:** Explicitly instruct the LLM to generate searches targeting **Google Trends**, **Reddit**, **social media**, and **customer reviews**.
- **Startup Ecosystem Validation:** Explicitly mandate that searches query definitive startup databases and VC portfolios (e.g., **Crunchbase, Wellfound/AngelList, Built In, Y Combinator, a16z, Khosla Ventures**) to accurately triangulate the startup's funding status, existing competitors, and market map.

---

## Proposed Changes

To fix these issues, we will make targeted enhancements across the three primary agents:

### 1. `app/extractor.py` (The Extractor Agent)
- Add a prompt rule: `"If specific metrics (like revenue) are missing, strictly output 'Not Provided'. Do not infer or invent numbers."`

### 2. `app/verifier.py` (The Verifier Agent)
- **Time/Context Awareness**: Add a clause instructing the AI that it may be reviewing historical or forward-looking documents.
- **Plausibility vs. Binary Fact**: Shift the verification goal from "strict facts" to "Assess the plausibleness of market claims."
- **Generate Smarter Queries**: Remove the outdated hint to search for *"founder backgrounds on LinkedIn"* (as LinkedIn blocks scrapers like Tavily), and replace it with relying on news and broader web indices. 

### 3. `app/evaluator.py` (The Evaluator Agent)
- **Eliminate Double-Dipping**: Remove the instruction telling the LLM to penalize for red flags, leaving the penalty exclusively to the mathematical Python formula.
- **Severity-Weighted Penalties**: We will rewrite the mathematical penalty. Instead of every red flag being a flat `-15` points:
  - **High Severity** (e.g. Fraud, fake founder background): **-15 points**
  - **Medium Severity** (e.g. Foundational miscalculation, strong direct overlooked competitor): **-5 points**
  - **Low Severity** (e.g. Minor outdated stat): **-0 points** (Noted but not penalized)
- **Upside Focus**: Shift the Prompt Persona to evaluate *asymmetric upside and founder quality*, acting like a true Angel.

---

## User Review Required

> [!WARNING]
> Please review this systemic overhaul of the LLM prompts and the new Severity-Weighted Scoring mechanism. Does this align properly with your vision for evaluating early-stage venture capital pitch decks?

Let me know if you approve or if you'd like to adjust any of prompt tweaks or penalty weights!
