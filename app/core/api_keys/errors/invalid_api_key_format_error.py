from app.core.shared.errors import AppError


class InvalidApiKeyFormatError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            message="The provided API key has an invalid format.",
        )
