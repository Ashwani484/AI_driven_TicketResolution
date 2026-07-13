from typing import Optional,TypedDict
from unittest import result
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from src.llm import init_llm,llm_explanation
from datetime import datetime,date
from src.paths import *
from src.log import setup_logger

logs=setup_logger(LOG_DIR)
logs.info("Cachedeletion Node Initiated.....")
llm=init_llm("grok")

class cachestate(TypedDict):
    inc_number: str
    category: str
    state: str
    short_description: str
    full_description: str
    # Agentic fields
    solution: str
    resolution_time: Date
    escalated_to: str
    work_notes: str
    resolved_by: str = "AgenticAI"

def cachedeletion(state:cachestate):
    print("Cache deletion node executed.")
    print(f"Incident Number: {state['inc_number']}")
    llm_response=llm_explanation(llm,str(state["short_description"]),str(state["full_description"]),SOP=None)
    print(f"LLM Response: {llm_response}")
    return {"solution": llm_response, "resolution_time": date, "state": "Resolved", "resolution_notes": "Solution implemented as per LLM recommendation.", "resolved_by": "AgenticAI_AKS"}

