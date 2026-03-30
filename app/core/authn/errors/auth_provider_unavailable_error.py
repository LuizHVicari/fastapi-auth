from app.core.shared.errors import AppError


class AuthProviderUnavailableError(AppError):
    def __init__(self) -> None:
        super().__init__(message="Auth service unavailable", status_code=503)
