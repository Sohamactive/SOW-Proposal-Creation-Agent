from backend.export.proposal_exporter import ProposalExporter
from backend.orchestrator.pipeline import ProposalPipeline

pipeline = ProposalPipeline()

client_input = """
Build an AI helpdesk system that classifies support tickets
and retrieves answers from a knowledge base.
"""

result = pipeline.run(client_input)

exporter = ProposalExporter()

docx = exporter.export_docx(result["proposal"])
pdf = exporter.export_pdf(result["proposal"])
ppt = exporter.export_pptx(result["proposal"])

print(docx)
print(pdf)
print(ppt)