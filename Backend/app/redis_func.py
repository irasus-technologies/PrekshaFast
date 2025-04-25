from app import redis_client
from app import get_db_connection
import asyncpg
import json

from app.utils import get_md5_hash, json_serialiser
from app import logging


async def fetch_cache_aware(db: asyncpg.Connection, query: str, params: dict):
    results = []

    # Use a hardcoded email for the key
    hardcoded_email = "test@example.com"

    # Generate a hash for the query and parameters
    query_hash = get_md5_hash(f"{query}_{str(params)}")
    cache_key = f"query_results:{hardcoded_email}:{query_hash}"

    # Check if the key exists in Redis
    if await redis_client.keys(cache_key):
        logging.debug(f"Query {cache_key} is already cached")

        # Retrieve the cached result
        query_results_str = await redis_client.get(cache_key)
        results = json.loads(query_results_str)

        logging.debug(f"Cached result retrieved: {str(results)}")
        return results

    else:
        logging.debug("Query is not cached. Fetching from the database.")

        # Fetch data from the database
        rows = await db.fetch(query=query, **params, timeout=600)
        for row in rows:
            result = {}
            for key, value in row.items():
                result[key] = value

            results.append(result)

        # Cache the results in Redis
        logging.debug(f"Caching results to Redis with key: {cache_key}")
        await redis_client.set(
            cache_key, json.dumps(results, default=json_serialiser), ex=1 * 60
        )

    return results


# from app import redis_client
# from app import get_db_connection
# import asyncpg
# import json

# from app.utils import get_md5_hash, json_serialiser
# from app import logging


# async def fetch_cache_aware(
#     db: asyncpg.Connection, email: str, query: str, params: dict
# ):
#     results = []

#     query_hash = get_md5_hash(f"{query}_{str(params)}")
#     cache_key = f"query_results:{email}:{query_hash}"

#     if await redis_client.keys(cache_key):
#         logging.debug(f"Query {cache_key} is already cached")

#         query_results_str = await redis_client.get(cache_key)
#         results = json.loads(query_results_str)

#         logging.debug(f"Cached result: {str(results)}")
#         return results

#     else:
#         logging.debug("Query is not cached. Fetching from db.")

#         rows = await db.fetch(query=query, **params, timeout=600)
#         for row in rows:
#             result = {}
#             for key, value in row.items():
#                 result[key] = value

#             results.append(result)

#         logging.debug(f"Caching results to redis with key: {cache_key}")
#         await redis_client.set(
#             cache_key, json.dumps(results, default=json_serialiser), ex=1 * 60
#         )

#     return results
