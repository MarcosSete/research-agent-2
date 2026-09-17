import math
from datetime import date
from app.config.research_profile_loader import ResearchProfile
from app.embeddings.base import BaseEmbeddingService
from app.llm.topic_enrichment import get_or_enrich_topic

IGNORED_SIMILARITY_THRESHOLD = 0.30


class PaperScorer:
    def __init__(
        self,
        profile: ResearchProfile,
        embedding_service: BaseEmbeddingService | None = None,
        debug: bool = False,
    ):
        self.profile = profile
        self.embedding_service = embedding_service
        self.debug = debug
        self._ignored_terms: list[str] = []
        self._ignored_vectors: list[list[float]] = (
            self._compute_ignored_vectors() if embedding_service else []
        )
        self._interest_vector: list[float] | None = (
            self._compute_interest_vector() if embedding_service else None
        )

    def _compute_ignored_vectors(self) -> list[list[float]]:
        if not self.profile.ignored:
            return []

        representations: list[str] = []
        labels: list[str] = []

        for topic in self.profile.ignored:
            expanded = get_or_enrich_topic(topic)
            terms = [
                term.strip()
                for term in expanded.split(",")
                if term.strip()
            ]

            # Preserve the original domain and also create contextual
            # representations. A bare label such as "Healthcare" is often
            # too abstract for sentence embeddings to match a concrete paper.
            contextual = (
                f"Research in {topic}, including applications, methods, "
                f"datasets and technical topics related to {', '.join(terms)}."
            )

            representations.extend([topic, contextual, *terms])
            labels.extend([topic, contextual, *terms])

        self._ignored_terms = labels
        return self.embedding_service.embed_batch(representations)

    def _compute_interest_vector(self) -> list[float] | None:
        if not self.profile.interests:
            return None

        expanded_texts = [
            get_or_enrich_topic(topic)
            for topic in self.profile.interests
        ]
        vectors = self.embedding_service.embed_batch(expanded_texts)

        weighted_vector = [0.0] * self.embedding_service.dimension
        total_weight = 0.0

        for topic, vector in zip(self.profile.interests, vectors):
            weight = max(self.profile.priority.get(topic, 1), 0)
            if weight == 0:
                continue

            total_weight += weight
            for index, value in enumerate(vector):
                weighted_vector[index] += value * weight

        if total_weight == 0:
            return None

        return [value / total_weight for value in weighted_vector]

    @property
    def interest_vector(self) -> list[float] | None:
        """Vetor semântico dos interesses, ponderado por prioridade."""
        return self._interest_vector

    def score(
        self,
        title: str,
        abstract: str,
        similarity: float,
        conference: str | None,
        author_names: list[str],
        published_date: date | None,
        citations: int,
        paper_vector: list[float] | None = None,
    ) -> float:

        if self._is_ignored_by_keyword(title, abstract):
            return 0.0

        if self.embedding_service is not None:
            if paper_vector is None:
                paper_vector = self.embedding_service.embed(f"{title}. {abstract}")
            if self._is_ignored_by_similarity(paper_vector, title):
                return 0.0

        interest_score = self._interest_score(title, abstract, paper_vector)
        conference_score = self._conference_score(conference)
        author_score = self._author_score(author_names)
        novelty_score = self._novelty_score(published_date)
        citation_score = self._citation_score(citations)

        final_score = (
            0.35 * interest_score +
            0.20 * similarity +
            0.15 * conference_score +
            0.10 * author_score +
            0.10 * novelty_score +
            0.10 * citation_score
        )

        return round(final_score, 4)

    def _is_ignored_by_keyword(self, title: str, abstract: str) -> bool:
        text = f"{title} {abstract}".lower()
        for ignored_topic in self.profile.ignored:
            expanded = get_or_enrich_topic(ignored_topic)
            candidates = [w.strip().lower() for w in expanded.split(",")]
            if any(candidate and candidate in text for candidate in candidates):
                return True
        return False

    def _is_ignored_by_similarity(self, paper_vector: list[float], title: str) -> bool:
        if not self._ignored_vectors:
            return False

        similarities = [
            self._cosine_similarity(paper_vector, vector)
            for vector in self._ignored_vectors
        ]
        max_similarity = max(similarities)

        if self.debug:
            ranked = sorted(
                zip(self._ignored_terms, similarities),
                key=lambda item: item[1],
                reverse=True,
            )
            print(f"[DEBUG] ignored similarities | {title[:60]}")
            for term, similarity in ranked[:10]:
                print(f"[DEBUG]   {similarity:.4f} | {term}")

        return max_similarity >= IGNORED_SIMILARITY_THRESHOLD

    def _interest_score(
        self,
        title: str,
        abstract: str,
        paper_vector: list[float] | None,
    ) -> float:
        if paper_vector is not None and self._interest_vector is not None:
            similarity = self._cosine_similarity(paper_vector, self._interest_vector)
            return max(similarity, 0.0)

        text = f"{title} {abstract}".lower()
        max_priority = max(self.profile.priority.values(), default=100)
        total = 0.0
        matches = 0
        for interest, weight in self.profile.priority.items():
            if interest.lower() in text:
                total += weight / max_priority
                matches += 1
        if matches == 0:
            return 0.0
        return min(total / matches, 1.0)

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        magnitude_a = math.sqrt(sum(a * a for a in vec_a))
        magnitude_b = math.sqrt(sum(b * b for b in vec_b))
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        return dot_product / (magnitude_a * magnitude_b)

    def _conference_score(self, conference: str | None) -> float:
        if not conference:
            return 0.0
        return 1.0 if conference in self.profile.favorite_conferences else 0.3

    def _author_score(self, author_names: list[str]) -> float:
        if not author_names:
            return 0.0
        favorites_lower = [a.lower() for a in self.profile.favorite_authors]
        for name in author_names:
            if name.lower() in favorites_lower:
                return 1.0
        return 0.2

    def _novelty_score(self, published_date: date | None) -> float:
        if not published_date:
            return 0.0
        days_old = (date.today() - published_date).days
        return math.exp(-days_old / 365)

    def _citation_score(self, citations: int) -> float:
        if citations <= 0:
            return 0.0
        return min(math.log1p(citations) / math.log1p(1000), 1.0)