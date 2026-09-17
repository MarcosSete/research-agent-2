# app/llm/topic_enrichment.py
import json
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage
from app.llm.factory import get_smart_llm

CACHE_PATH = Path(__file__).resolve().parents[2] / "config" / "topic_enrichment_cache.json"

ENRICHMENT_SYSTEM_PROMPT = """Você é um especialista em taxonomia de pesquisa científica.
Dado um tópico de pesquisa, gere de 8 a 12 termos e frases fortemente relacionados
que costumam aparecer em títulos e abstracts de papers sobre esse tema: sinônimos,
subtemas, técnicas específicas, benchmarks conhecidos e jargão técnico.
Responda APENAS com os termos separados por vírgula, sem numeração e sem texto extra."""


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with CACHE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_or_enrich_topic(topic: str) -> str:
    """Retorna 'tópico + termos correlatos gerados por LLM'. Cacheado em disco -
    só chama a API na primeira vez que um tópico aparece."""
    cache = _load_cache()
    key = topic.lower()

    if key in cache:
        return cache[key]

    try:
        llm = get_smart_llm(temperature=0.3)
        messages = [
            SystemMessage(content=ENRICHMENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Tópico: {topic}"),
        ]
        response = llm.invoke(messages)
        expanded = f"{topic}, {response.content.strip()}"
    except Exception as e:
        # Se a API falhar (rede, chave inválida, etc.), não derruba o pipeline -
        # usa o tópico puro e segue, mas avisa no console.
        print(f"[WARN] Falha ao enriquecer '{topic}' via LLM ({e}). Usando tópico sem expansão.")
        expanded = topic

    cache[key] = expanded
    _save_cache(cache)
    return expanded