import os
import tempfile
from google import genai
from google.genai import types
from schemas import ExtractorOutput
from utils import retry_on_demand_error

class ExtractorAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        
    @retry_on_demand_error()
    def extract(self, pdf_bytes: bytes) -> ExtractorOutput:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
            
        try:
            uploaded_file = self.client.files.upload(file=temp_pdf_path)
            
            # Read the due diligence questions to guide the extraction
            questions_path = os.path.join(os.path.dirname(__file__), "..", "due_diligence_questions.md")
            try:
                with open(questions_path, "r") as f:
                    dd_questions = f.read()
            except FileNotFoundError:
                dd_questions = "Focus on Team, Market, Product, Traction, and Financials."
                
            prompt = f"""
            Analyze this pitch deck and extract the requested information into the structured JSON format provided.
            Use the following Due Diligence Questions framework to explicitly guide your data extraction:
            
            {dd_questions}
            
            CRITICAL EXTRACTION RULE: If a specific quantitative metric (e.g., current revenue, user count) or data point is missing from the pitch deck, you must strictly output 'Not Provided'. Do NOT infer, calculate, or hallucinate missing financial or traction metrics.
            STAGE DEDUCTION: You must estimate the "startup_stage" based on traction, data, and raised amount. Use one of: "Pre-Seed", "Seed", "Series A", "Growth/Late Stage".
            """
            
            response = self.client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractorOutput,
                ),
            )
            return ExtractorOutput.model_validate_json(response.text)
        finally:
            os.remove(temp_pdf_path)
