from typing import List, Optional
from pydantic import BaseModel, Field

class TeamInfo(BaseModel):
    founder_backgrounds: str = Field(description="Backgrounds of the founders including prior startups.")
    team_excellence: str = Field(description="Assessment of team excellence and gaps.")

class MarketInfo(BaseModel):
    market_size: str = Field(description="Size of the target market and opportunity.")
    why_now: str = Field(description="Why this is a great opportunity right now.")

class ProductInfo(BaseModel):
    description: str = Field(description="Description of the product or service.")
    secret_sauce: str = Field(description="The product's secret sauce or defensibility.")
    competitors: List[str] = Field(description="List of direct and indirect competitors.")

class TractionInfo(BaseModel):
    current_revenue: str = Field(description="Current and historical revenue or initial traction.")
    growth: str = Field(description="Growth metrics and scalability.")

class FinancialsInfo(BaseModel):
    raise_amount: str = Field(description="How much they are raising and terms.")
    burn_rate: str = Field(description="Current monthly burn rate and cash runway.")

class ExtractorOutput(BaseModel):
    startup_stage: str = Field(description="The deduced stage of the startup (Pre-Seed, Seed, Series A, Growth/Late Stage)")
    team: TeamInfo
    market: MarketInfo
    product: ProductInfo
    traction: TractionInfo
    financials: FinancialsInfo

class VerifiedClaim(BaseModel):
    claim: str = Field(description="The original claim from the pitch deck")
    is_verified: bool = Field(description="Whether the claim is supported by search results")
    evidence_url: Optional[str] = Field(description="URL supporting the claim, if any")
    notes: str = Field(description="Brief note on findings")

class RedFlag(BaseModel):
    description: str = Field(description="Description of the discrepancy or red flag")
    severity: str = Field(description="Severity (Low, Medium, High)")
    source_url: Optional[str] = Field(description="URL refuting the claim, if any")

class VerifierOutput(BaseModel):
    verified_claims: List[VerifiedClaim]
    red_flags: List[RedFlag]

class EvaluationLLMOutput(BaseModel):
    team_score: int = Field(description="0-100 score for Team based on verification")
    team_reason: str = Field(description="Explanation for the Team score based on due diligence checklist")
    market_score: int = Field(description="0-100 score for Market based on verification")
    market_reason: str = Field(description="Explanation for the Market score based on due diligence checklist")
    product_score: int = Field(description="0-100 score for Product/IP based on verification")
    product_reason: str = Field(description="Explanation for the Product score based on due diligence checklist")
    traction_score: int = Field(description="0-100 score for Traction based on verification")
    traction_reason: str = Field(description="Explanation for the Traction score based on due diligence checklist")
    financials_score: int = Field(description="0-100 score for Financials based on verification")
    financials_reason: str = Field(description="Explanation for the Financials score based on due diligence checklist")
    executive_summary: str = Field(description="Concise executive summary of the startup and final recommendation")

class EvaluationOutput(BaseModel):
    team_score: int
    team_reason: str
    market_score: int
    market_reason: str
    product_score: int
    product_reason: str
    traction_score: int
    traction_reason: str
    financials_score: int
    financials_reason: str
    upside_conviction_score: int
    execution_risk_score: int
    investment_decision: str
    executive_summary: str
