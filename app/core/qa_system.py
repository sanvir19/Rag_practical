from ..config import Config
from langchain_groq import ChatGroq
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from .vector_store import VectorStoreManager

class QuestionAnswerSystem:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=Config.GROQ_API_KEY, 
            model_name=Config.LLM_MODEL
        )
        self.prompt_cache = {}
        self.default_prompt = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        {context}
        Question: {question}
        Answer:"""
    
    def get_conversational_chain(self, require_citations=False):
        template = self.default_prompt
        if require_citations:
            template += "\n\nPlease provide citations from the document where relevant."
        
        if template not in self.prompt_cache:
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )
            self.prompt_cache[template] = load_qa_chain(
                self.llm, 
                chain_type="stuff", 
                prompt=prompt
            )
        return self.prompt_cache[template]

    def process_question(self, question, db_name, conversation_history=None, require_citations=True):
        vector_store_manager = VectorStoreManager()
        db = vector_store_manager.get_vector_store(db_name)
        if not db:
            return {"answer": "I couldn't find the requested document.", "citations": []}

        # Get relevant document chunks
        docs = db.similarity_search(question, k=3)
        if not docs:
            return {"answer": "I couldn't find relevant information in the document.", "citations": []}

        # Prepare context with conversation history
        context = "\n\n".join([doc.page_content for doc in docs])
        if conversation_history:
            history_context = "\n\nPrevious conversation:\n" + "\n".join(
                [f"Q: {msg['query']}\nA: {msg['answer']}" 
                 for msg in conversation_history[-3:]])  # Keep last 3 exchanges
            context = history_context + "\n\nCurrent context:\n" + context

        # Process the question
        chain = self.get_conversational_chain(require_citations)
        response = chain({
            "input_documents": docs,
            "question": question
        }, return_only_outputs=True)

        # Extract citations
        citations = []
        if require_citations:
            citations = [
                {
                    "page": doc.metadata.get("page", "unknown"),
                    "document_name": doc.metadata.get("source", "document")
                }
                for doc in docs if hasattr(doc, 'metadata')
            ]

        return {
            "answer": response.get("output_text", "I couldn't generate a response."),
            "citations": citations
        }







