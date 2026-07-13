import os
import glob
from pathlib import Path


########################### Artifacts #########################





# For Embedding the sentence
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector store backend: "faiss" or "postgres"
VECTOR_BACKEND = "faiss"
# Postgres DB URL (optional). Example: postgresql://user:pass@host:5432/dbname
POSTGRES_URL = None

# RAG DB Path (for faiss/local)
DB_FAISS_PATH = "vectorstore/db_faiss"



# huggingface Model 
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" 

# Logs saved
LOG_DIR="logs"

knowledge_base_dir = "knowledgebase"

