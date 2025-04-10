from fastapi import FastAPI
import loguru
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSessionTransaction
from sqlalchemy.pool.base import _ConnectionRecord

from src.repository.database import async_db
from src.repository.base import Base


@event.listens_for(target=async_db.async_engine.sync_engine, identifier="connect")
def inspect_db_server_on_connection(
    db_api_connection: AsyncAdapt_asyncpg_connection, connection_record: _ConnectionRecord
) -> None:
    loguru.logger.info(f"New DB API Connection ---\n {db_api_connection}")
    loguru.logger.info(f"Connection Record ---\n {connection_record}")


@event.listens_for(target=async_db.async_engine.sync_engine, identifier="close")
def inspect_db_server_on_close(
    db_api_connection: AsyncAdapt_asyncpg_connection, connection_record: _ConnectionRecord
) -> None:
    loguru.logger.info(f"Closing DB API Connection ---\n {db_api_connection}")
    loguru.logger.info(f"Closed Connection Record ---\n {connection_record}")


async def initialize_db_tables(connection: AsyncConnection) -> None:
    loguru.logger.info("Database Table Creation --- Initializing . . .")

    await connection.run_sync(Base.metadata.drop_all)
    await connection.run_sync(Base.metadata.create_all)
    from sqlalchemy import insert

    loguru.logger.info("Database Table Creation --- Successfully Initialized!")


    loguru.logger.info("Database Table Creation --- Initializing . . .")

    table_exists = False
    for table in Base.metadata.sorted_tables:
        exists = await connection.run_sync(
            lambda sync_conn: sync_conn.dialect.has_table(sync_conn, table.name)
        )
        if exists:
            table_exists = True
            break

    if not table_exists:
        loguru.logger.info("No tables found - Creating tables...")
        await connection.run_sync(Base.metadata.create_all)
    else:
        loguru.logger.info("Tables already exist - Skipping creation")

    loguru.logger.info("Database Table Creation --- Successfully Initialized!")


async def initialize_db_connection(backend_app: FastAPI) -> None:
    loguru.logger.info("Database Connection --- Establishing . . .")

    backend_app.state.db = async_db

    async with backend_app.state.db.async_engine.begin() as connection:
        await initialize_db_tables(connection=connection)

    loguru.logger.info("Database Connection --- Successfully Established!")


async def dispose_db_connection(backend_app: FastAPI) -> None:
    loguru.logger.info("Database Connection --- Disposing . . .")

    await backend_app.state.db.async_engine.dispose()

    loguru.logger.info("Database Connection --- Successfully Disposed!")
