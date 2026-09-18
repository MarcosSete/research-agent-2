from langchain_deepseek import ChatDeepSeek

from app.config.settings import settings


def get_fast_llm(temperature: float = 0.0) -> ChatDeepSeek:
    """Fast, low-cost model for simple high-volume decisions."""
    return ChatDeepSeek(
        model=settings.deepseek_model_fast,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=temperature,
    )


def get_smart_llm(temperature: float = 0.3) -> ChatDeepSeek:
    """Model for complex tasks such as synthesis and planning."""
    return ChatDeepSeek(
        model=settings.deepseek_model_smart,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=temperature,
    )
