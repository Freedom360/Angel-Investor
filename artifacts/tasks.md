# Execution Tasks: AI Due Diligence Evaluation Refactor

- `[x]` 1. Update Schemas (`app/schemas.py`)
  - `[x]` Add `startup_stage` to `ExtractorOutput`.
  - `[x]` Remove `penalty_total` and `confidence_score` from `EvaluationOutput`.
  - `[x]` Add `upside_conviction_score`, `execution_risk_score`, and `investment_decision` to `EvaluationOutput`.
- `[x]` 2. Update Extractor (`app/extractor.py`)
  - `[x]` Modify the prompt to instruct the LLM to deduce the `startup_stage`.
- `[x]` 3. Update Verifier (`app/verifier.py`)
  - `[x]` Add the "Private Metrics & Future Plans" rule to the verification prompt to prevent false-positive red flags.
- `[x]` 4. Update Evaluator (`app/evaluator.py`)
  - `[x]` Implement dynamic stage-aware weighting logic based on the extracted `startup_stage`.
  - `[x]` Compute `upside_conviction_score` (stage-aware weighted average).
  - `[x]` Compute `execution_risk_score` (sum of severity penalties).
  - `[x]` Implement logic to determine the `investment_decision` ("Dive In", "Jump", "Belly Flop").
- `[x]` 5. Verification & Testing
  - `[x]` Run a test evaluation to ensure outputs schema correctly populate and output the new fields.
