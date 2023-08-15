from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "record" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "status" VARCHAR(7) NOT NULL  DEFAULT 'pending',
    "file_path" VARCHAR(1024) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "record"."status" IS 'DONE: done\nERROR: error\nPENDING: pending\nDELETED: deleted';
CREATE TABLE IF NOT EXISTS "stem" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(6) NOT NULL,
    "file_path" VARCHAR(1024) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "stem"."type" IS 'VOCAL: vocals\nBASS: bass\nDRUMS: drums\nGUITAR: guitar\nOTHER: other';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
