"""Pure embedding aggregation and similarity ranking."""

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

from model.errors import EmptyEmbeddingsError

type Embedding = NDArray[np.float32]

_SCORE_FLOOR: Final = 0.20
_SCORE_CEILING: Final = 0.70


@dataclass(frozen=True, slots=True)
class ReferenceVector:
    """One persisted centroid for a reference identity."""

    label: str
    embedding: Embedding
    image_count: int


@dataclass(frozen=True, slots=True)
class RankedMatch:
    """One comparison result ordered by cosine similarity."""

    label: str
    cosine: float
    score: float
    reference_count: int


def normalize_embedding(embedding: Embedding) -> Embedding:
    """Return an L2-normalized float32 embedding."""
    vector = np.asarray(embedding, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        raise EmptyEmbeddingsError
    return np.asarray(vector / norm, dtype=np.float32)


def aggregate_embeddings(embeddings: tuple[Embedding, ...]) -> Embedding:
    """Build a unit centroid so several photos represent one person."""
    if not embeddings:
        raise EmptyEmbeddingsError
    normalized = tuple(normalize_embedding(item) for item in embeddings)
    centroid = np.mean(np.stack(normalized), axis=0, dtype=np.float32)
    return normalize_embedding(np.asarray(centroid, dtype=np.float32))


def similarity_score(cosine: float) -> float:
    """Map raw cosine to a conservative 0-100 display score."""
    scaled = (cosine - _SCORE_FLOOR) / (_SCORE_CEILING - _SCORE_FLOOR) * 100.0
    return round(min(100.0, max(0.0, scaled)), 1)


def rank_matches(
    query: Embedding,
    references: tuple[ReferenceVector, ...],
    *,
    limit: int = 3,
) -> tuple[RankedMatch, ...]:
    """Rank reference centroids by cosine similarity."""
    normalized_query = normalize_embedding(query)
    matches = tuple(_to_match(normalized_query, reference) for reference in references)
    return tuple(sorted(matches, key=lambda item: item.cosine, reverse=True)[:limit])


def _to_match(query: Embedding, reference: ReferenceVector) -> RankedMatch:
    cosine = float(query @ reference.embedding)
    return RankedMatch(
        label=reference.label,
        cosine=round(cosine, 4),
        score=similarity_score(cosine),
        reference_count=reference.image_count,
    )
