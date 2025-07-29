import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from api.core.config import Settings
from api.core.database import Base
from api.core.logger import logger

# Import all models to ensure they are registered with Base
from api.models import *  # noqa: F403

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

settings = Settings()
database_url: str = settings.database_url_from_components.render_as_string(hide_password=False)
config.set_main_option(name="sqlalchemy.url", value=database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url: str | None = config.get_main_option(name="sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


@retry(
    stop=stop_after_attempt(max_attempt_number=30),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(exception_types=(Exception,)),
    reraise=True,
)
async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    Includes automatic retry logic for database connectivity.

    """
    logger.info("Connecting to database for migrations...")

    connectable = async_engine_from_config(
        configuration=config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            logger.info("✅ Database connection successful, running migrations...")
            await connection.run_sync(do_run_migrations)
    except Exception as e:
        logger.warning(f"⏳ Database connection failed during migrations: {e}")
        raise
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
