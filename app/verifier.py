import json
from google import genai
from google.genai import types
from tavily import TavilyClient
from schemas import ExtractorOutput, VerifierOutput
from utils import retry_on_demand_error

class VerifierAgent:
    def __init__(self, gemini_api_key: str, tavily_api_key: str):
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        
    @retry_on_demand_error()
    def verify(self, extracted_data: ExtractorOutput, custom_links: list = None) -> VerifierOutput:
        custom_links = custom_links or []
        prompt = f"""
        Based on the following extracted startup data, generate a list of 5-7 specific Google search queries to verify key claims.
        
        CRITICAL SEARCH STRATEGY:
        1. Social Sentiment: Explicitly target "Google Trends", "Reddit", "customer reviews", or social media keywords to assess market sentiment and verify if customers actually care about the problem/solution.
        2. Startup Ecosystem: Explicitly query definitive startup ecosystem databases and VC sites (e.g., site:crunchbase.com, site:wellfound.com, Built In, Y Combinator, a16z, Khosla Ventures) to triangulate the startup's footprint, direct competitors, and funding history.
        
        MUST Return a raw JSON list of strings representing the exact search queries. Do not use markdown blocks.
        Data: {extracted_data.model_dump_json()}
        """
        response = self.gemini_client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
        )
        try:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            queries = json.loads(text)
        except:
            # Fallback queries
            queries = [
                f"Market size for {extracted_data.market.market_size}",
                f"{extracted_data.product.description} competitors"
            ]
            
        search_context = []
        
        for link in custom_links:
            try:
                res = self.tavily_client.search(f"{link}", search_depth="basic")
                search_context.append({"query": f"User Provided Link: {link}", "results": res.get("results", [])})
            except Exception as e:
                print(f"Search failed for custom link {link}: {e}")
                
        for q in queries[:4]:
            try:
                res = self.tavily_client.search(q, search_depth="basic")
                search_context.append({"query": q, "results": res.get("results", [])})
            except Exception as e:
                print(f"Search failed for {q}: {e}")
                
        verify_prompt = f"""
        You are a due diligence market analyst. Compare the startup's claims against the search results context.
        Identify what is verified and assess overarching market sentiment based on the searches.
        
        CRITICAL RULES:
        1. HISTORICAL CONTEXT (The Time Machine Rule): You must account for when the pitch deck was created. Do NOT penalize a historical pitch deck if its claims (e.g. "market size is 2 Billion") were accurate for that year but seem small today. Cross-reference past claims contextually.
        2. PLAUSIBILITY OVER STRICT FACTS: Pitch decks contain subjective forward-looking projections. Assess the *plausibility* of the solution and market trends. Do not force strict binary True/False fact checks on visionary predictions.
        3. PRIVATE METRICS & FUTURE PLANS: If a claim involves private operating metrics (e.g. "scaled to $120M ARR") or future dates/plans, do NOT flag it as 'unverified' or create a red flag simply because it can't be found on public search. Treat private/future claims as neutral unless contradictory evidence is found.
        4. URL SOURCING: You MUST provide links for `evidence_url` and `source_url`. To prevent hallucination, you MUST ONLY use exact URLs provided in the "url" fields within the Search Results JSON below. NEVER synthesize or guess a URL.
        5. SEVERITY RATING: When flagging a discrepancy, be realistic about early-stage companies:
            - "High": Outright fraud, fake founder backgrounds, massive legal or regulatory blockers.
            - "Medium": Fundamental business model miscalculations, ignoring a massive direct competitor.
            - "Low": Minor statistical differences, outdated numbers, spelling errors.
        
        Startup Claims: {extracted_data.model_dump_json()}
        Search Results: {json.dumps(search_context)}
        """
        
        verify_response = self.gemini_client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=verify_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VerifierOutput,
            ),
        )
        return VerifierOutput.model_validate_json(verify_response.text)
