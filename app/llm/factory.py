from langchain_deepseek import ChatDeepSeek

from app.config.settings import settings


def get_fast_llm(temperature: float = 0.0) -> ChatDeepSeek:
    """Modelo rápido e barato para decisões simples e de alto volume."""
    return ChatDeepSeek(
        model=settings.deepseek_model_fast,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=temperature,
    )


def get_smart_llm(temperature: float = 0.3) -> ChatDeepSeek:
    """Modelo para tarefas complexas, como síntese e planejamento."""
    return ChatDeepSeek(
        model=settings.deepseek_model_smart,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=temperature,
    )
