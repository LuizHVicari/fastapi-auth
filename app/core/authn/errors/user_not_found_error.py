from uuid import UUID

from app.core.shared.errors import AppError


class UserNotFoundError(AppError):
    def __init__(self, user_id: UUID | None = None, auth_provider_id: str | None = None) -> None:
        identifier = str(user_id) if user_id is not None else auth_provider_id
        super().__init__(message=f"User not found: {identifier}", status_code=404)
