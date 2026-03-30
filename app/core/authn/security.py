from fastapi.security import APIKeyCookie, APIKeyHeader

kratos_session_token = APIKeyHeader(
    name="X-Session-Token",
    description="Ory Kratos session token.",
    auto_error=False,
)

kratos_session_cookie = APIKeyCookie(
    name="ory_kratos_session",
    description="Ory Kratos session cookie.",
    auto_error=False,
)
