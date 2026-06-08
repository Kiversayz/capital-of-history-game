import asyncio
from app.database import engine, Base
from app.models import *  # КРИТИЧНО ВАЖНЫЙ ИМПОРТ!


async def init_db():
    """
    Функция для создания всех таблиц, описанных в моделях.
    """
    async with engine.begin() as conn:
        # run_sync нужен, потому что create_all — синхронная функция,
        # а мы работаем в асинхронном контексте.
        await conn.run_sync(Base.metadata.create_all)

    print("✅ База данных успешно инициализирована! Таблицы созданы.")


# Этот блок позволяет запустить файл как скрипт из командной строки
if __name__ == "__main__":
    asyncio.run(init_db())