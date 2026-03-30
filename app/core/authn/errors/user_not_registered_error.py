from app.core.shared.errors import AppError


class UserNotRegisteredError(AppError):
    def __init__(self) -> None:
        super().__init__(message="User is not registered", status_code=401)
