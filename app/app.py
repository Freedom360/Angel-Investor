import streamlit as st
import os
from dotenv import load_dotenv

from extractor import ExtractorAgent
from verifier import VerifierAgent
from evaluator import EvaluatorAgent

load_dotenv()

st.set_page_config(page_title="Angel Insight MVP", page_icon="👼", layout="wide")

st.title("👼 Angel Insight MVP (Due Diligence Agent)")
st.markdown("Instantly evaluate startup pitch decks against web data to generate a Confidence Score.")

# Sidebar for API Keys
with st.sidebar:
    st.header("Configuration")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password", help="Get this from Google AI Studio")
    tavily_key = st.text_input("Tavily API Key", value=os.getenv("TAVILY_API_KEY", ""), type="password", help="Get this from tavily.com")
    
    st.markdown("---")
    st.markdown("**Scoring Algorithm:**")
    st.markdown("- Team: 30%")
    st.markdown("- Market: 20%")
    st.markdown("- Traction: 20%")
    st.markdown("- Product/IP: 15%")
    st.markdown("- Financials: 15%")
    st.markdown("*-15 points per Red Flag*")

# Main Page
uploaded_file = st.file_uploader("Upload Pitch Deck (PDF)", type=["pdf"])
custom_links_text = st.text_area("Additional Reference Links (Optional)", help="Paste URLs (one per line) like the company website or founder LinkedIn to ensure they are analyzed.", height=68)
custom_links = [url.strip() for url in custom_links_text.split('\n') if url.strip()]

if st.button("Run Due Diligence"):
    if not uploaded_file:
        st.error("Please upload a PDF pitch deck.")
    elif not gemini_key or not tavily_key:
        st.error("Please enter both API keys in the sidebar.")
    else:
        pdf_bytes = uploaded_file.read()
        
        with st.status("Running Due Diligence Pipeline...", expanded=True) as status:
            try:
                # Agent 1
                st.write("🕵️ Agent 1 (The Extractor): Parsing PDF to structured data...")
                extractor = ExtractorAgent(api_key=gemini_key)
                extracted_data = extractor.extract(pdf_bytes)
                st.write("✅ Extraction complete.")
                
                # Agent 2
                st.write("🔎 Agent 2 (The Verifier): Fact checking claims via Web Search...")
                verifier = VerifierAgent(gemini_api_key=gemini_key, tavily_api_key=tavily_key)
                verified_data = verifier.verify(extracted_data, custom_links=custom_links)
                st.write("✅ Verification complete.")
                
                # Agent 3
                st.write("⚖️ Agent 3 (The Evaluator): Calculating Confidence Score...")
                evaluator = EvaluatorAgent(api_key=gemini_key)
                eval_data = evaluator.evaluate(extracted_data=extracted_data, verification_data=verified_data)
                st.write("✅ Evaluation complete.")
                
                # --- NEW: Save to Local Storage ---
                import datetime, json
                os.makedirs("reports", exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = uploaded_file.name.replace(".pdf", "")
                report_path = os.path.join("reports", f"{safe_filename}_{timestamp}.json")
                
                full_report = {
                    "filename": uploaded_file.name,
                    "timestamp": timestamp,
                    "extracted_data": extracted_data.model_dump(),
                    "verified_data": verified_data.model_dump(),
                    "evaluation_data": eval_data.model_dump()
                }
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(full_report, f, indent=4)
                    
                st.write(f"💾 Report saved to local storage: `{report_path}`")
                
                status.update(label="Due Diligence Complete!", state="complete", expanded=False)
                
                # Layout Results
                st.markdown("---")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.header("Executive Summary")
                    # Big Metric 
                    delta_text = f"-{eval_data.execution_risk_score} Execution Risk" if eval_data.execution_risk_score > 0 else None
                    st.metric("Upside Conviction", f"{eval_data.upside_conviction_score} / 100", delta=delta_text, delta_color="inverse")
                    st.markdown(f"### Decision: {eval_data.investment_decision}")
                    st.markdown(eval_data.executive_summary)
                    
                    st.subheader("Pillar Scores")
                    st.progress(eval_data.team_score / 100.0, text=f"Team ({eval_data.team_score})")
                    with st.expander("Team Score Reasoning"):
                        st.write(eval_data.team_reason)
                        
                    st.progress(eval_data.market_score / 100.0, text=f"Market ({eval_data.market_score})")
                    with st.expander("Market Score Reasoning"):
                        st.write(eval_data.market_reason)
                        
                    st.progress(eval_data.product_score / 100.0, text=f"Product ({eval_data.product_score})")
                    with st.expander("Product Score Reasoning"):
                        st.write(eval_data.product_reason)
                        
                    st.progress(eval_data.traction_score / 100.0, text=f"Traction ({eval_data.traction_score})")
                    with st.expander("Traction Score Reasoning"):
                        st.write(eval_data.traction_reason)
                        
                    st.progress(eval_data.financials_score / 100.0, text=f"Financials ({eval_data.financials_score})")
                    with st.expander("Financials Score Reasoning"):
                        st.write(eval_data.financials_reason)
                    
                with col2:
                    st.header("Evidence Log & Red Flags")
                    
                    if verified_data.red_flags:
                        st.error(f"Found {len(verified_data.red_flags)} Red Flags")
                        for rf in verified_data.red_flags:
                            with st.expander(f"🚩 {rf.severity} Severity: {rf.description}"):
                                if rf.source_url:
                                    st.markdown(f"[Source Evidence]({rf.source_url})")
                                    
                    st.subheader("Verified Claims")
                    for vc in verified_data.verified_claims:
                        icon = "✅" if vc.is_verified else "❓"
                        with st.expander(f"{icon} {vc.claim}"):
                            st.write(vc.notes)
                            if vc.evidence_url:
                                st.markdown(f"[Supporting Source]({vc.evidence_url})")

            except Exception as e:
                status.update(label="Pipeline Failed", state="error")
                st.error(f"An error occurred: {str(e)}")
