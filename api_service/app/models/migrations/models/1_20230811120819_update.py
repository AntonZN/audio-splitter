from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stem" ALTER COLUMN "type" TYPE VARCHAR(50) USING "type"::VARCHAR(50);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stem" ALTER COLUMN "type" TYPE VARCHAR(6) USING "type"::VARCHAR(6);"""
