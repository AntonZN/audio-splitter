from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stem" ADD "record_id" UUID;
        ALTER TABLE "stem" ADD CONSTRAINT "fk_stem_record_bb06edce" FOREIGN KEY ("record_id") REFERENCES "record" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "stem" DROP CONSTRAINT "fk_stem_record_bb06edce";
        ALTER TABLE "stem" DROP COLUMN "record_id";"""
