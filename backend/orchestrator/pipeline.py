import logging
from backend.agents.project_state import ProjectState
from backend.agents.requirement_agent import RequirementUnderstandingAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.solution_agent import SolutionArchitectureAgent
from backend.agents.delivery_agent import DeliveryPlanningAgent
from backend.agents.risk_agent import RiskAssumptionAgent
from backend.agents.proposal_agent import ProposalWriterAgent
from backend.agents.reviewer_agent import ProposalReviewerAgent
from typing import Callable

logger = logging.getLogger(__name__)


class ProposalPipeline:
    def __init__(self):
        self.req = RequirementUnderstandingAgent()
        self.retr = RetrievalAgent()
        self.sol = SolutionArchitectureAgent()
        self.deliv = DeliveryPlanningAgent()
        self.risk = RiskAssumptionAgent()
        self.writer = ProposalWriterAgent()
        self.reviewer = ProposalReviewerAgent()

    def run(self, client_input: str, project_docs_text: str = "", progress_callback: Callable[[int, str], None] | None = None):
        logger.info("=========== Pipeline START -- input=%d, docs=%d ===========", len(client_input), len(project_docs_text))
        state = ProjectState()
        full_input = client_input + "\n\n" + project_docs_text

        def notify(step_index: int, step_label: str) -> None:
            logger.info("Pipeline step %d/4: %s", step_index, step_label)
            if progress_callback:
                progress_callback(step_index, step_label)

        try:
            notify(0, "Reading documents")
            self.req.run(state, full_input)
            notify(1, "Analyzing requirements")
            context = self.retr.run(state)
            notify(2, "Generating proposal")
            self.sol.run(state, context)
            self.deliv.run(state)
            self.risk.run(state)
            proposal = self.writer.run(state)
            notify(3, "Quality review")
            review = self.reviewer.run(proposal)
            notify(4, "Done")
            logger.info("=========== Pipeline COMPLETE -- sections=%d ===========", len(proposal))
            return {"proposal": proposal, "review": review}
        except Exception:
            logger.exception("Pipeline FAILED -- unhandled exception")
            raise
