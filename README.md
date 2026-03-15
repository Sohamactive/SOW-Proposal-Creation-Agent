# AI SOW Proposal Generator

AI-powered Statement of Work and proposal generator for turning project descriptions, RFPs, and reference documents into structured proposal drafts.

The application combines:

- FastAPI backend
- multi-agent proposal pipeline
- Gemini for reasoning and embeddings
- Qdrant for retrieval over uploaded knowledge-base documents
- simple browser frontend for uploads and DOCX download

## Features

- Enter a project description in the UI
- Upload a project document for the current proposal
- Upload knowledge-base documents for retrieval
- Generate a structured proposal draft
- Download the generated proposal as a `.docx`

## Project Structure

```text
backend/
  agents/                Multi-agent proposal pipeline
  api/                   FastAPI routes
  classification/        Document classification logic
  document_processing/   PDF and DOCX parsing
  export/                DOCX/PDF/PPTX exporters
  orchestrator/          Pipeline orchestration
  rag/                   Embeddings, ingestion, retrieval, vector storage
frontend/
  index.html             Browser UI
  app.js                 Frontend logic
  style.css              Frontend styles
qdrant_storage/          Local Qdrant data
requirements.txt
```

## Requirements

- Python 3.13
- Qdrant running locally on `http://localhost:6333`
- A valid Gemini API key

## Environment Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_api_key_here
```

## Docker Compose Setup

This project now includes:

- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [.dockerignore](.dockerignore)

The Compose setup runs:

- `backend` on `http://127.0.0.1:8000`
- `qdrant` on `http://127.0.0.1:6333`

### 1. Create `.env`

Add at least:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Optional overrides:

```env
QDRANT_COLLECTION=knowledge_base
EXPORT_FOLDER=/app/generated_proposals
```

### 2. Start with Docker Compose

```powershell
docker compose up --build
```

### 3. Open the app

Frontend:

```text
http://127.0.0.1:8000/frontend/index.html
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### 4. Stop the stack

```powershell
docker compose down
```

If you want to remove persisted Qdrant data too:

```powershell
docker compose down -v
```

### Persisted Data

Docker Compose keeps these folders mounted from your repo:

- `./qdrant_storage` for vector data
- `./generated_proposals` for exported proposal files
- `./backend/sample_docs` for uploaded documents

If Qdrant is not running, knowledge-base ingestion and retrieval will fail.

## Run the App

From the project root:

```powershell
.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

For the local non-Docker setup, Qdrant still needs to be available at `http://localhost:6333` unless you override `QDRANT_URL` in `.env`.

Open the frontend in the browser:

```text
http://127.0.0.1:8000/frontend/index.html
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Workflow

1. Enter a project description.
2. Optionally upload a project document.
3. Optionally upload one or more knowledge-base documents.
4. Click `Generate Proposal`.
5. Download the generated `.docx` file when the button appears.

The frontend includes a loading state during document upload, indexing, and proposal generation.

## API Endpoints

- `POST /upload-project-doc`
  - Uploads a project document and extracts text for the current proposal flow.

- `POST /upload-knowledge-doc`
  - Uploads and indexes a knowledge-base document into Qdrant.

- `POST /generate-proposal`
  - Generates the proposal from description plus extracted project document text.

- `GET /download-proposal/{filename}`
  - Downloads a generated `.docx` proposal.

## Running the Test Scripts

Run modules from the project root so Python resolves the `backend` package correctly:

```powershell
python -m backend.test_exporter
python -m backend.test_ingestion
python -m backend.test_retrieval
python -m backend.test_pipeline
```

Do not run them as direct file paths like `python backend/test_exporter.py` if you rely on package imports.

## Output Files

Generated proposal files are written to:

```text
generated_proposals/
```

Uploaded documents are stored in:

```text
backend/sample_docs/
```

## Notes

- Gemini free-tier quotas can stop the pipeline with `429 RESOURCE_EXHAUSTED` if too many requests are made.
- Knowledge-base retrieval is only useful after documents have been indexed successfully.
- The frontend is served by FastAPI. There is no separate frontend dev server in the current setup.
- In Docker Compose, the backend connects to Qdrant through the internal service URL `http://qdrant:6333`.

## Submission Notes

For the required setup documentation submission, point reviewers to:

- [README.md](README.md) for setup and run steps
- [docker-compose.yml](docker-compose.yml) for the container stack
- [Dockerfile](Dockerfile) for the backend container image