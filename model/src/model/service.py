from pathlib import Path
from threading import RLock
from typing import Protocol, final

from model.engine import FaceEngine, UniFaceEngine
from model.errors import (
    InvalidImageError,
    MissingLandmarksError,
    NoFaceError,
    NoReferenceImagesError,
    NoReferenceIndexError,
)
from model.index_store import ReferenceIndexStore
from model.schemas import (
    AnalysisResponse,
    ArtifactImages,
    MatchResponse,
    ModelState,
    ModelStatusResponse,
)
from model.similarity import Embedding, ReferenceVector, aggregate_embeddings, rank_matches

_IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp"})


class AnalysisService(Protocol):
    def status(self) -> ModelStatusResponse: ...

    def rebuild_index(self) -> ModelStatusResponse: ...

    def analyze(self, image_bytes: bytes) -> AnalysisResponse: ...


@final
class LocalAnalysisService:
    """Mutable application service because it owns lazy models and a replaceable index."""

    def __init__(self, reference_dir: Path, index_path: Path) -> None:
        self._reference_dir: Path = reference_dir
        self._store: ReferenceIndexStore = ReferenceIndexStore(index_path)
        self._references: tuple[ReferenceVector, ...] = self._store.load()
        self._engine: FaceEngine | None = None
        self._state: ModelState = "ready" if self._references else "idle"
        self._message: str = (
            "기준 벡터 준비됨" if self._references else "기준 인물 사진이 필요합니다"
        )
        self._lock: RLock = RLock()

    def status(self) -> ModelStatusResponse:
        with self._lock:
            return self._status_response()

    def rebuild_index(self) -> ModelStatusResponse:
        with self._lock:
            self._state = "indexing"
            self._message = "YOLO 정렬과 얼굴 벡터를 생성하는 중입니다"
            try:
                engine = self._get_engine()
                references = self._build_references(engine)
                self._store.save(references)
                self._references = references
                self._state = "ready"
                self._message = "모델과 기준 벡터 준비됨"
            except NoReferenceImagesError:
                self._state = "error"
                self._message = "기준 인물 사진을 확인해 주세요"
                raise
            return self._status_response()

    def analyze(self, image_bytes: bytes) -> AnalysisResponse:
        with self._lock:
            if not self._references:
                raise NoReferenceIndexError
            processed = self._get_engine().process(image_bytes)
            matches = rank_matches(processed.embedding, self._references)
            return AnalysisResponse(
                artifacts=ArtifactImages(
                    original=processed.original,
                    detected=processed.detected,
                    aligned=processed.aligned,
                    masked=processed.masked,
                ),
                detector_confidence=processed.confidence,
                warnings=processed.warnings,
                matches=tuple(
                    MatchResponse(
                        label=match.label,
                        cosine=match.cosine,
                        score=match.score,
                        reference_count=match.reference_count,
                    )
                    for match in matches
                ),
            )

    def _get_engine(self) -> FaceEngine:
        if self._engine is None:
            self._engine = UniFaceEngine()
        return self._engine

    def _build_references(self, engine: FaceEngine) -> tuple[ReferenceVector, ...]:
        grouped: list[ReferenceVector] = []
        if not self._reference_dir.exists():
            raise NoReferenceImagesError
        for person_dir in sorted(path for path in self._reference_dir.iterdir() if path.is_dir()):
            embeddings: list[Embedding] = []
            for image_path in sorted(person_dir.iterdir()):
                if image_path.suffix.lower() not in _IMAGE_SUFFIXES:
                    continue
                try:
                    embeddings.append(engine.process(image_path.read_bytes()).embedding)
                except (InvalidImageError, MissingLandmarksError, NoFaceError):
                    continue
            if embeddings:
                grouped.append(
                    ReferenceVector(
                        label=person_dir.name,
                        embedding=aggregate_embeddings(tuple(embeddings)),
                        image_count=len(embeddings),
                    )
                )
        if not grouped:
            raise NoReferenceImagesError
        return tuple(grouped)

    def _status_response(self) -> ModelStatusResponse:
        return ModelStatusResponse(
            state=self._state,
            message=self._message,
            indexed_people=len(self._references),
            indexed_images=sum(item.image_count for item in self._references),
        )
