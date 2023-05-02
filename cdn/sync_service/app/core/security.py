from http import HTTPStatus

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

token_header = APIKeyHeader(name="Authorization", auto_error=False)


async def check_auth_token(token_header: str = Security(token_header)):
    if token_header != settings.SECRET_KEY and token_header != f"Bearer {settings.SECRET_KEY}":
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Invalid authorization token")
