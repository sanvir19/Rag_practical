import os
from ..config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
        self.vector_store_dir = Config.VECTOR_STORE_DIR
    

    def create_vector_store(self, text_chunks, db_name):
        if not text_chunks:
            return False

        pdf_vector_path = os.path.join(self.vector_store_dir, db_name)
        os.makedirs(pdf_vector_path, exist_ok=True)

        if os.path.exists(os.path.join(pdf_vector_path, "index.faiss")):
            vector_store = FAISS.load_local(pdf_vector_path, self.embeddings, allow_dangerous_deserialization=True)
            vector_store.add_documents(text_chunks)  
        else:
            vector_store = FAISS.from_documents(text_chunks, embedding=self.embeddings)  

        vector_store.save_local(pdf_vector_path)
        return True

    
    def get_vector_store(self, db_name):
        db_path = os.path.join(self.vector_store_dir, db_name)
        return FAISS.load_local(db_path, self.embeddings, allow_dangerous_deserialization=True) \
               if os.path.exists(db_path) else None


