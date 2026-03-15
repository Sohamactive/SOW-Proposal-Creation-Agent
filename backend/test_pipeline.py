from backend.orchestrator.pipeline import ProposalPipeline


pipeline = ProposalPipeline()

client_input = """
A company wants to build an AI-powered helpdesk platform that classifies
support tickets and retrieves answers from a knowledge base.
"""

result = pipeline.run(client_input)

print("\nProposal:")
print(result["proposal"])

print("\nReview:")
print(result["review"])