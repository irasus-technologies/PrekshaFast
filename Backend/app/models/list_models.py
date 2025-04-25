# # app/models/list_models.py

# from sqlalchemy.ext.asyncio import AsyncSession
# from redis.asyncio import Redis
# from hashlib import md5
# import json

# # Parameterized SQL query with filters
# SQL_QUERY = """
# SELECT * FROM "snipe-it".models
# WHERE (:status_label IS NULL OR status_label = :status_label)
# AND (:model_name IS NULL OR model_name = :model_name);
# """


# async def fetch_models_with_cache(
#     db: AsyncSession, redis: Redis, status_label: str = None, model_name: str = None
# ):
#     """Fetch models from DB and cache them in Redis."""

#     query_params = {
#         "status_label": status_label,
#         "model_name": model_name,
#     }

#     # Create a unique cache key
#     query_key = f"query_result:{md5(json.dumps(query_params, sort_keys=True).encode()).hexdigest()}"

#     # Try fetching from Redis
#     cached = await redis.get(query_key)
#     if cached:
#         return json.loads(cached)

#     try:
#         result = await db.execute(SQL_QUERY, query_params)
#         models = result.fetchall()

#         if not models:
#             return []

#         models_dict = [dict(row) for row in models]

#         await redis.set(query_key, json.dumps(models_dict), ex=60)
#         return models_dict

#     except Exception as e:
#         raise e
