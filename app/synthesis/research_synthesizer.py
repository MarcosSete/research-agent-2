from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.config.research_profile_loader import load_research_profile
from app.llm.factory import get_smart_llm


SYSTEM_PROMPT = """Você é um pesquisador de Machine Learning.
Sua tarefa é sintetizar papers científicos selecionados por um pipeline de pesquisa.

Regras:
- Baseie-se exclusivamente nos papers fornecidos.
- Não invente resultados, métodos, métricas ou conclusões.
- Considere o nível de leitura e o estilo de resumo do perfil.
- Explique os trabalhos de forma técnica e objetiva.
- Compare os papers quando houver diferenças relevantes.
- Destaque ideias, contribuições, limitações e possíveis relações entre os trabalhos.
"""


class PaperSynthesis(BaseModel):
    title: str
    problem: str
    method: str
    contribution: str
    limitations: str
    why_read: str


class ResearchSynthesis(BaseModel):
    overview: str
    papers: list[PaperSynthesis] = Field(default_factory=list)
    comparison: str
    deep_dive_points: list[str] = Field(default_factory=list)


def _fallback_synthesis(ranked_papers: str) -> ResearchSynthesis:
    """Mantém uma saída válida mesmo quando o modelo não retorna estrutura válida."""
    return ResearchSynthesis(
        overview="Síntese estruturada indisponível; consulte os papers selecionados.",
        papers=[],
        comparison="Não foi possível gerar a comparação estruturada.",
        deep_dive_points=[],
    )


def synthesize_ranked_papers(ranked_papers: str) -> str:
    """Gera uma síntese técnica estruturada e a renderiza em Markdown."""
    if not ranked_papers.strip():
        return "Nenhum paper disponível para síntese."

    profile = load_research_profile()
    llm = get_smart_llm(temperature=0.2)

    prompt = f"""{SYSTEM_PROMPT}

Perfil de leitura: {profile.reading_level}
Estilo de resumo: {profile.summary_style}

Papers selecionados pelo ranking:

{ranked_papers}

Retorne uma síntese estruturada.
Para cada paper, preencha:
- title
- problem
- method
- contribution
- limitations
- why_read

Depois preencha:
- overview
- comparison
- deep_dive_points

Use somente informações presentes nos papers fornecidos.
"""

    structured_llm = llm.with_structured_output(ResearchSynthesis)
    result = structured_llm.invoke(prompt)

    return render_research_synthesis(result)


def render_research_synthesis(synthesis: ResearchSynthesis) -> str:
    lines = [
        "# Research Report",
        "",
        "## Visão geral",
        "",
        synthesis.overview,
        "",
        "## Papers recomendados",
        "",
    ]

    for position, paper in enumerate(synthesis.papers, start=1):
        lines.extend([
            f"### {position}. {paper.title}",
            "",
            "#### 🎯 Problema",
            "",
            paper.problem,
            "",
            "#### 🧠 Método",
            "",
            paper.method,
            "",
            "#### 💡 Contribuição",
            "",
            paper.contribution,
            "",
            "#### ⚠️ Limitações",
            "",
            paper.limitations,
            "",
            "#### 📖 Por que ler",
            "",
            paper.why_read,
            "",
        ])

    lines.extend([
        "## Comparação",
        "",
        synthesis.comparison,
        "",
        "## Pontos para aprofundamento",
        "",
    ])

    for point in synthesis.deep_dive_points:
        lines.append(f"- {point}")

    return "\n".join(lines)
