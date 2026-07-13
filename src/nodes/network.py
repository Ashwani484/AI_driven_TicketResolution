from typing import Optional,TypedDict
from unittest import result

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from src.llm import init_llm,llm_explanation
from datetime import datetime,date
from src.paths import *
from src.log import setup_logger

logs=setup_logger(LOG_DIR)
logs.info("Network Node Initiated.....")

llm=init_llm("grok")

class networkstate(TypedDict):
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

def network_node(state:networkstate):
    print("Network node executed.")
    print(f"Incident Number: {state['inc_number']}")
    return {"solution": "Network Node runbook is triggered by ansible and issue resolved", "resolution_time": date, "state": "Resolved", "resolved_by": "AgenticAI_AKS"}
    
