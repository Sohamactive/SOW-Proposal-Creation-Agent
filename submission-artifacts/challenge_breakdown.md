# Example Challenge Breakdown

## Overview

This document provides a sample Topcoder-style challenge breakdown for the AI SOW / Proposal Creation Agent.

Goal: deliver a working system that can ingest project inputs, retrieve historical knowledge, generate a structured proposal, review it, and export it as DOCX/PDF/PPTX.

## Assumptions

- Backend uses FastAPI.
- LLM provider is Gemini.
- Vector database is Qdrant.
- Frontend is a lightweight web UI.
- Core pipeline is agent-based and state-driven.

## Delivery Model

A phased challenge model is used to reduce risk and validate each layer before the next phase starts.

## Phase 1: Architecture and Technical Design Challenge

Duration: 3-5 days

Objective:
- Finalize end-to-end architecture, component boundaries, data flow, and interfaces.

Scope:
- System architecture diagram
- Agent orchestration plan
- Project state schema
- RAG ingestion/retrieval design
- API contract draft
- Deployment approach (Docker Compose)

Deliverables:
- Architecture diagram (reviewer-friendly)
- System design document
- API endpoint specification
- Data model and project state schema
- Risk and dependency register

Acceptance Criteria:
- Architecture covers input, RAG, agent pipeline, review loop, and export
- API contracts are clear for frontend-backend integration
- Design supports DOCX export and retrieval-based context injection

## Phase 2: Knowledge Ingestion and RAG Foundation Challenge

Duration: 4-6 days

Objective:
- Implement knowledge base ingestion and retrieval pipeline.

Scope:
- PDF/DOCX parsing
- Document chunking
- Embedding generation
- Qdrant collection setup
- Retrieval with top-k results and metadata support

Deliverables:
- Ingestion module
- Embeddings module
- Vector store module
- Retrieval module
- Sample indexed documents and retrieval test output

Acceptance Criteria:
- Knowledge documents can be uploaded and indexed
- Retrieval returns relevant chunks for domain-specific queries
- Modules run reliably with configured Qdrant endpoint

## Phase 3: Agent Pipeline Implementation Challenge

Duration: 5-7 days

Objective:
- Implement and connect all proposal-generation agents through a shared project state.

Scope:
- Requirement Understanding Agent
- Retrieval Agent
- Solution Architecture Agent
- Delivery Planning Agent
- Risk and Assumption Agent
- Proposal Writer Agent
- Proposal Reviewer Agent

Deliverables:
- Agent implementations and prompts
- Shared project state manager
- Orchestrator pipeline
- JSON-structured outputs for each step

Acceptance Criteria:
- Pipeline executes sequentially with state updates at each stage
- Reviewer output includes status, issues, and suggestions
- Pipeline returns proposal plus review summary

## Phase 4: Proposal Export and API Integration Challenge

Duration: 3-5 days

Objective:
- Expose user-facing APIs and generate downloadable proposal files.

Scope:
- Upload endpoints for project docs and knowledge docs
- Proposal generation endpoint
- DOCX/PDF/PPTX export
- Download endpoint for generated DOCX

Deliverables:
- API routes
- Export service
- Generated sample proposal files
- API usage examples

Acceptance Criteria:
- Endpoints support upload -> process -> generate -> download flow
- DOCX export is successful and readable
- API responses include file download metadata

## Phase 5: Frontend and UX Challenge

Duration: 3-5 days

Objective:
- Build an operator-friendly interface for PM workflow.

Scope:
- Description input
- Project document upload
- Knowledge document upload
- Generate action with loading indicators
- Proposal preview and DOCX download button

Deliverables:
- Frontend HTML/CSS/JS
- Structured proposal preview view
- Error and status messages

Acceptance Criteria:
- User can complete full workflow from browser
- Loading states are shown for long-running operations
- Download link appears after successful generation

## Phase 6: Stabilization, Testing, and Submission Assets Challenge

Duration: 2-4 days

Objective:
- Prepare reliable handoff and submission package.

Scope:
- Error handling improvements
- Setup docs and Docker Compose verification
- Sample proposal output generation
- Demo video capture

Deliverables:
- README with local and Docker setup
- Dockerfile and docker-compose.yml
- Demo video
- Sample generated proposal
- Submission checklist status

Acceptance Criteria:
- Fresh setup works using documented steps
- System can generate at least one proposal end-to-end
- All required submission artifacts are available

## Suggested Timeline Summary

- Phase 1: Week 1
- Phase 2: Week 1-2
- Phase 3: Week 2-3
- Phase 4: Week 3
- Phase 5: Week 4
- Phase 6: Week 4

Total suggested duration: 3-4 weeks

## Roles

- Solution Architect
- Backend Engineer
- AI Engineer
- Frontend Engineer
- QA Engineer
- Project Manager

## Risks and Mitigations

- LLM response format instability
  - Mitigation: enforce JSON response config and robust parsing

- API quota/rate-limit interruptions
  - Mitigation: retries, graceful error handling, fallback messaging

- Retrieval relevance variability
  - Mitigation: improve metadata tagging and query strategy

- Integration delays between phases
  - Mitigation: lock API contracts in Phase 1 and validate in Phase 4

## Definition of Done

The challenge plan is considered complete when:

- all core phases are implemented and integrated
- proposal generation works from UI and API
- DOCX export is downloadable
- setup documentation is reproducible
- submission artifacts are packaged and verified
