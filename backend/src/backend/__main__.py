from typing import Annotated

import typer
import uvicorn

from backend.api import create_app
from backend.config import Settings


def serve(
    host: Annotated[str | None, typer.Option(help="Server bind address.")] = None,
    port: Annotated[int | None, typer.Option(min=1, max=65535, help="Server port.")] = None,
) -> None:
    """Run the TAPIE FACE backend and local model workbench."""
    settings = Settings()
    uvicorn.run(
        create_app(settings),
        host=host if host is not None else settings.host,
        port=port if port is not None else settings.port,
    )


def main() -> None:
    typer.run(serve)


if __name__ == "__main__":
    main()
