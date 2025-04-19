from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor
import shutil
import os
import sqlite3
import uuid
from . import app
from .config import Config
from .core.file_processor import FileProcessor
from .core.vector_store import VectorStoreManager
from .core.qa_system import QuestionAnswerSystem

executor = ThreadPoolExecutor(max_workers=4)
file_processor = FileProcessor()
vector_store_manager = VectorStoreManager()
qa_system = QuestionAnswerSystem()


conversations = {}

@app.route("/api/embedding", methods=["POST"])
def embed_document():
    if "document" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No document provided"
        }), 400
    
    file = request.files["document"]
    if file.filename == "":
        return jsonify({
            "status": "error",
            "message": "Empty filename"
        }), 400

    # Generate a unique document ID
    document_id = str(uuid.uuid4())
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.doc', '.docx', '.txt']:  # Added .txt support
        return jsonify({
            "status": "error",
            "message": "Unsupported file type"
        }), 400

    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)
    
    # Process the document in background
    executor.submit(process_document_for_embedding, temp_path, document_id)
    
    return jsonify({
        "status": "success",
        "message": "Document embedding started successfully",
        "document_id": document_id
    })


def process_document_for_embedding(temp_path, document_id):
    try:
    
        documents = FileProcessor.process_file(temp_path)
        if not documents:
            app.logger.error(f"No valid content found in document {document_id}")
            return

        vector_store_manager.create_vector_store(documents, document_id)
        app.logger.info(f"Document {document_id} processed successfully")

    except Exception as e:
        app.logger.error(f"Error processing document {document_id}: {str(e)}")

    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            app.logger.error(f"Error removing temp file {temp_path}: {str(e)}")


@app.route("/api/query", methods=["POST"])
def query_document():
    data = request.json
    if not data or "query" not in data or "document_id" not in data:
        return jsonify({
            "status": "error",
            "message": "Missing required fields (query or document_id)"
        }), 400

    document_id = data["document_id"]
    query = data["query"]
    require_citations = data.get("require_citations", True)
    conversation_id = data.get("conversation_id")

    # Check if document exists
    db_path = os.path.join(Config.VECTOR_STORE_DIR, document_id)
    if not os.path.exists(db_path):
        return jsonify({
            "status": "error",
            "message": "Document not found"
        }), 404

    # Handle conversation
    if conversation_id and conversation_id not in conversations:
        return jsonify({
            "status": "error",
            "message": "Invalid conversation ID"
        }), 400

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = []

    # Process the query
    try:
        result = qa_system.process_question(
            question=query,
            db_name=document_id,
            conversation_history=conversations[conversation_id],
            require_citations=require_citations
        )

        # Update conversation history
        conversations[conversation_id].append({
            "query": query,
            "answer": result["answer"],
            "citations": result.get("citations", [])
        })

        response = {
            "status": "success",
            "response": {
                "answer": result["answer"],
                "citations": result.get("citations", [])
            }
        }

        if len(conversations[conversation_id]) == 1:
            response["conversation_id"] = conversation_id

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

