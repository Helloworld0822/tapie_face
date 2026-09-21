"""Validated API response models."""

from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

type ModelState = Literal["idle", "indexing", "ready", "error"]


class ModelStatusResponse(BaseModel):
    """Current model and reference-index readiness."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    state: ModelState
    message: str
    indexed_people: int = Field(ge=0)
    indexed_images: int = Field(ge=0)


class ArtifactImages(BaseModel):
    """Four visual stages returned to the correction rail."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    original: str
    detected: str
    aligned: str
    masked: str


class MatchResponse(BaseModel):
    """One reference identity similarity result."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    label: str
    cosine: float = Field(ge=-1.0, le=1.0)
    score: float = Field(ge=0.0, le=100.0)
    reference_count: int = Field(ge=1)


class AnalysisResponse(BaseModel):
    """Complete observable result for one uploaded portrait."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    artifacts: ArtifactImages
    detector_confidence: float = Field(ge=0.0, le=1.0)
    warnings: tuple[str, ...]
    matches: tuple[MatchResponse, ...]


class ErrorResponse(BaseModel):
    """Stable error body announced by the frontend."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    code: str
    message: str
