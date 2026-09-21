import numpy as np
import pytest

from model.similarity import ReferenceVector, aggregate_embeddings, rank_matches, similarity_score


def test_similarity_score_when_cosine_increases_then_score_is_monotonic() -> None:
    # Given
    cosines = (-1.0, 0.2, 0.45, 0.7, 1.0)

    # When
    scores = tuple(similarity_score(value) for value in cosines)

    # Then
    assert scores == tuple(sorted(scores))
    assert scores[0] == 0.0
    assert scores[-1] == 100.0


def test_aggregate_embeddings_when_multiple_images_then_returns_unit_centroid() -> None:
    # Given
    embeddings = (
        np.array([1.0, 0.0], dtype=np.float32),
        np.array([0.8, 0.2], dtype=np.float32),
    )

    # When
    centroid = aggregate_embeddings(embeddings)

    # Then
    assert np.linalg.norm(centroid) == pytest.approx(1.0)
    assert centroid[0] > centroid[1]


def test_rank_matches_when_references_exist_then_orders_highest_cosine_first() -> None:
    # Given
    query = np.array([1.0, 0.0], dtype=np.float32)
    references = (
        ReferenceVector("person-b", np.array([0.0, 1.0], dtype=np.float32), 1),
        ReferenceVector("person-a", np.array([1.0, 0.0], dtype=np.float32), 2),
    )

    # When
    matches = rank_matches(query, references, limit=2)

    # Then
    assert [match.label for match in matches] == ["person-a", "person-b"]
    assert matches[0].reference_count == 2
