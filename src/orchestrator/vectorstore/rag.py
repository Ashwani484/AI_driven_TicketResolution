import os
import re
import json
import datetime
import logging
from src.paths import *
from src.log import setup_logger

# LangChain Imports
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PyPDFLoader, UnstructuredMarkdownLoader, 
    UnstructuredExcelLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = setup_logger(LOG_DIR)

# Ensure this matches your configuration environment
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 
knowledge_base_dir = r"D:\AI-Projects\Self_developed_AI\Agentic_ServiceNow_Ticket_Resolution\knowledgebase"

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_file(self, category):
        """
        Scans the directory and loads documents. 
        Specially processes JSON files to preserve KB structure and metadata.
        """
        logger.info(f"Scanning directory: {knowledge_base_dir}")
        
        if os.path.exists(knowledge_base_dir):        
            entries = os.listdir(knowledge_base_dir)
            filenames = [f for f in entries if os.path.isfile(os.path.join(knowledge_base_dir, f))]
        else:
            logger.error(f"Error: Directory '{knowledge_base_dir}' not found.")
            return []

        # Normalized mapping for file matching based on your 3 nodes
        # Matches category inputs to file prefix structures
        category_lower = category.lower().replace(" ", "_")
        
        all_documents = []

        for file_name in filenames:
            file_name_lower = file_name.lower()
            
            # Check if the file corresponds to the requested category node
            if category_lower in file_name_lower:
                ext = os.path.splitext(file_name)[-1].lower()
                file_path = os.path.join(knowledge_base_dir, file_name)
                logger.info(f"Processing file: {file_name} with extension: {ext}")

                try:
                    # --- Optimized JSON KB Processor ---
                    if ext == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            kb_data = json.load(f)
                        
                        # Handle both single objects or lists of items
                        if isinstance(kb_data, dict):
                            kb_data = [kb_data]
                            
                        for item in kb_data:
                            # Format steps and keywords for clear text representation
                            steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(item.get("resolution_steps", []))])
                            keywords = ", ".join(item.get("keywords", []))
                            
                            # Construct an explicit, searchable text string for vectorization
                            page_content = (
                                f"Category: {item.get('category')}\n"
                                f"Title: {item.get('title')}\n"
                                f"Symptoms: {item.get('symptoms')}\n"
                                f"Root Cause Analysis: {item.get('root_cause_analysis')}\n"
                                f"Resolution Steps:\n{steps}\n"
                                f"Keywords: {keywords}"
                            )
                            
                            # Retain item properties as rich metadata for filtering/re-ranking
                            metadata = {
                                "kb_id": item.get("kb_id"),
                                "category": item.get("category"),
                                "title": item.get("title"),
                                "source": file_name
                            }
                            
                            all_documents.append(Document(page_content=page_content, metadata=metadata))
                        logger.info(f"Successfully loaded {len(kb_data)} structured KB articles from JSON.")
                    
                    # --- Legacy/Alternative File Loaders ---
                    elif ext == '.txt':
                        loader = TextLoader(file_path, encoding='utf-8')
                        all_documents.extend(loader.load())
                    elif ext == '.csv':
                        loader = CSVLoader(file_path)
                        all_documents.extend(loader.load())
                    elif ext == '.pdf':
                        loader = PyPDFLoader(file_path)
                        all_documents.extend(loader.load())
                    elif ext == '.md':
                        loader = UnstructuredMarkdownLoader(file_path)
                        all_documents.extend(loader.load())
                    elif ext in ['.xlsx', '.xls']:
                        loader = UnstructuredExcelLoader(file_path)            
                        all_documents.extend(loader.load())
                    else:
                        logger.warning(f"Unsupported file format: {ext}. Skipping {file_name}.")
                        
                except Exception as e:
                    logger.error(f"Error loading file {file_name}: {e}")
                    
        return all_documents

    def rag_db(self, categ):
        """
        Creates a FAISS vector database from loaded documents.
        Preserves individual document contexts rather than squashing objects together.
        """
        docs = self.load_file(category=categ)
        if not docs:
            logger.warning(f"No documents found or loaded for category: {categ}")
            return None
            
        logger.info(f"Processing {len(docs)} document structures for Vector Store updates.")
        
        # Split documents using the text splitter while maintaining separate metadata profiles
        final_chunks = self.text_splitter.split_documents(docs)
        
        logger.info(f"Total chunks created for vector store: {len(final_chunks)}")
        
        # Initialize HuggingFace Embeddings
        embeddings_engine = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL, 
            model_kwargs={'device': 'cpu'}
        )

        # Build FAISS vector store seamlessly using the chunked documents
        vectorstore = FAISS.from_documents(final_chunks, embeddings_engine)
        return vectorstore
    



    