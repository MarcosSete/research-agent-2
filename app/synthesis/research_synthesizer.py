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


def synthesize_ranked_papers(ranked_papers: str) -> str:
    """Gera uma síntese técnica a partir do resultado textual do ranking."""
    if not ranked_papers.strip():
        return "Nenhum paper disponível para síntese."

    profile = load_research_profile()
    llm = get_smart_llm(temperature=0.2)

    prompt = f"""{SYSTEM_PROMPT}

Perfil de leitura: {profile.reading_level}
Estilo de resumo: {profile.summary_style}

Papers selecionados pelo ranking:

{ranked_papers}

Produza uma síntese técnica dos papers selecionados. Para cada paper, apresente:
1. Problema abordado
2. Ideia ou método principal
3. Principal contribuição
4. Limitações, quando identificáveis no conteúdo fornecido

Depois, apresente uma seção curta de comparação entre os trabalhos e outra com
os principais pontos que merecem leitura aprofundada.
"""

    response = llm.invoke(prompt)
    return response.content
