# backend/test_retrieval.py

from backend.rag.retrieval import retrieve_context

query = "AI helpdesk ticket classification system"

context = retrieve_context(query)

print(context[:500])