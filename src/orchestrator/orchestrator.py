from typing import Optional,TypedDict
from datetime import datetime,date
from langgraph.graph import StateGraph, END
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.nodes.cachedelete import cachedeletion
from src.nodes.network import network_node
from src.nodes.server_reboot import server_reboot
from src.nodes.sys_optimization import sys_optimization
from src.paths import *
from src.log import setup_logger
from src.orchestrator.vectorstore.rag import DocumentProcessor
from src.llm import init_llm,llm_explanation


logs=setup_logger(LOG_DIR)
logs.info("Orchestrator agent Initiated.....")
llm=init_llm("grok")
# Database setup
DATABASE_URL = "sqlite:///./sql_db/incidents.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    inc_number = Column(String, unique=True, index=True)
    category = Column(String)
    creation_date = Column(String)
    state = Column(String)
    urgency = Column(String)
    assigned_to = Column(String)
    open_by = Column(String)
    short_description = Column(String)
    full_description = Column(String)
        # Agentic fields
    solution = Column(String)
    resolution_time = Column(String)
    escalated_to = Column(String)
    work_notes = Column(String)
    resolved_by = Column(String)
    
Base.metadata.create_all(bind=engine)



class incidentstate(TypedDict):
    inc_number: str
    category: str
    state: str
    urgency:str
    short_description: str
    full_description: str
    # Agentic fields
    solution: str
    resolution_time: String
    escalated_to: String
    work_notes: String
    resolved_by: str = str

def fetch_new_tickets():
    """Fetch all tickets with state == 'New'."""
    db = SessionLocal()
    try:
        tickets = db.query(Incident).filter(Incident.state == "New").all()
        return tickets
    finally:
        db.close()


# Extractor node must accept a single Incident instance, it takes the ticket as input from DB instance 
# and returns an incidentstate dict with the relevant fields for routing and processing. 
def extractor(ticket: Incident) -> incidentstate:
    logs.info(f"Extractor node processing ticket: {ticket['inc_number']}")
    if ticket['state'] == "New":
        return {
            "category": ticket['category'],
            "state": ticket['state'],
            "short_description": ticket['short_description'],
            "full_description": ticket['full_description']
        }
    return {}

def retrieval_node(state: incidentstate) -> incidentstate:
    logs.info("Retrieval node running RAG lookup")
    try:
        rag_processor=DocumentProcessor()
        logs.info("RAG DB initiated")
        
    except Exception as e:
        logs.info("Vector store import failed:", e)
        state["work_notes"] = []
        return state
    list_categ=['network','server']
    createg=state.get("category")
    text = state.get("full_description")
    if not text or createg not in list_categ:
        results=[]
        llm_response=llm_explanation(llm,str(state["short_description"]),str(state["full_description"]),results)
        state["work_notes"] = llm_response
        return state
    elif  state.get("urgency") in ["Critical", "Medium","High"]:
         logs.info("Human in the Loop required due to critical problem")
         return state
    else:
        try:
            results = []
            logs.info("retrival started")
            db=rag_processor.rag_db(createg)
            results = db.similarity_search(text, k=1)
            llm_response=llm_explanation(llm,str(state["short_description"]),str(state["full_description"]),results)
            #logs.info(f"LLM Response: {llm_response}")
            state["work_notes"] = llm_response

        except Exception as e:
            logs.info("RAG query failed:", e)
            state["work_notes"] = []
    return state


def human_review_node(state: incidentstate) -> incidentstate:
    logs.info("Human review required for this ticket")
    state["solution"] = None
    state["work_notes"] = "Escalated for Human validation due to HIGH PRIORITY and High Risk"
    state["resolved_by"] = "Human"
    state["state"] = "Hold"
    state["escalated_to"]="L3 Engineer"
    return state


class Orchestrator:
    def __init__(self):
        workflow = StateGraph(incidentstate)
        workflow.add_node("retrieval", retrieval_node)
        workflow.add_node("extractor", extractor)
        workflow.add_node("cachedelete", cachedeletion)
        workflow.add_node("network_node", network_node)
        workflow.add_node("server_reboot", server_reboot)
        workflow.add_node("sys_optimization", sys_optimization)
        workflow.add_node("human_review", human_review_node)

        workflow.set_entry_point("extractor")

        def route_by_category(state: incidentstate):
            logs.info(f"Routing based on category: {state['category']}")
            logs.info(f"Routing based on category: {state}")
            # Human-in-the-loop condition
            if state.get("urgency") in ["Critical", "Medium","High"]:
                return "human_review"
            if state['category'] == "cache":
                return "cachedelete"
            elif state['category'] == "network":
                return "network_node"
            elif state['category'] == "server":
                logs.info("Routing to server reboot node")
                return "server_reboot"
            elif state['category'] == "optimize":
                return "sys_optimization"
            else:
                logs.info("Unknown category, routing to END")
                return END

        # perform retrieval before routing to nodes
        
        workflow.add_edge("extractor", "retrieval")
        workflow.add_conditional_edges("retrieval", route_by_category)
        workflow.add_edge("cachedelete", END)
        workflow.add_edge("network_node", END)
        workflow.add_edge("server_reboot", END)
        workflow.add_edge("sys_optimization", END)
        # Add edge so human_review ends workflow
        workflow.add_edge("human_review", END)

        self.agent_app = workflow.compile()

    def run(self, ticket):
        logs.info(f"Running orchestrator for ticket: {ticket.inc_number}")
        result = self.agent_app.invoke(ticket)
        logs.info("Workflow result:", result)
        ticket_id = ticket.inc_number
        
        db = SessionLocal()
        
        incident = db.query(Incident).filter(Incident.inc_number == ticket_id).first()
        if incident and result:
            incident.state = result["state"]
            incident.solution = result["solution"]
            incident.resolved_by=result["resolved_by"]
            incident.work_notes=result["work_notes"]
            incident.escalated_to=result["escalated_to"]
            incident.resolution_time=incident.creation_date
            db.commit()
            db.refresh(incident)
        db.close()
        
        return result

