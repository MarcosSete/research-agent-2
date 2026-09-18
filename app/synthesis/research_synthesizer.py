import json

from pydantic import BaseModel, Field

from app.config.research_profile_loader import load_research_profile
from app.llm.factory import get_smart_llm


SYSTEM_PROMPT = """You are a Machine Learning researcher.
Your task is to synthesize scientific papers selected by a research pipeline.

Rules:
- Base the synthesis exclusively on the provided papers.
- Do not invent results, methods, metrics, or conclusions.
- Consider the reading level and summary style from the research profile.
- Explain the papers in a technical and objective way.
- Compare the papers when relevant differences exist.
- Highlight ideas, contributions, limitations, and relationships between the papers.
- Produce both English and Portuguese versions of every synthesis field.
- The English version must be written first and the Portuguese version must faithfully
  preserve the meaning of the English version.
"""


class RankedPaper(BaseModel):
    position: int
    title: str
    score: float
    authors: list[str] = Field(default_factory=list)
    published: str | None = None
    conference: str | None = None
    citations: int = 0
    abstract: str
    source: str


class PaperSynthesis(BaseModel):
    title: str
    problem_en: str
    method_en: str
    contribution_en: str
    limitations_en: str
    why_read_en: str
    problem_pt: str
    method_pt: str
    contribution_pt: str
    limitations_pt: str
    why_read_pt: str


class ResearchSynthesis(BaseModel):
    overview_en: str
    papers: list[PaperSynthesis] = Field(default_factory=list)
    comparison_en: str
    deep_dive_points_en: list[str] = Field(default_factory=list)
    overview_pt: str
    comparison_pt: str
    deep_dive_points_pt: list[str] = Field(default_factory=list)


def synthesize_ranked_papers(ranked_papers: str) -> str:
    """Generate a structured bilingual research synthesis and render it as Markdown."""
    if not ranked_papers.strip():
        return "No papers available for synthesis."

    ranking_data = json.loads(ranked_papers)
    ranked = [RankedPaper.model_validate(item) for item in ranking_data.get("papers", [])]

    if not ranked:
        return "No papers available for synthesis."

    profile = load_research_profile()
    llm = get_smart_llm(temperature=0.2)

    papers_for_llm = [
        {
            "title": paper.title,
            "abstract": paper.abstract,
        }
        for paper in ranked
    ]

    prompt = f"""{SYSTEM_PROMPT}

Reading level: {profile.reading_level}
Summary style: {profile.summary_style}

Papers selected by the ranking:

{json.dumps(papers_for_llm, ensure_ascii=False, indent=2)}

Return ONLY one valid JSON object.

Required format:
{{
  "overview_en": "English overview of the selection",
  "papers": [
    {{
      "title": "exact paper title",
      "problem_en": "problem addressed",
      "method_en": "main method or idea",
      "contribution_en": "main contribution",
      "limitations_en": "limitations identifiable from the provided content",
      "why_read_en": "why this paper is worth reading",
      "problem_pt": "Portuguese translation of problem_en",
      "method_pt": "Portuguese translation of method_en",
      "contribution_pt": "Portuguese translation of contribution_en",
      "limitations_pt": "Portuguese translation of limitations_en",
      "why_read_pt": "Portuguese translation of why_read_en"
    }}
  ],
  "comparison_en": "English comparison of the papers",
  "deep_dive_points_en": [
    "English point for further study"
  ],
  "overview_pt": "Portuguese translation of overview_en",
  "comparison_pt": "Portuguese translation of comparison_en",
  "deep_dive_points_pt": [
    "Portuguese translation of each deep_dive_points_en item"
  ]
}}

Return one item in "papers" for each provided paper.
Use only information present in the provided abstracts.
Do not add fields.
"""
 
    response = llm.invoke(prompt)
    content = response.content

    if not isinstance(content, str) or not content.strip():
        raise ValueError("The LLM returned empty content for the structured synthesis.")

    data = json.loads(content)
    synthesis = ResearchSynthesis.model_validate(data)

    return render_research_synthesis(synthesis, ranked)


def render_research_synthesis(
    synthesis: ResearchSynthesis,
    ranked_papers: list[RankedPaper],
) -> str:
    metadata_by_title = {paper.title: paper for paper in ranked_papers}

    lines = [
        "# Research Report",
        "",
        "[🇧🇷 Jump to the Portuguese version](#português)",
        "",
        "## English",
        "",
        "### Overview",
        "",
        synthesis.overview_en,
        "",
        "### Recommended Papers",
        "",
    ]

    for position, paper in enumerate(synthesis.papers, start=1):
        metadata = metadata_by_title.get(paper.title)

        lines.extend([
            f"#### {position}. {paper.title}",
            "",
        ])

        if metadata:
            lines.extend([
                f"**Score:** {metadata.score:.4f}",
                f"**Authors:** {', '.join(metadata.authors) or 'Not provided'}",
                f"**Published:** {metadata.published or 'Not provided'}",
                f"**Conference:** {metadata.conference or 'Not provided'}",
                f"**Citations:** {metadata.citations}",
                f"**Source:** {metadata.source}",
                "",
            ])

        lines.extend([
            "##### 🎯 Problem",
            "",
            paper.problem_en,
            "",
            "##### 🧠 Method",
            "",
            paper.method_en,
            "",
            "##### 💡 Contribution",
            "",
            paper.contribution_en,
            "",
            "##### ⚠️ Limitations",
            "",
            paper.limitations_en,
            "",
            "##### 📖 Why read",
            "",
            paper.why_read_en,
            "",
        ])

    lines.extend([
        "### Comparison",
        "",
        synthesis.comparison_en,
        "",
        "### Points for Further Study",
        "",
    ])

    for point in synthesis.deep_dive_points_en:
        lines.append(f"- {point}")

    lines.extend([
        "",
        "---",
        "",
        "## Português",
        "",
        "[🇺🇸 Back to the English version](#english)",
        "",
        "### Visão geral",
        "",
        synthesis.overview_pt,
        "",
        "### Papers recomendados",
        "",
    ])

    for position, paper in enumerate(synthesis.papers, start=1):
        metadata = metadata_by_title.get(paper.title)

        lines.extend([
            f"#### {position}. {paper.title}",
            "",
        ])

        if metadata:
            lines.extend([
                f"**Score:** {metadata.score:.4f}",
                f"**Autores:** {', '.join(metadata.authors) or 'Não informado'}",
                f"**Publicado:** {metadata.published or 'Não informado'}",
                f"**Conferência:** {metadata.conference or 'Não informado'}",
                f"**Citações:** {metadata.citations}",
                f"**Fonte:** {metadata.source}",
                "",
            ])

        lines.extend([
            "##### 🎯 Problema",
            "",
            paper.problem_pt,
            "",
            "##### 🧠 Método",
            "",
            paper.method_pt,
            "",
            "##### 💡 Contribuição",
            "",
            paper.contribution_pt,
            "",
            "##### ⚠️ Limitações",
            "",
            paper.limitations_pt,
            "",
            "##### 📖 Por que ler",
            "",
            paper.why_read_pt,
            "",
        ])

    lines.extend([
        "### Comparação",
        "",
        synthesis.comparison_pt,
        "",
        "### Pontos para aprofundamento",
        "",
    ])

    for point in synthesis.deep_dive_points_pt:
        lines.append(f"- {point}")

    return "\n".join(lines)
