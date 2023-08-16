from fastapi import APIRouter, Depends
from starlette import status

from api import responses
from api.endpoints import records
from core.deps import token_validation

router = APIRouter(
    dependencies=[Depends(token_validation)],
    responses={
        status.HTTP_401_UNAUTHORIZED: responses.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN: responses.HTTP_403_FORBIDDEN,
    },
)

router.include_router(records.router, tags=["records"], prefix="/records")
