from fastapi.security import APIKeyCookie, APIKeyHeader, OAuth2AuthorizationCodeBearer

from app.core.env import settings

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

# Documents the Hydra OAuth2 Authorization Code flow in Swagger UI.
# Used by MCP / API clients that obtain tokens via Ory Hydra.
hydra_oauth2 = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.hydra_public_url}/oauth2/auth",
    tokenUrl=f"{settings.hydra_public_url}/oauth2/token",
    scopes={"openid": "OpenID Connect", "offline": "Offline access (refresh tokens)"},
    auto_error=False,
)
