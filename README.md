# 🧠 Research Intelligence System

> **An autonomous, agentic pipeline for discovering, enriching, ranking, and synthesizing machine learning research papers.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white) 
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red?logo=qdrant&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-purple?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎥 Demonstration

> *[📽️ **Watch the full system walkthrough and agent execution here**]*

---

## 📖 Overview

Keeping up with the exponential growth of ML research is impossible. Hundreds of papers are published continuously across research platforms and repositories. Most researchers rely on basic keyword searches or social media threads, missing critical cross-domain connections.

The **Research Intelligence System** is a **single-agent research pipeline** that combines deterministic data processing with probabilistic models to automate the research workflow:
1. **Discover** papers from multiple sources.
2. **Normalize and persist** paper metadata.
3. **Enrich** research topics using an LLM.
4. **Generate** local embeddings for semantic retrieval.
5. **Rank** papers according to the research profile.
6. **Synthesize** selected papers into a technical research summary.

The current implementation uses a **single DeepAgents agent with specialized tools**, rather than a multi-agent architecture.

---

## 🏗️ Architecture

*(Architecture diagram generated below. For an editable version, see the Excalidraw instructions at the bottom of this file.)*

![Captura de tela 2026-09-17 152425.png](docs/images/Captura%20de%20tela%202026-09-17%20152425.png)
The system is divided into four distinct layers, ensuring separation of concerns and making it easy to swap out components:

1. **Discovery Layer**: Collectors for Arxiv, Semantic Scholar, and Hugging Face Papers normalize data into a unified `Paper` Pydantic model.
2. **Processing Layer**: 
   - *LLM Enrichment*: Uses DeepSeek to dynamically expand research topics into related concepts.
   - *Ignored-topic filtering*: Enriched ignored topics are represented as independent semantic terms for similarity checks.
   - *Embedding Service*: Uses `SentenceTransformers` (local, offline, open-source) to generate dense vector representations of abstracts.
3. **Storage Layer**:
   - *PostgreSQL*: Relational storage for paper and author metadata.
   - *Qdrant*: High-performance vector database for semantic search and similarity checks.
4. **Agentic Layer**: A single `DeepAgents` agent coordinates search, embedding generation, ranking, and technical synthesis through specialized tools.

---

## 🧬 Core Philosophy

- **Local-First & Privacy**: Embeddings are generated locally using HuggingFace `SentenceTransformers`. No paper abstracts are sent to external APIs for vectorization.
- **Low Coupling**: Uses standard SQL (PostgreSQL) and an open-source vector database (Qdrant). LLM access is centralized in `app/llm/factory.py`.
- **Deterministic + Probabilistic**: Collection, normalization, persistence, retrieval, and ranking rules are deterministic. Topic enrichment and research synthesis use probabilistic LLMs.

---

## 🛠️ Tech Stack

| Category | Technology | Why we use it |
| :--- | :--- | :--- |
| **Orchestration** | `DeepAgents` / `LangChain` | Tool calling and multi-step agent orchestration. |
| **LLM Provider** | `DeepSeek` (via `langchain-deepseek`) | Fast and reasoning models for enrichment and synthesis. |
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
```

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
python -m app.planner.research_agent
```

### 6. Start the Scheduler
Leave the cron job running to automatically collect papers every Sunday at 08:00:
```bash
python -m app.scheduler.run_scheduler
```

---

## ⚙️ Personalizando seu perfil de pesquisa

As preferências de pesquisa de cada usuário ficam no arquivo:

`config/research_profile.yaml`

**Este é o principal arquivo que você deve editar para personalizar o comportamento do sistema.** Você não precisa alterar o código do agente para definir seus interesses.

### Exemplo

```yaml
interests:
  - Deep Learning
  - Reinforcement Learning
  - Probabilistic Machine Learning
  - Deep Generative Modeling
  - Graph Neural Network
  - Causal Machine Learning

priority:
  Deep Learning: 100
  Reinforcement Learning: 80
  Probabilistic Machine Learning: 70
  Deep Generative Modeling: 60
  Graph Neural Network: 50
  Causal Machine Learning: 40

ignored:
  - Healthcare
  - Biology

favorite_authors:
  - Richard Sutton
  - Yoshua Bengio
  - Yann LeCun

favorite_conferences:
  - NeurIPS
  - ICML
  - ICLR

reading_level: advanced
max_daily_papers: 20
summary_style: technical
```

### O que significa cada seção?

| Campo | Descrição |
| :--- | :--- |
| `interests` | Temas que você deseja pesquisar. Eles são usados como base para a busca e para o perfil semântico de interesse. |
| `priority` | Peso relativo de cada interesse no ranking. Valores maiores fazem aquele interesse ter maior influência no perfil semântico. |
| `ignored` | Temas ou domínios que você deseja evitar nos resultados. |
| `favorite_authors` | Autores que você considera relevantes para sua pesquisa. |
| `favorite_conferences` | Conferências que você considera relevantes para sua pesquisa. |
| `reading_level` | Nível técnico esperado para a síntese dos papers, como `beginner`, `intermediate` ou `advanced`. |
| `max_daily_papers` | Limite configurado de papers considerados por execução/período do perfil. |
| `summary_style` | Estilo desejado para a síntese, por exemplo `technical`. |

### 🔑 Entendendo `priority`

A seção `priority` **não representa porcentagens nem pontos adicionados diretamente a cada paper**. Ela define a importância relativa dos seus interesses dentro do perfil usado pelo ranking.

Por exemplo:

```yaml
priority:
  Deep Learning: 100
  Reinforcement Learning: 80
  Graph Neural Network: 50
```

Isso significa:

- **Deep Learning** → maior influência;
- **Reinforcement Learning** → influência intermediária;
- **Graph Neural Network** → menor influência entre os três.

Os valores são relativos. Você pode usar, por exemplo, `100 / 80 / 50`, `10 / 8 / 5` ou outros valores proporcionais.

**Importante:** os interesses usados em `priority` devem corresponder aos interesses definidos em `interests`.

### 🛠️ Como personalizar

1. Abra `config/research_profile.yaml`.
2. Altere as seções de acordo com seus interesses.
3. Salve o arquivo.
4. Execute o agente novamente:

```bash
python -m app.planner.research_agent
```

O pipeline utilizará o perfil atualizado na próxima execução.

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
│   ├── collectors/     # Arxiv, Semantic Scholar, Hugging Face
│   ├── config/         # Application settings and research profile loader
│   ├── database/       # SQLAlchemy models, repository, session
│   ├── embeddings/     # Local embeddings and Qdrant integration
│   ├── llm/            # LLM factory and topic enrichment
│   ├── models/         # Domain models
│   ├── planner/        # Single-agent research orchestration
│   ├── ranking/        # Paper scoring
│   ├── skills/         # Agent tools
│   └── synthesis/      # Technical research synthesis
├── scripts/            # Local execution and utility scripts
├── migrations/         # Alembic DB migrations
└── config/             # YAML profiles (research_profile.yaml)
```

---


## 📄 License

This project is open-source under the MIT License. Built with ❤️ by the ML Engineering community.
