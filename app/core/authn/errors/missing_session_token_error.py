from app.core.shared.errors import AppError


class MissingSessionTokenError(AppError):
    def __init__(self) -> None:
        super().__init__(message="Missing session token", status_code=401)
