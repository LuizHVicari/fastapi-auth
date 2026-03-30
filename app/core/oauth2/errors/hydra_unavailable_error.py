from app.core.shared.errors import AppError


class HydraUnavailableError(AppError):
    def __init__(self) -> None:
        super().__init__("Hydra authorization server is unavailable", status_code=503)
