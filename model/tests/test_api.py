from dataclasses import dataclass

from fastapi.testclient import TestClient

from model.api import create_app
from model.schemas import (
    AnalysisResponse,
    ArtifactImages,
    MatchResponse,
    ModelStatusResponse,
)


@dataclass(frozen=True, slots=True)
class FakeAnalysisService:
    def status(self) -> ModelStatusResponse:
        return ModelStatusResponse(
            state="ready",
            message="모델 준비됨",
            indexed_people=1,
            indexed_images=2,
        )

    def rebuild_index(self) -> ModelStatusResponse:
        return self.status()

    def analyze(self, image_bytes: bytes) -> AnalysisResponse:
        assert image_bytes == b"fake-image"
        return AnalysisResponse(
            artifacts=ArtifactImages(
                original="data:image/png;base64,AA==",
                detected="data:image/png;base64,AA==",
                aligned="data:image/png;base64,AA==",
                masked="data:image/png;base64,AA==",
            ),
            detector_confidence=0.98,
            warnings=(),
            matches=(
                MatchResponse(
                    label="reference-person",
                    cosine=0.72,
                    score=100.0,
                    reference_count=2,
                ),
            ),
        )


def test_status_when_service_is_ready_then_returns_index_counts() -> None:
    # Given
    client = TestClient(create_app(FakeAnalysisService()))

    # When
    response = client.get("/api/status")

    # Then
    assert response.status_code == 200
    assert response.json()["indexed_people"] == 1


def test_analyze_when_image_is_valid_then_returns_ranked_match() -> None:
    # Given
    client = TestClient(create_app(FakeAnalysisService()))

    # When
    response = client.post(
        "/api/analyze",
        files={"image": ("face.png", b"fake-image", "image/png")},
    )

    # Then
    assert response.status_code == 200
    assert response.json()["matches"][0]["label"] == "reference-person"


def test_analyze_when_media_type_is_not_an_image_then_rejects_boundary() -> None:
    # Given
    client = TestClient(create_app(FakeAnalysisService()))

    # When
    response = client.post(
        "/api/analyze",
        files={"image": ("face.txt", b"fake-image", "text/plain")},
    )

    # Then
    assert response.status_code == 415
