from fastapi import APIRouter, Depends
from starlette import status

from app.api import responses
from app.api.endpoints import records, tts, prompts
from app.core.deps import token_validation

router = APIRouter(
    dependencies=[Depends(token_validation)],
    responses={
        status.HTTP_401_UNAUTHORIZED: responses.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: responses.HTTP_403_FORBIDDEN,
    },
)

router.include_router(records.router, tags=["records"], prefix="/records")
router.include_router(tts.router, tags=["tts"], prefix="/tts")
router.include_router(prompts.router, tags=["prompts"], prefix="/prompts")
