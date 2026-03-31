from app.core.shared.errors import AppError


class UserAlreadyExistsError(AppError):
    def __init__(self, auth_provider_id: str) -> None:
        super().__init__(
            message=f"User already exists for auth provider ID: {auth_provider_id}",
            status_code=409,
        )
