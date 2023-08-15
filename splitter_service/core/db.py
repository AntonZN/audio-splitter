from tortoise import Tortoise

from app.core import get_settings

settings = get_settings()


async def init():
    await Tortoise.init(db_url=settings.DATABASE_URI, modules={"models": ["models"]})
