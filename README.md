# 📄 Copie e cole este conteúdo no seu `README.md`


# 🧠 Research Intelligence System

> **An autonomous, agentic pipeline for discovering, enriching, and ranking cutting-edge machine learning papers.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white) 
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red?logo=qdrant&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-purple?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎥 Demonstration

> *[📽️ **Watch the full system walkthrough and agent execution here**]*
> *(Insert your YouTube/Vimeo video link or embed code here. A 2-3 minute video showing the scheduler triggering, the LLM enriching topics, and the final ranked report being generated is highly recommended.)*

---

## 📖 Overview

Keeping up with the exponential growth of ML research is impossible. Hundreds of papers are published weekly on Arxiv, Semantic Scholar, and OpenReview. Most researchers rely on basic keyword searches or social media threads, missing critical cross-domain connections.

The **Research Intelligence System** is not just a scraper. It is a **Research Orchestrator**. It combines deterministic data pipelines with probabilistic Large Language Models to:
1. **Collect** papers from multiple sources without duplication.
2. **Enrich** topics dynamically using LLMs (expanding "RL" to "PPO, DreamerV3, Reward Shaping...").
3. **Embed** and store papers in a local, open-source vector database.
4. **Rank** papers using a hybrid scoring system (Semantic Similarity + Novelty + Author Prestige).
5. **Orchestrate** the entire workflow via an autonomous agent powered by DeepSeek.

---

## 🏗️ Architecture

*(Architecture diagram generated below. For an editable version, see the Excalidraw instructions at the bottom of this file.)*

![Architecture Diagram](./docs/images/architecture.png)

The system is divided into four distinct layers, ensuring separation of concerns and making it easy to swap out components:

1. **Ingestion Layer**: Connectors for Arxiv and Semantic Scholar. Normalizes data into a unified `Paper` Pydantic model.
2. **Processing Layer**: 
   - *LLM Enrichment*: Uses DeepSeek to dynamically expand research topics into rich taxonomies, cached locally to save API costs.
   - *Embedding Service*: Uses `SentenceTransformers` (local, offline, open-source) to generate dense vector representations of abstracts.
3. **Storage Layer**:
   - *PostgreSQL*: Relational storage for paper metadata, authors, and reading history.
   - *Qdrant*: High-performance vector database for semantic search and similarity checks.
4. **Agentic Layer**: The `DeepAgents` core acts as the brain, deciding when to search, when to generate embeddings, and how to synthesize the final weekly report.

---

## 🧬 Core Philosophy

- **Local-First & Privacy**: Embeddings are generated locally using HuggingFace `SentenceTransformers`. No paper abstracts are sent to external APIs for vectorization.
- **Zero Vendor Lock-in**: Uses standard SQL (PostgreSQL) and open-source Vector DBs (Qdrant). The LLM provider (DeepSeek) is abstracted behind LangChain, meaning you can switch to Anthropic or OpenAI by changing a single `.env` variable.
- **Deterministic + Probabilistic**: Data collection and storage are deterministic (Python/SQL). Ranking and synthesis are probabilistic (LLM/Embeddings). This hybrid approach ensures reliability while maintaining "intelligence".

---

## 🛠️ Tech Stack

| Category | Technology | Why we use it |
| :--- | :--- | :--- |
| **Orchestration** | `DeepAgents` / `LangChain` | Native support for tool-calling, memory, and multi-step planning. |
| **LLM Provider** | `DeepSeek` (via `langchain-deepseek`) | Best-in-class reasoning capabilities at a fraction of the cost of GPT-4. |
| **Vector DB** | `Qdrant` | Rust-based, blazing fast, and fully self-hostable via Docker. |
| **Relational DB** | `PostgreSQL` + `SQLAlchemy` | The gold standard for relational data. `Alembic` handles schema migrations. |
| **Embeddings** | `SentenceTransformers` | Open-source, runs locally on CPU/GPU, no API keys required. |
| **Validation** | `Pydantic V2` | Strict data validation from API ingestion to database storage. |
| **Scheduling** | `APScheduler` | Robust cron-like scheduling for weekly research jobs. |

---

## 🎨 Design Patterns

This project is built as a reference implementation for modern ML Engineering practices:

- **Repository Pattern**: `PaperRepository` abstracts all database operations. The business logic never writes raw SQL.
- **Factory Pattern**: `app/llm/factory.py` centralizes LLM instantiation, allowing easy swapping between "Fast" (routing) and "Smart" (reasoning) models.
- **Strategy Pattern**: `BaseCollector` and `BaseEmbeddingService` define interfaces. Adding a new source (e.g., `HuggingFaceCollector`) requires zero changes to the core pipeline.
- **CQRS (Command Query Responsibility Segregation)**: The ingestion pipeline (Commands) is decoupled from the ranking/reporting pipeline (Queries).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for PostgreSQL and Qdrant)
- A DeepSeek API Key (Get one at [platform.deepseek.com](https://platform.deepseek.com))

### 1. Clone and Setup Environment
```bash
git clone https://github.com/MarcosSete/research-agent-2.git
cd research-agent-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
`

### 2. Infrastructure (Docker)
Start the database and vector store:
```bash
docker-compose up -d
```

### 3. Configuration
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
*Edit `.env` and add your `DEEPSEEK_API_KEY`.*

### 4. Database Migrations
Apply the SQLAlchemy schemas to PostgreSQL:
```bash
alembic upgrade head
```

### 5. Run the Agent
Execute the research pipeline manually to test the connection:
```bash
python -m app.agent.research_agent
```

### 6. Start the Scheduler
Leave the cron job running to automatically collect papers every Sunday at 08:00:
```bash
python scripts/run_scheduler.py
```

---

## 🤝 Contributing

This project is designed to be a collaborative effort. If you want to contribute, here is the best way to start:

### Where to begin?
1. **Good First Issue**: Add a new Collector! Implement `app/collectors/huggingface_collector.py` following the `BaseCollector` interface.
2. **Improve Ranking**: Tweak the weights in `app/ranking/scorer.py` or add a new metric (e.g., "Code Availability Score").
3. **UI/Dashboard**: Currently, the output is CLI/Markdown based. Building a simple FastAPI + Streamlit dashboard to visualize the `papers` table would be an amazing contribution.

### Project Structure
```text
research-agent-2/
├── app/
│   ├── agent/          # DeepAgents tools and orchestration
│   ├── collectors/     # API integrations (Arxiv, Semantic Scholar)
│   ├── config/         # Pydantic settings and profile loader
│   ├── database/       # SQLAlchemy models and repositories
│   ├── embeddings/     # Vectorization and Qdrant integration
│   ├── llm/            # LLM factories and topic enrichment
│   └── ranking/        # Scoring algorithms
├── scripts/            # Cron jobs and utility scripts
├── migrations/         # Alembic DB migrations
└── config/             # YAML profiles (research_profile.yaml)
```

---

## 🛣️ Roadmap

- [ ] **Multi-Agent Swarm**: Split the monolithic agent into specialized sub-agents (e.g., "RL Agent", "NLP Agent").
- [ ] **RAG Integration**: Allow the agent to "read" the full PDF of top-ranked papers using PyMuPDF and summarize the methodology.
- [ ] **Notion/Obsidian Sync**: Automatically push the weekly digest to your personal knowledge base.
- [ ] **Web UI**: A lightweight dashboard to browse, filter, and mark papers as "Read".

---

## 📄 License

This project is open-source under the MIT License. Built with ❤️ by the ML Engineering community.
