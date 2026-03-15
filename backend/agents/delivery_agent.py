# backend/agents/delivery_agent.py

from google import genai

from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json


client = genai.Client(api_key=settings.GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are a project delivery planner.

Based on the system architecture and project requirements, define a delivery plan.

Include:

- project timeline
- Topcoder challenge structure
- team roles
- deliverables

Return JSON only.

Architecture:
{architecture}

Requirements:
{requirements}
"""


class DeliveryPlanningAgent:

    def run(self, project_state: ProjectState):

        state = project_state.get()

        architecture = state["architecture"]
        requirements = state["requirements"]

        prompt = PROMPT_TEMPLATE.format(
            architecture=architecture,
            requirements=requirements
        )

        result = generate_json(client, prompt)

        timeline = result.get("timeline", [])
        challenge_plan = result.get("challenge_plan", [])
        team_structure = result.get("team_structure", [])
        deliverables = result.get("deliverables", [])

        project_state.update({
            "delivery_plan": {
                "timeline": timeline,
                "challenge_plan": challenge_plan,
                "team_structure": team_structure
            },
            "deliverables": deliverables
        })

        return result