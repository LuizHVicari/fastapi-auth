from app.core.shared.errors import AppError


class InvalidChallengeError(AppError):
    def __init__(self, challenge: str) -> None:
        super().__init__(f"Invalid or expired OAuth2 challenge: {challenge}", status_code=400)
