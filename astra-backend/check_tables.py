import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def check():
    url = os.environ['DATABASE_URL']
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        for row in result:
            print(row[0])
    await engine.dispose()
asyncio.run(check())
