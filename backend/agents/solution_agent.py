# backend/agents/solution_architecture_agent.py
import logging
from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json
from backend.genai_client import create_genai_client

logger = logging.getLogger(__name__)
client = create_genai_client()

PROMPT_TEMPLATE = """
You are a solution architect designing a system for the described project.

Using the project requirements and retrieved knowledge, design a system architecture.

Define:

- frontend
- backend
- ai_services
- data_storage
- integration_services
- technology_stack

Return JSON only.

Project Requirements:
{requirements}

Retrieved Knowledge:
{retrieved_context}
"""


class SolutionArchitectureAgent:
    def run(self, project_state: ProjectState, retrieved_context: dict):
        state = project_state.get()
        requirements = state["requirements"]
        logger.info("SolutionArchitectAgent -> designing architecture")
        prompt = PROMPT_TEMPLATE.format(requirements=requirements, retrieved_context=retrieved_context)
        result = generate_json(client, prompt)
        architecture = result.get("architecture", {})
        tech_stack = result.get("technology_stack", [])
        project_state.update({"architecture": architecture, "technology_stack": tech_stack})
        logger.info("SolutionArchitectAgent -> done (tech_stack=%d items)", len(tech_stack))
        return result
