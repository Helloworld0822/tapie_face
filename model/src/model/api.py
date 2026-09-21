from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from model.errors import (
    FacePipelineError,
    ImageTooLargeError,
    UnsupportedMediaTypeError,
)
from model.schemas import AnalysisResponse, ErrorResponse, ModelStatusResponse
from model.service import AnalysisService, LocalAnalysisService

_PACKAGE_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_ROOT.parents[1]
_STATIC_ROOT = _PACKAGE_ROOT / "static"
_ALLOWED_MEDIA_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
_MAX_IMAGE_BYTES = 10 * 1024 * 1024


def create_app(service: AnalysisService | None = None) -> FastAPI:
    analysis_service = service or LocalAnalysisService(
        reference_dir=_PROJECT_ROOT / "references",
        index_path=_PROJECT_ROOT / ".data" / "face-index.npz",
    )
    application = FastAPI(
        title="TAPIE FACE",
        version="0.1.0",
    )
    application.mount("/static", StaticFiles(directory=_STATIC_ROOT), name="static")

    @application.exception_handler(FacePipelineError)
    def handle_pipeline_error(_: Request, error: FacePipelineError) -> Response:
        body = ErrorResponse(code=error.code, message=error.public_message)
        return Response(
            status_code=error.status_code,
            content=body.model_dump_json(),
            media_type="application/json",
        )

    @application.get("/", include_in_schema=False)
    def index_page() -> FileResponse:
        return FileResponse(_STATIC_ROOT / "index.html")

    @application.get("/showcase", include_in_schema=False)
    def showcase_page() -> FileResponse:
        return FileResponse(_STATIC_ROOT / "showcase.html")

    @application.get("/api/status")
    def get_status() -> ModelStatusResponse:
        return analysis_service.status()

    @application.post("/api/reindex")
    def rebuild_index() -> ModelStatusResponse:
        return analysis_service.rebuild_index()

    @application.post("/api/analyze")
    def analyze_image(image: Annotated[UploadFile, File()]) -> AnalysisResponse:
        if image.content_type not in _ALLOWED_MEDIA_TYPES:
            raise UnsupportedMediaTypeError
        image_bytes = image.file.read(_MAX_IMAGE_BYTES + 1)
        if len(image_bytes) > _MAX_IMAGE_BYTES:
            raise ImageTooLargeError
        return analysis_service.analyze(image_bytes)

    return application


app = create_app()
