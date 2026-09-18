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


SYSTEM_PROMPT = """You are a scientific research assistant. Execute the research pipeline completely and then provide a useful execution summary.

Workflow:
1. Search for new papers on the requested topics using two discovery sources:
   arxiv and huggingface, calling search_and_save_papers for each topic/source pair.
2. Generate pending embeddings with generate_pending_embeddings.
3. Return the final ranking with get_top_ranked_papers.
4. Synthesize the ranking with synthesize_ranked_papers.
5. Save the complete bilingual synthesis with save_final_research_report.

Semantic Scholar is available as an auxiliary source, but it is not required for discovery.
Do not use Semantic Scholar automatically when arxiv and huggingface have already been queried.

Do not skip steps. Do not invent papers; use only papers returned by the tools.
The synthesis must be based exclusively on the data returned by the ranking tool.

Final response requirements:
- Do not narrate future actions such as "I will save the report" or "Now let me save...".
- The final response must be written only after the save_final_research_report tool has completed successfully.
- Report what actually happened during the run.
- Include these sections:
  1. Discovery — number of searches, topics/sources, papers found, and new papers saved.
  2. Embeddings — number generated or state that none were pending.
  3. Ranking — list the top 10 papers with their scores.
  4. Technical synthesis — briefly summarize the generated synthesis, including its main cross-paper themes.
  5. Final report — include the Markdown and JSON report paths returned by the save tool.
- Keep the final response concise but informative.
- Do not reproduce the full bilingual report in the final response.
- If a tool returns an error or a step cannot be completed, state that explicitly instead of claiming success."""
 
 
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
