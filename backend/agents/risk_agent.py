# backend/agents/risk_agent.py

from google import genai

from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json


client = genai.Client(api_key=settings.GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are analyzing a software project proposal.

Identify realistic project assumptions and risks.
Provide mitigation strategies.

Return JSON only.

Project Information:
{project_state}
"""


class RiskAssumptionAgent:

    def run(self, project_state: ProjectState):

        state = project_state.get()

        prompt = PROMPT_TEMPLATE.format(
            project_state=state
        )

        result = generate_json(client, prompt)

        assumptions = result.get("assumptions", [])
        risks = result.get("risks", [])

        project_state.update({
            "assumptions": assumptions,
            "risks": risks
        })

        return result