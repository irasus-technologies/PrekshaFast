# from fastapi import APIRouter, HTTPException, Depends
# from Backend.app.battery_packs.db import init_db, get_db_connection, get_cached_result, cache_result
# from asyncpg import Connection
# from app.utils import get_md5_hash
# import json
# from datetime import datetime
# import logging

# router = APIRouter(prefix="/models")


# async def get_db_with_init():
#     await init_db()  # Ensure the DB pool is initialized
#     async for (
#         conn
#     ) in get_db_connection():  # Use async for to iterate over the generator
#         yield conn


# def serialize_record(record):
#     """Convert datetime objects in a record to strings."""
#     for key, value in record.items():
#         if isinstance(value, datetime):
#             record[key] = value.isoformat()  # Convert datetime to ISO 8601 string
#     return record


# @router.get("/")
# async def get_models(conn: Connection = Depends(get_db_with_init)):
#     # Hardcoded email for now
#     email = "test@example.com"

#     # Query to execute
#     query = 'SELECT * FROM "snipe-it".models'

#     # Generate the hashed query
#     hashed_query = get_md5_hash(query)

#     # Generate the Redis key
#     redis_key = f"{email}:{hashed_query}"
#     logging.debug(f"Generated Redis key: {redis_key}")

#     # Try to get cached data from Redis
#     logging.debug(f"Checking Redis cache for key: {redis_key}")
#     cached_data = await get_cached_result(redis_key)

#     if cached_data:
#         logging.debug("Cache hit. Returning cached data.")
#         # If cached data is found, return it directly
#         return {"status": "ok", "data": json.loads(cached_data)}

#     logging.debug("Cache miss. Querying the database.")

#     # If no cached data, query the database
#     records = await conn.fetch(query)

#     if not records:
#         logging.debug("No records found in the database.")
#         raise HTTPException(status_code=404, detail="No data found")

#     logging.debug(f"Fetched {len(records)} records from the database.")

#     # Convert records to a list of dictionaries and serialize datetime objects
#     result = [serialize_record(dict(record)) for record in records]

#     # Cache the result in Redis
#     logging.debug(f"Caching result in Redis with key: {redis_key}")
#     await cache_result(redis_key, json.dumps(result), ttl=3600)  # Cache for 1 hour

#     # Return the result as JSON
#     logging.debug("Returning data to the client.")
#     return {"status": "ok", "data": result}


# # from fastapi import APIRouter, HTTPException, Depends
# # from db import init_db, get_db_connection, get_cached_result, cache_result
# # from asyncpg import Connection
# # import json
# # from datetime import datetime

# # router = APIRouter(prefix="/models")


# # async def get_db_with_init():
# #     await init_db()  # Ensure the DB pool is initialized
# #     async for (
# #         conn
# #     ) in get_db_connection():  # Use async for to iterate over the generator
# #         yield conn


# # def serialize_record(record):
# #     """Convert datetime objects in a record to strings."""
# #     for key, value in record.items():
# #         if isinstance(value, datetime):
# #             record[key] = value.isoformat()  # Convert datetime to ISO 8601 string
# #     return record


# # @router.get("/")
# # async def get_models(conn: Connection = Depends(get_db_with_init)):
# #     redis_key = "models_data_cache"

# #     # Try to get cached data from Redis
# #     cached_data = await get_cached_result(redis_key)

# #     if cached_data:
# #         # If cached data is found, return it directly
# #         return {"status": "ok", "data": json.loads(cached_data)}

# #     # If no cached data, query the database
# #     query = 'SELECT * FROM "snipe-it".models'
# #     records = await conn.fetch(query)

# #     if not records:
# #         raise HTTPException(status_code=404, detail="No data found")

# #     # Convert records to a list of dictionaries and serialize datetime objects
# #     result = [serialize_record(dict(record)) for record in records]

# #     # Cache the result in Redis
# #     await cache_result(redis_key, json.dumps(result), ttl=3600)  # Cache for 1 hour

# #     # Return the result as JSON
# #     return {"status": "ok", "data": result}
