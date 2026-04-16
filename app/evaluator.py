from google import genai
from google.genai import types
from schemas import ExtractorOutput, VerifierOutput, EvaluationLLMOutput, EvaluationOutput
from utils import retry_on_demand_error

class EvaluatorAgent:
    def __init__(self, api_key: str):
        self.gemini_client = genai.Client(api_key=api_key)
        
    @retry_on_demand_error()
    def evaluate(self, extracted_data: ExtractorOutput, verification_data: VerifierOutput) -> EvaluationOutput:
        import os
        questions_path = os.path.join(os.path.dirname(__file__), "..", "due_diligence_questions.md")
        try:
            with open(questions_path, "r") as f:
                dd_questions = f.read()
        except FileNotFoundError:
            dd_questions = "Use standard startup evaluation criteria."
            
        eval_prompt = f"""
        You are an expert Angel Investor evaluating a startup. Your goal is to identify asymmetric upside, founder quality, and market pull.
        You must evaluate the startup rigorously based on the following Core Checklist and Diligence Framework:
        
        {dd_questions}
        
        Review the extracted pitch deck claims and the verification report below.
        
        Provide a concise executive summary of the opportunity focusing on potential upside and major risks.
        Calculate a foundational sub-score (0-100) for each of the 5 pillars based on their standalone strength. Do NOT artificially lower these scores due to red flags; the mathematical system handles red flag deductions automatically.
        Also provide a specific reason/explanation justifying each score.
        
        Claims: {extracted_data.model_dump_json()}
        Verification: {verification_data.model_dump_json()}
        """
        
        response = self.gemini_client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=eval_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EvaluationLLMOutput,
            ),
        )
        
        llm_output = EvaluationLLMOutput.model_validate_json(response.text)
        
        stage = getattr(extracted_data, 'startup_stage', 'Seed').lower()
        if "pre-seed" in stage or "seed" in stage:
            team_w, market_w, product_w, traction_w, fin_w = 0.45, 0.35, 0.20, 0.0, 0.0
        elif "series a" in stage:
            team_w, market_w, product_w, traction_w, fin_w = 0.30, 0.20, 0.20, 0.20, 0.10
        else:
            team_w, market_w, product_w, traction_w, fin_w = 0.20, 0.20, 0.15, 0.25, 0.20
            
        upside_conviction_score = int(
            llm_output.team_score * team_w +
            llm_output.market_score * market_w +
            llm_output.product_score * product_w +
            llm_output.traction_score * traction_w +
            llm_output.financials_score * fin_w
        )
        
        execution_risk_score = 0
        for flag in verification_data.red_flags:
            severity = flag.severity.lower()
            if "high" in severity:
                execution_risk_score += 20
            elif "medium" in severity:
                execution_risk_score += 10
        execution_risk_score = min(100, execution_risk_score)
        
        if upside_conviction_score > 80 and execution_risk_score <= 20:
            investment_decision = "Dive In"
        elif upside_conviction_score > 60 and execution_risk_score <= 40:
            investment_decision = "Jump"
        else:
            investment_decision = "Belly Flop"
            
        return EvaluationOutput(
            team_score=llm_output.team_score,
            team_reason=llm_output.team_reason,
            market_score=llm_output.market_score,
            market_reason=llm_output.market_reason,
            product_score=llm_output.product_score,
            product_reason=llm_output.product_reason,
            traction_score=llm_output.traction_score,
            traction_reason=llm_output.traction_reason,
            financials_score=llm_output.financials_score,
            financials_reason=llm_output.financials_reason,
            upside_conviction_score=upside_conviction_score,
            execution_risk_score=execution_risk_score,
            investment_decision=investment_decision,
            executive_summary=llm_output.executive_summary
        )
