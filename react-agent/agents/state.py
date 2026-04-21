from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_input: str
    selected_model: Optional[str]
    ticker: Optional[str]
    form_type: Optional[str]
    filing_text: Optional[str]
    analysis: Optional[str]
    advice: Optional[str]
    error: Optional[str]
