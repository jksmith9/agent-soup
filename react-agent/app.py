import streamlit as st
import os
from dotenv import load_dotenv
from agents.graph import build_graph

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Multi-Agent SEC Analyst", page_icon="📈", layout="wide")

st.title("📈 Multi-Agent SEC 10-K & 10-Q Analyst")
st.markdown("""
This application uses LangGraph and Google Gemini to orchestrate a set of specialized agents:
1. **Data Fetcher Agent**: Resolves stock tickers and downloads SEC filings.
2. **Financial Analyst Agent**: Extracts signals and risks from the text.
3. **Investment Advisor Agent**: Formulates sector advice.
""")

import urllib.request
import json

@st.cache_data
def get_available_models(api_key: str):
    url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            # Grab all models that support generation
            models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            # Strip 'models/' prefix so ChatGoogleGenerativeAI likes it implicitly if needed, actually it doesn't matter, but keeping full name is fine
            return [m.replace("models/", "") for m in models]
    except Exception as e:
        return ["gemini-2.0-flash", "gemini-1.5-pro"] # basic fallback

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    st.warning("⚠️ Please set your GOOGLE_API_KEY in the `.env` file to use this app.")
    st.stop()

available_models = get_available_models(api_key)
# Find a sensible default index
default_idx = available_models.index("gemma-4-31b-it") if "gemma-4-31b-it" in available_models else 0

selected_model = st.selectbox("Select Gemini Model", options=available_models, index=default_idx)

@st.cache_resource
def get_graph():
    return build_graph()

app_graph = get_graph()

user_prompt = st.text_input("What would you like to analyze?", placeholder="e.g., Analyze the latest 10-K for MSFT and offer Tech sector investment advice.")

if st.button("Analyze"):
    if not user_prompt:
        st.error("Please enter a prompt.")
    else:
        with st.status("Agents are working...", expanded=True) as status:
            try:
                st.write("🟢 Starting workflow...")
                initial_state = {"user_input": user_prompt, "selected_model": selected_model}
                
                final_advice = None
                
                for output in app_graph.stream(initial_state):
                    for key, value in output.items():
                        st.write(f"🔄 **{key.replace('_', ' ').title()} Agent** finished processing.")
                        
                        if value.get("error"):
                            st.error(value["error"])
                            status.update(label="Analysis failed.", state="error")
                            st.stop()
                            
                        if key == "data_fetcher":
                            st.success(f"Identified {value.get('ticker')} and fetched {value.get('form_type')}.")
                            with st.expander("View SEC Text Preview (Truncated)"):
                                st.write(value.get("filing_text")[:2000] + "...")
                        elif key == "analyst":
                            st.info("Analysis extraction complete.")
                            with st.expander("View Interim Financial Analysis"):
                                st.markdown(value.get("analysis"))
                        elif key == "advisor":
                            final_advice = value.get("advice")
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)
                
                if final_advice:
                    st.subheader("Final Investment Advice")
                    st.markdown(final_advice)
                
            except Exception as e:
                status.update(label="An error occurred.", state="error")
                st.error(f"Error: {str(e)}")
