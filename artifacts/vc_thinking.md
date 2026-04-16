# AI Due Diligence Agent: Refactor Complete

We have successfully rebuilt the AI evaluation pipeline to think more like an elite early-stage VC rather than a punitive underwriter. 

## What Was Changed

### 1. Stage-Aware Extractor (`app/schemas.py`, `app/extractor.py`)
- We updated `ExtractorOutput` to capture a `startup_stage` field.
- The `ExtractorAgent` will now explicitly deduce the startup's stage ("Pre-Seed", "Seed", "Series A", or "Growth/Late Stage") based on the pitch deck's traction and financial claims.

### 2. Guardrails Against "Unverifiable" Private Metrics (`app/verifier.py`)
- We've added a strict `PRIVATE METRICS & FUTURE PLANS` rule. 
- The verification agent will **no longer generate red flags** simply because future projections or historic private company ARR aren't indexed on Google or Crunchbase.

### 3. The Conviction vs. Risk Matrix Engine (`app/evaluator.py`)
We've replaced the single punitive `confidence_score` with a dynamic Dual-Scoring system:
- **`upside_conviction_score`**: Calculated using stage-aware weights (e.g., Pre-Seed metrics completely drop "Traction" and "Financials", heavily weighting "Team" and "Market" instead).
- **`execution_risk_score`**: Computed from verifyable material red flags.

### 4. The Final Decision Thresholds
We swapped out standard confidence numbers for your requested fun qualitative rating:
- **🟢 Dive In**: High conviction (>80), Low risk (<=20)
- **🟡 Jump**: Solid baseline (>60 conviction, <=40 risk)
- **🔴 Belly Flop**: Low upside and/or insurmountable execution risk.

This final output is returned cleanly via `investment_decision` in the JSON payload, along with your updated `upside_conviction_score` and `execution_risk_score`.
