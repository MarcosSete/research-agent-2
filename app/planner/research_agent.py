from deepagents import create_deep_agent
import json
from app.skills.tools import (
    search_and_save_papers,
    generate_pending_embeddings,
    get_top_ranked_papers,
)
from app.reports.report_writer import save_research_report
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
5. Return the complete bilingual synthesis. The runtime saves the rendered synthesis after the agent finishes.

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
        ],
        system_prompt=SYSTEM_PROMPT,
    )


def _message_content(message) -> str:
    content = getattr(message, "content", "")
    return content if isinstance(content, str) else str(content or "")


def _extract_synthesis(messages) -> str | None:
    for message in reversed(messages):
        content = _message_content(message)
        if "# Research Report" in content:
            return content
    return None


def _extract_ranking(messages) -> dict | None:
    for message in reversed(messages):
        content = _message_content(message).strip()
        if not content.startswith("{"):
            continue
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and isinstance(data.get("papers"), list):
            return data
    return None


def _build_execution_summary(messages, report_path: str, json_path: str) -> str:
    search_results = []
    embedding_result = None

    for message in messages:
        content = _message_content(message)
        if "new papers saved out of" in content:
            search_results.append(content)
        if "embeddings generated and saved" in content or "No papers pending embedding generation" in content:
            embedding_result = content

    ranking = _extract_ranking(messages)
    synthesis = _extract_synthesis(messages)

    total_found = 0
    total_saved = 0

    for content in search_results:
        parts = content.split(" new papers saved out of ")
        if len(parts) != 2:
            continue
        try:
            saved = int(parts[0])
            found = int(parts[1].split(" found", 1)[0])
        except (ValueError, IndexError):
            continue
        total_saved += saved
        total_found += found

    lines = [
        "Research pipeline completed successfully.",
        "",
        "## 1. Discovery",
        "",
        f"{len(search_results)} searches completed.",
        f"- Papers found: {total_found}",
        f"- New papers saved: {total_saved}",
        "",
        "## 2. Embeddings",
        "",
        embedding_result or "Embedding stage completed; no tool result was returned.",
        "",
        "## 3. Ranking — Top 10",
        "",
    ]

    if ranking and ranking.get("papers"):
        lines.extend([
            "| # | Paper | Score |",
            "|---|---|---:|",
        ])
        for paper in ranking["papers"][:10]:
            lines.append(
                f"| {paper.get('position', '')} | {paper.get('title', '')} | "
                f"{paper.get('score', '')} |"
            )
    else:
        lines.append("Ranking data was not returned.")

    synthesis_lines = []
    if synthesis:
        english_papers = synthesis.count("\n#### ") // 2
        english_points = synthesis.split("### Points for Further Study", 1)
        further_study_count = 0
        if len(english_points) == 2:
            further_study_count = sum(
                1 for line in english_points[1].splitlines() if line.startswith("- ")
            )
        synthesis_lines = [
            "The bilingual technical synthesis was generated successfully.",
            f"- Papers synthesized: {len(ranking.get('papers', [])) if ranking else 0}",
            "- Languages: English and Portuguese",
            "- Sections: overview, paper analyses, comparison, and further study",
        ]
        if further_study_count:
            synthesis_lines.append(f"- Further-study points: {further_study_count}")
    else:
        synthesis_lines = ["The synthesis stage did not return a rendered report."]

    lines.extend([
        "",
        "## 4. Technical synthesis",
        "",
        *synthesis_lines,
        "",
        "## 5. Final report",
        "",
        f"- Markdown: `{report_path}`",
        f"- JSON: `{json_path}`",
    ])

    return "\n".join(lines)


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
                f"and produce a complete bilingual technical synthesis of those papers. "
            ),
        }]
    })

    messages = result.get("messages", [])
    synthesis_report = _extract_synthesis(messages)

    if synthesis_report:
        save_result = save_research_report(synthesis_report)
        markdown_path, json_path = save_result

        final_message = _build_execution_summary(messages, markdown_path, json_path)
    else:
        final_message = (
            "Research pipeline did not produce a final synthesis. "
            "The agent completed without returning a rendered research report."
        )

    print(final_message)
    return final_message


if __name__ == "__main__":
    run_research_pipeline()
