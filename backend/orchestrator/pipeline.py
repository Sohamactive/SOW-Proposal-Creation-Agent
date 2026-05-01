from backend.agents.project_state import ProjectState
from backend.agents.requirement_agent import RequirementUnderstandingAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.solution_agent import SolutionArchitectureAgent
from backend.agents.delivery_agent import DeliveryPlanningAgent
from backend.agents.risk_agent import RiskAssumptionAgent
from backend.agents.proposal_agent import ProposalWriterAgent
from backend.agents.reviewer_agent import ProposalReviewerAgent
from typing import Callable


class ProposalPipeline:

    def __init__(self):

        self.req = RequirementUnderstandingAgent()
        self.retr = RetrievalAgent()
        self.sol = SolutionArchitectureAgent()
        self.deliv = DeliveryPlanningAgent()
        self.risk = RiskAssumptionAgent()
        self.writer = ProposalWriterAgent()
        self.reviewer = ProposalReviewerAgent()

    def run(
        self,
        client_input: str,
        project_docs_text: str = "",
        progress_callback: Callable[[int, str], None] | None = None
    ):

        state = ProjectState()

        # Combine project inputs
        full_input = client_input + "\n\n" + project_docs_text

        def notify(step_index: int, step_label: str) -> None:
            if progress_callback:
                progress_callback(step_index, step_label)

        # Requirement analysis
        notify(0, "Reading documents")
        self.req.run(state, full_input)

        # Knowledge retrieval
        notify(1, "Analyzing requirements")
        context = self.retr.run(state)

        # Solution architecture
        notify(2, "Generating proposal")
        self.sol.run(state, context)

        # Delivery planning
        self.deliv.run(state)

        # Risks
        self.risk.run(state)

        # Proposal writing
        proposal = self.writer.run(state)

        # Review
        notify(3, "Quality review")
        review = self.reviewer.run(proposal)
        notify(4, "Done")

        return {
            "proposal": proposal,
            "review": review
        }
