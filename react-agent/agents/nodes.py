from .state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from tools.sec_tools import get_rag_context

def extract_text_from_response(content) -> str:
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n\n".join(parts)
    return str(content)

class ExtractedInfo(BaseModel):
    ticker: str = Field(description="The stock ticker symbol (e.g. AAPL, MSFT)")
    form_type: str = Field(description="The SEC form type requested, usually 10-K or 10-Q", default="10-K")

def data_fetcher_node(state: AgentState) -> dict:
    print("--- RUNNING DATA FETCHER AGENT ---")
    user_input = state["user_input"]
    
    model_name = state.get("selected_model") or "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, max_retries=3)
    structured_llm = llm.with_structured_output(ExtractedInfo)
    
    try:
        extracted = structured_llm.invoke([
            SystemMessage(content="Extract the company stock ticker symbol and SEC form type (10-K or 10-Q) from the user's request. Default to 10-K if not obvious."),
            HumanMessage(content=user_input)
        ])
        
        if not extracted or not extracted.ticker:
            return {"error": "Could not identify a ticker symbol from the request."}
            
        ticker = extracted.ticker.upper()
        form_type = extracted.form_type.upper()
        
        # We do not fetch text directly anymore. We've loaded the Pinecone index with the pulls.
        return {"ticker": ticker, "form_type": form_type, "filing_text": "Using Pinecone RAG"}
        
    except Exception as e:
         return {"error": f"Failed to extract info: {str(e)}"}

def analyst_node(state: AgentState) -> dict:
    print("--- RUNNING ANALYST AGENT ---")
    if state.get("error"):
        return state # skip if error
        
    model_name = state.get("selected_model") or "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, max_retries=3)
    
    # Run RAG Query based on user request instead of processing the entire filing
    rag_context = get_rag_context(
        ticker=state["ticker"], 
        form_type=state["form_type"], 
        query="financial performance, risk factors, strategic initiatives",
        top_k=20
    )
    
    prompt = f"""
    You are an expert Financial Analyst. 
    Review the following retrieved RAG context snippets from a {state['form_type']} filing for {state['ticker']}.
    Extract the key financial performance signals, major risk factors, and strategic initiatives mentioned.
    
    RAG Context:
    {rag_context}
    
    Format your analysis cleanly with Markdown headers (Financial Performance, Risk Factors, Strategic Initiatives).
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"analysis": extract_text_from_response(response.content)}

def advisor_node(state: AgentState) -> dict:
    print("--- RUNNING ADVISOR AGENT ---")
    if state.get("error"):
        return state
        
    model_name = state.get("selected_model") or "gemini-2.0-flash"
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3, max_retries=3)
    
    prompt = f"""
    You are a Senior Investment Advisor specializing in stock market sector analysis. 
    Based on the following financial analysis of {state['ticker']}'s recent {state['form_type']} filing, 
    provide sector-specific investment advice. 
    
    Is it a buy, hold, or sell in the current market environment? 
    What are the key takeaways for an investor looking at this stock's sector?
    
    Financial Analyst's Report:
    {state['analysis']}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"advice": extract_text_from_response(response.content)}
