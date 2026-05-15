# backend/agents/proposal_agent.py
import json
import logging
from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json
from backend.genai_client import create_genai_client

logger = logging.getLogger(__name__)
client = create_genai_client()

PROMPT_TEMPLATE = """
You are a professional proposal writer.

Using the provided project information, generate a structured project proposal.

Sections required:

Executive Summary
Project Overview
Scope of Work
Technical Approach
Deliverables
Project Timeline
Team Structure
Assumptions
Risks and Mitigation
Previous Experience
Pricing Estimate
Conclusion

Return JSON only.

Project State:
{project_state}
"""


class ProposalWriterAgent:
    def run(self, project_state: ProjectState):
        state = project_state.get()
        logger.info("ProposalWriterAgent -> composing proposal")
        prompt = PROMPT_TEMPLATE.format(project_state=json.dumps(state, indent=2))
        proposal = generate_json(client, prompt)
        logger.info("ProposalWriterAgent -> done (sections=%d)", len(proposal))
        return proposal
