from deepagents import create_deep_agent
from app.skills.tools import (
    search_and_save_papers,
    generate_pending_embeddings,
    get_top_ranked_papers,
    save_final_research_report,
)
from app.synthesis.research_synthesizer import synthesize_ranked_papers
from app.config.research_profile_loader import load_research_profile
from app.llm.factory import get_fast_llm


SYSTEM_PROMPT = """You are a scientific research assistant. Follow this workflow in order:
1. Search for new papers on the requested topics using two discovery sources:
   arxiv and huggingface, calling search_and_save_papers for each topic/source pair.
2. Generate pending embeddings with generate_pending_embeddings.
3. Return the final ranking with get_top_ranked_papers.
4. Synthesize the ranking with synthesize_ranked_papers.

Semantic Scholar is available as an auxiliary source, but it is not required for discovery.
Do not use Semantic Scholar automatically when arxiv and huggingface have already been queried.

Do not skip steps. Do not invent papers; use only papers returned by the tools.
The synthesis must be based exclusively on the data returned by the ranking tool."""
 
 
def build_research_agent():
    llm = get_fast_llm(temperature=0.0)

    return create_deep_agent(
        model=llm,
        tools=[
            search_and_save_papers,
            generate_pending_embeddings,
            get_top_ranked_papers,
            synthesize_ranked_papers,
            save_final_research_report,
        ],
        system_prompt=SYSTEM_PROMPT,
    )


def run_research_pipeline(topics: list[str] | None = None) -> str:
    profile = load_research_profile()
    topics = topics or profile.interests

    agent = build_research_agent()
    topics_text = ", ".join(topics)

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                f"Search for new papers on these topics: {topics_text}. "
                f"Use arxiv and huggingface as discovery sources. "
                f"Then generate pending embeddings, return the top 10 ranked papers, "
                f"and produce a technical synthesis of those papers. "
                f"Finally, save the final synthesis as a report."
            ),
        }]
    })

    final_message = result["messages"][-1].content
    print(final_message)
    return final_message


if __name__ == "__main__":
    run_research_pipeline()
