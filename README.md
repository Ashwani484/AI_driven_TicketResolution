# AI-driven Ticket Resolution Orchestrator

## 📌 Overview
This project implements an **AI + Human-in-the-Loop ticket resolution system**.  
It combines:
- **FastAPI (Uvicorn)** → Backend API for incident management
- **Streamlit** → Frontend simulator for ServiceNow-like ticket UI
- **Core Engine (Orchestrator)** → Automates ticket classification, resolution, and escalation

The orchestrator leverages **LangGraph**, **LLM (GenAI)**, and **SQLAlchemy** to process tickets, route them to specialized nodes, and escalate sensitive cases to humans.

---

## ⚙️ Workflow

### 1. Ticket Ingestion
- Tickets are stored in a SQLite database (`incidents.db`).
- Each ticket has fields like `inc_number`, `category`, `urgency`, `state`, `short_description`, and `full_description`.

### 2. Extractor Node
- Pulls new tickets (`state == "New"`) from the DB.
- Converts them into a structured `incidentstate` dictionary for downstream processing.

### 3. Retrieval Node (RAG + LLM)
- Runs **RAG (Retrieval-Augmented Generation)** lookup using `DocumentProcessor`.
- Queries vector store for relevant solutions based on ticket category and description.
- Generates AI-driven resolution notes via `llm_explanation`.

### 4. Routing Logic
- Tickets are routed based on **category**:
  - `cache` → Cache deletion node
  - `network` → Network troubleshooting node
  - `server` → Server reboot node
  - `optimize` → System optimization node
- **Human-in-the-Loop**:  
  If `urgency` is **critical** or **medium**, tickets are escalated to a `human_review_node`.  
  - AI does not auto-resolve these.
  - Ticket state is set to `Escalated`.
  - Resolution notes indicate human validation required.

### 5. Node Execution
- Each specialized node applies corrective actions (e.g., reboot server, clear cache).
- Updates ticket with `solution`, `resolution_notes`, `resolved_by`, and `resolution_time`.

### 6. Database Update
- Orchestrator commits results back to SQLite DB.
- Tickets move from `New` → `Resolved` or `Escalated`.

---

## 🖥️ Components

- **FastAPI Backend** (`src/engine/fastapi_backend.py`)  
  Provides REST API endpoints for ticket creation, retrieval, and monitoring.

- **Streamlit Frontend** (`src/engine/snow_simulator.py`)  
  Simulates ServiceNow UI for incident management.

- **Core Engine (Orchestrator)** (`src/orchestrator/orchestrator.py`)  
  Implements the LangGraph workflow, routing, and resolution logic.

---

## 🚀 Running the System

### Local Development
Run all three components in parallel using threads:




src/
 ├── engine/
 │    ├── fastapi_backend.py   # FastAPI app
 │    └── snow_simulator.py    # Streamlit UI
 ├── orchestrator/
 │    ├── orchestrator.py      # Core workflow
 │    ├── nodes/               # Specialized resolution nodes
 │    └── vectorstore/         # RAG document processor
 └── llm.py                    # LLM initialization and explanation

