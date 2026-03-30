from app.core.shared.errors import AppError


class InvalidSessionError(AppError):
    def __init__(self) -> None:
        super().__init__(message="Invalid session token", status_code=401)
