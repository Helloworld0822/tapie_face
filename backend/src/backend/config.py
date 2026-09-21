from pathlib import Path
from typing import ClassVar, Final

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT: Final = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Local server configuration, read from TAPIE_* variables or backend/.env."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="TAPIE_",
        env_file=_REPO_ROOT / "backend" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    host: str = "127.0.0.1"
    port: int = Field(default=8001, ge=1, le=65535)
    reference_dir: Path = _REPO_ROOT / "model" / "references"
    index_path: Path = _REPO_ROOT / "model" / ".data" / "face-index.json"
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    @field_validator("reference_dir", "index_path")
    @classmethod
    def resolve_data_path(cls, value: Path) -> Path:
        """Resolve relative data paths against the repository, regardless of cwd."""
        return (_REPO_ROOT / value.expanduser()).resolve()
