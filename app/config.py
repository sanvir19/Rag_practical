import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GORQ_API_KEY") 
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    LLM_MODEL = "llama-3.3-70b-versatile" 
    VECTOR_STORE_DIR = "faiss_index"
    AGENCY_API_URL = "https://ticketz.1automations.com/apiagency/get_setting/domain"
    CHUNK_SIZE = 10000
    CHUNK_OVERLAP = 2000
    DEFAULT_PROMPT_TEMPLATE = """
    You are an AI assistant. Answer based on context below.

    Context: {context}

    Question: {question}

    Answer:"""





