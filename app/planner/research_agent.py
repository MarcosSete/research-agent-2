from deepagents import create_deep_agent
from app.skills.tools import (
    search_and_save_papers,
    generate_pending_embeddings,
    get_top_ranked_papers,
)
from app.config.research_profile_loader import load_research_profile

SYSTEM_PROMPT = """Você é um assistente de pesquisa científica. Seu trabalho, nesta ordem:
1. Buscar papers novos sobre os temas pedidos, em pelo menos duas fontes diferentes
   (arxiv e semantic_scholar), usando a tool search_and_save_papers para cada tema/fonte.
2. Gerar embeddings pendentes com generate_pending_embeddings.
3. Retornar o ranking final com get_top_ranked_papers.

Não pule etapas. Não invente papers - use somente o que as tools retornarem."""


def build_research_agent():
    return create_deep_agent(
        model="deepseek:deepseek-chat",
        tools=[search_and_save_papers, generate_pending_embeddings, get_top_ranked_papers],
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
                f"Busque papers novos sobre estes temas: {topics_text}. "
                f"Use arxiv e semantic_scholar. Depois gere os embeddings pendentes "
                f"e me traga o top 10 ranqueado."
            ),
        }]
    })

    final_message = result["messages"][-1].content
    print(final_message)
    return final_message


if __name__ == "__main__":
    run_research_pipeline()