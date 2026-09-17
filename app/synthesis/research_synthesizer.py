import json

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

Retorne SOMENTE um objeto JSON válido.

Formato obrigatório:
{{
  "overview": "visão geral da seleção",
  "papers": [
    {{
      "title": "título exato do paper",
      "problem": "problema abordado",
      "method": "método ou ideia principal",
      "contribution": "principal contribuição",
      "limitations": "limitações identificáveis no conteúdo fornecido",
      "why_read": "por que este paper merece leitura"
    }}
  ],
  "comparison": "comparação entre os papers",
  "deep_dive_points": [
    "ponto para aprofundamento"
  ]
}}

Use somente informações presentes nos papers fornecidos.
Não adicione campos.
"""

    response = llm.invoke(prompt)
    content = response.content

    if not isinstance(content, str) or not content.strip():
        raise ValueError("O LLM retornou conteúdo vazio para a síntese estruturada.")

    data = json.loads(content)
    result = ResearchSynthesis.model_validate(data)

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
