PRD: Angel Insight MVP (Due Diligence Agent)

# 1. Product Vision
To provide angel investors with an instant, multi-layered "Sanity Check" on startup opportunities by cross-referencing pitch deck claims against real-world data, ultimately outputting a Confidence Score that highlights where to dig deeper.

# 2. Target User
Persona: Individual Angel Investors or Seed Fund Associates.

Problem: Manual due diligence (checking LinkedIn, searching for competitors, verifying market size) takes 3–5 hours per deck.

Goal: Reduce initial DD time from hours to <60 seconds.

# 3. Functional Requirements
Agent,Name,Primary Responsibility,Tools/Models
Agent 1,The Extractor,Parse PDF pitch deck into structured JSON based on the Core Checklist.,Gemini 1.5 Pro (Native PDF)
Agent 2,The Verifier,"Use external search to validate Team, Market, and Competitive claims.",Gemini + Google Search Tool
Agent 3,The Evaluator,Calculate confidence scores and generate the final executive verdict.,Gemini 1.5 Flash

The Scoring Methodology (The "Algorithm")
The Confidence Score (0-100) is calculated using a weighted average of five pillars:

1. Team (30%): Verification of founder backgrounds/prior exits.

2. Market (20%): Alignment of TAM/SAM claims with industry reports.

3. Product/IP (15%): Defensibility and "Secret Sauce" clarity.

4. Traction (20%): Revenue/Growth verification (if public/available).

5. Financials (15%): Sanity check on burn rate and valuation logic.

Penalty Logic: Subtract 15 points if a "Red Flag" is found (e.g., "Founder claims an exit that isn't on LinkedIn/Crunchbase").

# 4. Technical Specification
User Interface (Streamlit)
Sidebar: API Key configuration (Gemini) and specialized "Weighting" sliders (optional).

Main Page:

File Uploader (accepts .pdf).

st.status container to show real-time progress of the three agents.

Big Metric: Display the Confidence Score.

Columns: Left (Summary Report) | Right (Evidence Log & Red Flags).

Data Handling
PDF Processing: Gemini 1.5 Pro should receive the PDF bytes directly for native vision-based parsing (preserves layout/charts).

Search Queries: Agent 2 should generate specific queries:

"[Founder Name] [Company] LinkedIn"

"[Industry] market size 2026 reports"

"[Company Name] competitors and alternatives"

# 5. Success Metrics (MVP)
Latency: Entire pipeline finishes in <45 seconds.

Accuracy: Agent 1 must correctly identify at least 80% of the questions in the provided checklist from a standard deck.

Utility: The "Evidence Log" must provide at least 2 clickable links to external sources for every startup analyzed.

# 6. Out of Scope (For Future Versions)
Automated email outreach to founders.

Deep financial modeling (P&L projections).

Integration with CRM (e.g., Affinity or Salesforce).