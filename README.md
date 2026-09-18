# MedicalResearch AI

An AI-powered research assistant for exploring and comparing medical and biotechnology literature.

Upload scientific PDFs, build a personal research library, and ask grounded questions with source attribution — powered by RAG, persistent vector storage, and multi-provider LLM support.

## Features

- **Multi-PDF RAG** — Index and query across multiple research papers
- **Persistent Chroma DB** — Separate indexing and query pipelines; vectors survive restarts
- **Document scope filtering** — Query all papers or focus on one
- **Source attribution** — Every answer cites document name and page
- **LLM fallback** — Gemini primary with automatic Cohere fallback on quota/rate limits
- **Research-focused UI** — Modern chatbot interface with research library sidebar

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_key
COHERE_API_KEY=your_cohere_key
PRIMARY_LLM=gemini
FALLBACK_LLM=cohere
EMBEDDING_PROVIDER=cohere
```

### 3. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/documents/upload` | Upload and index a PDF |
| `GET` | `/documents` | List indexed documents |
| `GET` | `/documents/{id}/file` | Download/view a PDF |
| `DELETE` | `/documents/{id}` | Remove document and vectors |
| `POST` | `/chat` | Ask a question |

### Chat request example

```json
{
  "question": "What are the main applications of AI in drug discovery?",
  "document_id": null,
  "history": []
}
```

## Architecture

```text
PDF Upload → Validate → Hash → Chunk → Embed → Chroma (persistent)
Question → Retriever (scoped) → Context → LLM → Answer + Sources
```

## Project Structure

```text
app/
├── api/          FastAPI routes
├── core/         Config, logging, exceptions
├── documents/    Upload, registry, indexing
├── rag/          Loader, splitter, embeddings, vectorstore, chain
├── llm/          Gemini, Cohere, fallback manager
└── models/       Pydantic schemas

frontend/         HTML/CSS/JS chatbot UI
data/
├── uploads/      Stored PDFs
├── chroma_db/    Vector database
└── documents.json Document registry
```

## Disclaimer

MedicalResearch AI is a research assistant and does not provide medical diagnosis or treatment advice. Answers are based solely on uploaded research literature.
