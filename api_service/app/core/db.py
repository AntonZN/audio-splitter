from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import get_settings

settings = get_settings()


TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URI,
    },
    "apps": {
        "models": {
            "models": settings.MODELS,
            "default_connection": "default",
        },
    },
}


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        modules={"models": settings.MODELS},
        generate_schemas=False,
        add_exception_handlers=True,
    )
