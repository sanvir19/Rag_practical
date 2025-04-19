# Document QA System

![System Architecture](docs/system_architecture.png)

A production-ready document processing and question-answering API supporting PDF, DOCX, and TXT files with semantic search capabilities.

## Features

- 📄 Multi-format document processing (PDF, DOCX, TXT)
- 🔍 Hybrid text extraction (direct + OCR fallback)
- 💬 Context-aware conversational QA
- 📑 Automated citation generation
- ⚡ High-performance (300+ tokens/sec via Groq)

## Quick Start

### Prerequisites
- Python 3.8+
- Tesseract OCR (`apt install tesseract-ocr` for Linux)

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/document-qa-system.git
cd document-qa-system

# Setup environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
echo "GORQ_API_KEY=your_groq_api_key" > .env

# Launch server
flask run

## API Documentation

### Base URL
`http://localhost:5000/api`

### Endpoints

#### 1. Document Upload

# Request Body:
```curl -X POST -F "document=@sample.pdf" http://localhost:5000/api/embedding
Content-Type: multipart/form-data

# Success Response
{
  "status": "success",
  "document_id": "uuid4_string",
  "message": "Document processing started"
}

2. Document Query
  POST /query
Content-Type: application/json

# Request Body:
{
  "document_id": "string (required)",
  "query": "what is capital of france",
  "conversation_id": "string (optional)",
  "require_citations": "boolean (default: true)"
}

# Success Response:
{
  "answer": "The capital of France is Paris...",
  "citations": [
    {"page": 42, "source": "world_facts.pdf"},
    {"page": 15, "source": "world_facts.pdf"}
  ],
  "conversation_id": "uuid4_string"
}

