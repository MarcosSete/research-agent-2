import json
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage
from app.llm.factory import get_smart_llm

CACHE_PATH = Path(__file__).resolve().parents[2] / "config" / "topic_enrichment_cache.json"

ENRICHMENT_SYSTEM_PROMPT = """You are a scientific research taxonomy specialist.
Given a research topic, generate 8 to 12 strongly related terms and phrases that
commonly appear in paper titles and abstracts for that topic: synonyms,
subtopics, specific techniques, known benchmarks, and technical jargon.
Respond ONLY with comma-separated terms, without numbering or additional text."""


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
    """Return the topic plus LLM-generated related terms. Cached on disk."""
    cache = _load_cache()
    key = topic.lower()

    if key in cache:
        return cache[key]

    try:
        llm = get_smart_llm(temperature=0.3)
        messages = [
            SystemMessage(content=ENRICHMENT_SYSTEM_PROMPT),
            HumanMessage(content=f"Topic: {topic}"),
        ]
        response = llm.invoke(messages)
        expanded = f"{topic}, {response.content.strip()}"
    except Exception as e:
        print(
            f"[WARN] Failed to enrich '{topic}' via LLM ({e}). "
            "Using the original topic without expansion."
        )
        expanded = topic

    cache[key] = expanded
    _save_cache(cache)
    return expanded
