import time
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract session data
        session = request.session
        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")
        expires_at = session.get("access_token_expires_at")

        current_time = time.time()

        # Token expiration check
        if access_token and expires_at and current_time >= expires_at:
            # Attempt token refresh
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url="http://localhost:8000/refresh",  # Adjust the URL if necessary
                        json={"refresh_token": refresh_token},
                    )
                if response.status_code != 200:
                    return Response("Unauthorized", status_code=401)

                token_data = response.json()
                session["access_token"] = token_data["access_token"]
                session["refresh_token"] = token_data["refresh_token"]
                session["access_token_expires_at"] = (
                    current_time + token_data["expires_in"]
                )
            except Exception as e:
                return Response("Internal Server Error", status_code=500)

        # Continue with request processing
        return await call_next(request)


# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from starlette.responses import Response
# from starlette.types import ASGIApp
# from fastapi import status
# import time
# import logging
# import httpx  # used instead of requests for async
# import asyncio

# logger = logging.getLogger("uvicorn")


# class TokenRefreshMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app: ASGIApp):
#         super().__init__(app)

#     async def dispatch(self, request: Request, call_next):
#         try:
#             session = request.session  # requires SessionMiddleware to be active
#         except AssertionError:
#             logger.error("❌ SessionMiddleware not installed — session unavailable.")
#             return Response(
#                 "Session not available",
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         access_token = session.get("access_token")
#         refresh_token = session.get("refresh_token")
#         expires_at = session.get("access_token_expires_at")  # UNIX timestamp

#         current_time = time.time()

#         logger.debug("🛂 Checking access token validity...")
#         logger.debug(f"📦 Session access_token: {access_token}")
#         logger.debug(f"⏱️ Current time: {current_time}, Expires at: {expires_at}")

#         # Step 1: If access token is missing or expired
#         if access_token and expires_at and current_time >= expires_at:
#             logger.info("🔁 Access token expired. Attempting to refresh...")

#             try:
#                 async with httpx.AsyncClient() as client:
#                     response = await client.post(
#                         url="http://localhost:8000/refresh",
#                         json={"refresh_token": refresh_token},
#                     )

#                 if response.status_code != 200:
#                     logger.error(
#                         f"❌ Failed to refresh token. Status: {response.status_code}, Message: {response.text}"
#                     )
#                     return Response(
#                         "Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED
#                     )

#                 token_data = response.json()

#                 # Step 3: Update session with new tokens
#                 session["access_token"] = token_data["access_token"]
#                 session["refresh_token"] = token_data["refresh_token"]
#                 session["access_token_expires_at"] = (
#                     current_time + token_data["expires_in"]
#                 )

#                 logger.info(
#                     "✅ Access token successfully refreshed and session updated."
#                 )
#                 logger.debug(f"📦 New access_token: {session['access_token']}")
#                 logger.debug(f"⏱️ New expiry time: {session['access_token_expires_at']}")

#             except Exception as e:
#                 logger.exception("❌ Exception occurred while refreshing token.")
#                 return Response("Internal Server Error", status_code=500)

#         elif not access_token:
#             logger.warning("🚫 No access token in session.")
#         else:
#             logger.debug("✅ Access token is still valid.")

#         # Step 4: Proceed to the next route handler
#         response = await call_next(request)
#         return response
