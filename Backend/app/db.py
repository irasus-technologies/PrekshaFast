import logging
import os
import sys
import asyncpg
from dotenv import load_dotenv
from redis import asyncio as aioredis
from typing import Optional

load_dotenv()

DB_POOL = None

logging.basicConfig(
    level=os.getenv("LOGGING_LEVEL", "DEBUG"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


# Initialize Postgres Database Connection Pool
async def init_db():
    global DB_POOL
    if DB_POOL is None:
        try:
            DB_POOL = await asyncpg.create_pool(
                user=os.getenv("POSTGRES_USERNAME"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DATABASE"),
                host=os.getenv("POSTGRES_HOSTNAME"),
                port=int(os.getenv("POSTGRES_PORTNUMBER", "5432")),
                min_size=5,
                max_size=30,
            )
            logging.info("🔌 Postgres DB pool initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Postgres DB pool: {e}")
            raise


# Acquire a DB connection from the pool (no async generator)
async def get_db_connection() -> asyncpg.Connection:
    if DB_POOL is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    try:
        conn = await DB_POOL.acquire()
        logging.debug("Acquired a DB connection")
        return conn
    except Exception as e:
        logging.error(f"Error acquiring DB connection: {e}")
        raise


# Release DB connection back to the pool
async def release_db_connection(conn: asyncpg.Connection):
    if conn:
        try:
            await DB_POOL.release(conn)
            logging.debug("Released DB connection")
        except Exception as e:
            logging.error(f"Error releasing DB connection: {e}")


# Redis setup
redis_client = aioredis.Redis(
    host=os.getenv("REDIS_HOSTNAME", "localhost"),
    port=int(os.getenv("REDIS_PORTNUMBER", "6379")),
    password=os.getenv("REDIS_PASSWORD", None),
    decode_responses=True,
)


# Cache a result in Redis with a given key and TTL (time-to-live)
async def cache_result(key: str, result: any, ttl: int = 3600):
    try:
        logging.debug(f"🔐 Caching result with key: {key}")
        await redis_client.setex(key, ttl, result)
    except Exception as e:
        logging.error(f"Error caching result with key {key}: {e}")


# Fetch a cached result from Redis by key
async def get_cached_result(key: str):
    try:
        logging.debug(f"📦 Fetching from cache with key: {key}")
        value = await redis_client.get(key)
        if value:
            logging.debug("✅ Cache hit")
        else:
            logging.debug("❌ Cache miss")
        return value
    except Exception as e:
        logging.error(f"Error fetching from cache with key {key}: {e}")
        return None


# import logging
# import os
# import sys
# import asyncpg
# from dotenv import load_dotenv
# from redis import asyncio as aioredis
# from typing import AsyncGenerator

# # Load environment variables from .env file
# load_dotenv()

# # Global DB pool variable
# DB_POOL = None

# # Setup logging
# logging.basicConfig(
#     level=os.getenv("LOGGING_LEVEL", "DEBUG"),
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(sys.stdout)],
# )


# # Initialize the DB connection pool
# async def init_db():
#     global DB_POOL
#     if DB_POOL is None:
#         DB_POOL = await asyncpg.create_pool(
#             user=os.getenv("POSTGRES_USERNAME"),
#             password=os.getenv("POSTGRES_PASSWORD"),
#             database=os.getenv("POSTGRES_DATABASE"),
#             host=os.getenv("POSTGRES_HOSTNAME"),
#             port=os.getenv("POSTGRES_PORTNUMBER"),
#             min_size=5,
#             max_size=30,
#         )


# # Function to get a DB connection from the pool
# async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
#     if DB_POOL is None:
#         raise RuntimeError("Database pool not initialized. Call init_db() first.")
#     async with DB_POOL.acquire() as connection:
#         logging.debug("Acquired a DB connection")
#         yield connection
#         logging.debug("Released the DB connection")


# # Redis client setup
# redis_client = aioredis.Redis(
#     host=os.getenv("REDIS_HOSTNAME", ""),
#     port=int(os.getenv("REDIS_PORTNUMBER", "6379")),
#     password=os.getenv("REDIS_PASSWORD"),
#     decode_responses=True,
# )


# # Cache a result in Redis
# async def cache_result(key: str, result: any, ttl: int = 3600):
#     logging.debug(f"Caching data in Redis with key: {key}")
#     await redis_client.setex(key, ttl, result)


# # Get cached result from Redis
# async def get_cached_result(key: str):
#     logging.debug(f"Fetching data from Redis with key: {key}")
#     cached_result = await redis_client.get(key)
#     if cached_result:
#         logging.debug(f"Cache hit for key: {key}")
#     else:
#         logging.debug(f"Cache miss for key: {key}")
#     return cached_result
