from uuid import UUID

from app.core.shared.errors import AppError


class ApiKeyNotFoundError(AppError):
    def __init__(self, *, public_key: str | None = None, key_id: UUID | None = None) -> None:
        if public_key is not None:
            message = f"API key with public key '{public_key}' not found"
        elif key_id is not None:
            message = f"API key with id '{key_id}' not found"
        else:
            message = "API key not found"
        super().__init__(message)
