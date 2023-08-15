from fastapi import HTTPException, status, Security
from fastapi.security.api_key import APIKeyQuery

from app.core.config import get_settings

settings = get_settings()
token_query = APIKeyQuery(name="token")


def token_validation(token: str = Security(token_query)) -> bool:
    if not token or token != settings.AUTH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return True
