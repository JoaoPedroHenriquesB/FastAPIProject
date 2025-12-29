from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import registry, DeclarativeBase, MappedAsDataclass
from app.config.settings import settings

engine = create_async_engine(settings.DATABASE_URL)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSession() as session:
        yield session

table_registry = registry()
class Base(DeclarativeBase, MappedAsDataclass):
    registry = table_registry
