# backend/agents/retrieval_agent.py

from google import genai

from backend.config import settings
from backend.agents.project_state import ProjectState
from backend.agents.llm_utils import generate_json
from backend.rag.retrieval import retrieve_chunks


client = genai.Client(api_key=settings.GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are an AI assistant generating search queries to retrieve relevant project knowledge.

Generate 3–4 search queries that would retrieve useful examples of similar systems,
architectures, and delivery models.

Return JSON.

Project Information:

problem_statement: {problem_statement}

features: {features}

domain: {project_domain}
"""


class RetrievalAgent:

    def run(self, project_state: ProjectState):

        state = project_state.get()

        problem_statement = state["project_info"]["problem_statement"]
        features = state["requirements"]["features"]
        domain = state["project_info"]["project_domain"]

        prompt = PROMPT_TEMPLATE.format(
            problem_statement=problem_statement,
            features=features,
            project_domain=domain
        )

        result = generate_json(client, prompt)

        queries = [query for query in result.get("queries", []) if isinstance(query, str) and query.strip()]

        retrieved_context = []

        for q in queries:
            chunks = retrieve_chunks(q)
            retrieved_context.extend(chunks)

        # Simplified grouping (can be improved later)
        similar_projects = []
        architecture_patterns = []
        challenge_examples = []

        for c in retrieved_context:

            text = c["text"]

            if "architecture" in text.lower():
                architecture_patterns.append(text)

            elif "challenge" in text.lower():
                challenge_examples.append(text)

            else:
                similar_projects.append(text)

        context = {
            "similar_projects": similar_projects[:3],
            "architecture_patterns": architecture_patterns[:3],
            "challenge_examples": challenge_examples[:3]
        }

        project_state.update({
            "previous_experience": context["similar_projects"]
        })

        return context