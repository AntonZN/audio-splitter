from tortoise import Tortoise

from app.core.config import get_settings

settings = get_settings()


async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URI,
        modules={"models": settings.MODELS},
    )
