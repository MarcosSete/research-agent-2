import math
from datetime import date
from app.config.research_profile_loader import ResearchProfile

class PaperScorer:
    def __init__(self, profile: ResearchProfile):
        self.profile = profile

    def score(
            self,
            title: str,
            abstract: str,
            similarity: float,
            conference: str | None,
            author_names: list[str],
            published_date: date | None,
            citations: int,
    ) -> float:

        if self._is_ignored(title, abstract):
            return 0.0

        interest_score = self._interest_score(title, abstract)
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

    def _is_ignored(self, title: str, abstract: str) -> bool:
        """Checagem de exclusão total - roda antes de qualquer outro cálculo."""
        text = f"{title} {abstract}".lower()
        return any(ignored.lower() in text for ignored in self.profile.ignored)

    def _interest_score(self, title: str, abstract: str) -> float:
        """Combina o texto do paper com os interesses do perfil (busca por palavra-chave)."""
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
        """Papers mais recentes pontuam mais. Decaimento exponencial em 365 dias."""
        if not published_date:
            return 0.0
        days_old = (date.today() - published_date).days
        return math.exp(-days_old / 365)

    def _citation_score(self, citations: int) -> float:
        """Normaliza citações usando log, já que a distribuição é bem desigual."""
        if citations <= 0:
            return 0.0
        return min(math.log1p(citations) / math.log1p(1000), 1.0)