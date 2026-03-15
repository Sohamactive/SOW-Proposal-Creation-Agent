# backend/agents/reviewer_agent.py

import json
from google import genai

from backend.config import settings
from backend.agents.llm_utils import generate_json


client = genai.Client(api_key=settings.GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are reviewing a project proposal.

Evaluate the proposal for:

- missing sections
- unclear explanations
- inconsistencies
- unrealistic assumptions

Return JSON only.

Required sections:

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

Proposal:
{proposal}
"""


class ProposalReviewerAgent:

    def run(self, proposal: dict):

        prompt = PROMPT_TEMPLATE.format(
            proposal=json.dumps(proposal, indent=2)
        )

        review = generate_json(client, prompt)

        return review