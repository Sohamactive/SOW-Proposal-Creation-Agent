# backend/agents/proposal_agent.py

import json
from google import genai

from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json


client = genai.Client(api_key=settings.GEMINI_API_KEY)


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

        prompt = PROMPT_TEMPLATE.format(
            project_state=json.dumps(state, indent=2)
        )

        proposal = generate_json(client, prompt)

        return proposal