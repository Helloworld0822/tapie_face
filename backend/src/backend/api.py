from typing import ClassVar, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.api import create_app as create_model_app
from model.service import LocalAnalysisService
from pydantic import BaseModel, ConfigDict

from backend.config import Settings


class HealthResponse(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    status: Literal["ok"] = "ok"


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else Settings()
    service = LocalAnalysisService(
        reference_dir=config.reference_dir,
        index_path=config.index_path,
    )
    application = create_model_app(service)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/api/health")
    def health() -> HealthResponse:
        """Report HTTP liveness without loading models or requiring an index."""
        return HealthResponse()

    return application
