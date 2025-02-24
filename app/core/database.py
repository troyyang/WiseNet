import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from . import config

# Update the connection parameters as needed
DATABASE_URL = (
    f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
    f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)

# Configure connection pool parameters
POOL_SIZE = 100  # Number of connections to keep in the pool
MAX_OVERFLOW = 20  # Number of connections to allow beyond the pool size
POOL_TIMEOUT = 30  # Seconds to wait before giving up on getting a connection
POOL_RECYCLE = 1800  # Connections older than this many seconds will be recycled

# Create the SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE
)

# Create a configured "AsyncSession" class
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Declarative base class for ORM models
DBBase = declarative_base()
db_semaphore = asyncio.Semaphore(POOL_SIZE)

class AsyncCustomSession:
    def __init__(self):
        self._session = AsyncSessionLocal()

    async def commit(self):
        """Commit the current transaction."""
        try:
            if config.API_ENV.lower() != "test":
                await self._session.commit()
        except Exception as e:
            print(f"Error committing session: {e}")
            await self._session.rollback()
            raise

    async def refresh(self, instance):
        """Refresh the state of an instance from the database."""
        try:
            if instance not in self._session:
                print(f"Instance {instance} is not in the session. Adding it now.")
                self._session.add(instance)

            if config.API_ENV.lower() != "test":
                await self._session.refresh(instance)
        except Exception as e:
            print(f"Error refreshing instance {instance}: {e}")
            await self._session.rollback()
            raise

    async def close(self):
        """Close the session."""
        if config.API_ENV.lower() == "test":
            await self._session.rollback()
        await self._session.close()

    def __getattr__(self, name):
        """Delegate attribute access to the underlying session."""
        return getattr(self._session, name)

# Provide an async context manager for session management
@asynccontextmanager
async def get_async_session():
    """Provide a transactional scope for session management."""
    async with db_semaphore:
        session = AsyncCustomSession()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage example:
# async with get_async_session() as session:
#     # Perform database operations
#     pass
