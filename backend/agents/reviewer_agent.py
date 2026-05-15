# backend/agents/reviewer_agent.py
import json
import logging
from backend.config import settings
from backend.agents.llm_utils import generate_json
from backend.genai_client import create_genai_client

logger = logging.getLogger(__name__)
client = create_genai_client()

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
        logger.info("ReviewerAgent -> reviewing proposal (sections=%d)", len(proposal))
        prompt = PROMPT_TEMPLATE.format(proposal=json.dumps(proposal, indent=2))
        review = generate_json(client, prompt)
        logger.info("ReviewerAgent -> done (status=%s, issues=%d)", review.get("status", "?"), len(review.get("issues", [])))
        return review
