from backend.agents.project_state import ProjectState
from backend.agents.requirement_agent import RequirementUnderstandingAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.solution_agent import SolutionArchitectureAgent
from backend.agents.delivery_agent import DeliveryPlanningAgent
from backend.agents.risk_agent import RiskAssumptionAgent
from backend.agents.proposal_agent import ProposalWriterAgent
from backend.agents.reviewer_agent import ProposalReviewerAgent


class ProposalPipeline:

    def __init__(self):

        self.req = RequirementUnderstandingAgent()
        self.retr = RetrievalAgent()
        self.sol = SolutionArchitectureAgent()
        self.deliv = DeliveryPlanningAgent()
        self.risk = RiskAssumptionAgent()
        self.writer = ProposalWriterAgent()
        self.reviewer = ProposalReviewerAgent()

    def run(self, client_input: str, project_docs_text: str = ""):

        state = ProjectState()

        # Combine project inputs
        full_input = client_input + "\n\n" + project_docs_text

        # Requirement analysis
        self.req.run(state, full_input)

        # Knowledge retrieval
        context = self.retr.run(state)

        # Solution architecture
        self.sol.run(state, context)

        # Delivery planning
        self.deliv.run(state)

        # Risks
        self.risk.run(state)

        # Proposal writing
        proposal = self.writer.run(state)

        # Review
        review = self.reviewer.run(proposal)

        return {
            "proposal": proposal,
            "review": review
        }