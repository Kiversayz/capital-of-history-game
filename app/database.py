from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# URL подключения
DATABASE_URL = "sqlite+aiosqlite:///./capital_of_history.db"

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # True, чтобы видеть SQL-запросы
    future=True
)

# Асинхронная фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session