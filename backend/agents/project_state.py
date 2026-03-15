# backend/agents/project_state.py

from typing import Dict, Any


class ProjectState:
    """
    Shared structured state used by all agents.

    Each agent reads from and updates this object.
    """

    def __init__(self):

        self.state: Dict[str, Any] = {

            "project_info": {
                "problem_statement": "",
                "project_domain": "",
                "client_objectives": [],
                "expected_outcomes": []
            },

            "requirements": {
                "features": [],
                "integrations": [],
                "data_sources": [],
                "target_users": []
            },

            "scope": {
                "in_scope": [],
                "out_of_scope": []
            },

            "ai_components": [],

            "architecture": {
                "frontend": "",
                "backend": "",
                "ai_services": [],
                "data_storage": "",
                "integration_services": []
            },

            "technology_stack": [],

            "deliverables": [],

            "delivery_plan": {
                "timeline": [],
                "challenge_plan": [],
                "team_structure": []
            },

            "risks": [],

            "assumptions": [],

            "previous_experience": [],

            "pricing_estimate": {
                "architecture_hours": 0,
                "design_hours": 0,
                "development_hours": 0,
                "testing_hours": 0
            }
        }

    def get(self) -> Dict[str, Any]:
        """
        Return current state.
        """
        return self.state

    def update(self, updates: Dict[str, Any]):
        """
        Update specific fields in the state.
        """

        for key, value in updates.items():

            if key not in self.state:
                continue

            if isinstance(self.state[key], dict) and isinstance(value, dict):
                self.state[key].update(value)

            else:
                self.state[key] = value