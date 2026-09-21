from pathlib import Path
from typing import ClassVar, final

import numpy as np
from pydantic import BaseModel, ConfigDict, ValidationError

from model.similarity import ReferenceVector


class StoredReference(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    label: str
    embedding: tuple[float, ...]
    image_count: int


class StoredIndex(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    references: tuple[StoredReference, ...]


@final
class ReferenceIndexStore:
    def __init__(self, path: Path) -> None:
        self._path = path.with_suffix(".json")

    def load(self) -> tuple[ReferenceVector, ...]:
        if not self._path.exists():
            return ()
        try:
            stored = StoredIndex.model_validate_json(self._path.read_text(encoding="utf-8"))
        except (OSError, ValidationError):
            return ()
        return tuple(
            ReferenceVector(
                label=item.label,
                embedding=np.asarray(item.embedding, dtype=np.float32),
                image_count=item.image_count,
            )
            for item in stored.references
        )

    def save(self, references: tuple[ReferenceVector, ...]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        stored = StoredIndex(
            references=tuple(
                StoredReference(
                    label=item.label,
                    embedding=tuple(float(value) for value in item.embedding),
                    image_count=item.image_count,
                )
                for item in references
            )
        )
        _ = self._path.write_text(stored.model_dump_json(), encoding="utf-8")
