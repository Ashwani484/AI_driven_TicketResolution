from src.orchestrator.orchestrator import Incident, Orchestrator,fetch_new_tickets
from src.engine.fastapi_backend import app
import threading
import time
import uvicorn
import subprocess
from src.paths import *
from src.log import setup_logger


logs=setup_logger(LOG_DIR)
logs.info("Cachedeletion Node Initiated.....")
# --- Thread target functions ---

def run_uvicorn():
    """Run FastAPI backend with Uvicorn."""
    uvicorn.run(
        app ,  # assuming FastAPI app 
        host="0.0.0.0",
        port=8080,
        reload=False
        
    )


def run_streamlit():
    """Run Streamlit frontend."""
    # Use subprocess so Streamlit runs as if from CLI
    subprocess.run(["streamlit", "run", "src/engine/snow_simulator.py", "--server.port", "8501"])


def run_engine():
    """Run core orchestrator/worker loop."""
    while True:
        try:
            print("Core engine polling tickets...")
            orch = Orchestrator()
            new_tickets = fetch_new_tickets()
            if not new_tickets:
                print("No new tickets found.")

            for ticket in new_tickets:
                print(f"Processing ticket: {ticket.category} - {ticket.short_description}")
                orch.run(ticket)   # your orchestrator logic
            time.sleep(5)       # poll interval
        except Exception as e:
            print("Engine error:", e)
            time.sleep(10)


# --- Thread setup ---
if __name__ == "__main__":
    threads = []

    t1 = threading.Thread(target=run_uvicorn, daemon=True)
    t2 = threading.Thread(target=run_streamlit, daemon=True)
    t3 = threading.Thread(target=run_engine, daemon=True)

    threads.extend([t1, t2, t3])
    logs.info("All the process BACKEND, FRONTEND, ORCHESTRATOR has been started....")
    # Start all threads
    for t in threads:
        t.start()

    # Keep main thread alive
    try:
        while True:
            logs.info("ORCHESTRATOR is running and looking for New INCIDENTS....")
            time.sleep(60)
    except KeyboardInterrupt:
        logs.info("Shutting down services...")



