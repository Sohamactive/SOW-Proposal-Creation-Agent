# backend/agents/requirement_agent.py
import logging
from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json
from backend.genai_client import create_genai_client

logger = logging.getLogger(__name__)
client = create_genai_client()

PROMPT_TEMPLATE = """
You are an AI assistant helping a project manager understand a client's project request.

Analyze the following project description and extract structured project information.

Extract the following fields:

problem_statement
project_domain
client_objectives
expected_outcomes
features
integrations
target_users
data_sources

Return JSON only.

Project Description:
{client_input}
"""


class RequirementUnderstandingAgent:
    def run(self, project_state: ProjectState, client_input: str, rfp_text: str = "", meeting_notes: str = ""):
        logger.info("RequirementAgent -> starting (input_length=%d)", len(client_input))
        combined_input = client_input
        if rfp_text:
            combined_input += "\n\nRFP:\n" + rfp_text
        if meeting_notes:
            combined_input += "\n\nMeeting Notes:\n" + meeting_notes
        prompt = PROMPT_TEMPLATE.format(client_input=combined_input)
        result = generate_json(client, prompt)
        project_state.update({
            "project_info": {
                "problem_statement": result.get("problem_statement", ""),
                "project_domain": result.get("project_domain", ""),
                "client_objectives": result.get("client_objectives", []),
                "expected_outcomes": result.get("expected_outcomes", [])
            },
            "requirements": {
                "features": result.get("features", []),
                "integrations": result.get("integrations", []),
                "data_sources": result.get("data_sources", []),
                "target_users": result.get("target_users", [])
            }
        })
        logger.info("RequirementAgent -> done (domain=%s, features=%d)", result.get("project_domain", "?"), len(result.get("features", [])))
        return result
