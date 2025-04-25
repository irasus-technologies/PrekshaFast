# main.py
import logging
import os
import sys
import base64
import hashlib
import secrets
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.datastructures import URL
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

from app.db import init_db, redis_client
from app.middleware import TokenRefreshMiddleware
from app.battery_packs import router as battery_packs

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=os.getenv("LOGGING_LEVEL", "DEBUG"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# OAuth config
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
AUTH_URL = os.getenv("OAUTH_AUTH_URL")
TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")

app = FastAPI()

# Middlewares
app.add_middleware(TokenRefreshMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="my_session",
    same_site="lax",
    https_only=False,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(battery_packs, tags=["battery_packs"])


# PKCE generation
def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode("utf-8")
        .rstrip("=")
    )
    return code_verifier, code_challenge


@app.on_event("startup")
async def startup_event():
    await init_db()
    logging.info("✅ Database pool initialized")


@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.aclose()
    logging.info("🧹 Redis connection closed")


@app.get("/")
def home():
    return {"message": "You're logged in!"}


@app.get("/login")
def login(request: Request):
    code_verifier, code_challenge = generate_pkce_pair()
    request.session["code_verifier"] = code_verifier
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    url = URL(AUTH_URL).include_query_params(**params)
    return RedirectResponse(str(url))


@app.get("/callback")
async def callback(request: Request, code: str):
    code_verifier = request.session.get("code_verifier")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=token_resp.status_code, detail="Failed to retrieve token"
        )

    token_data = token_resp.json()
    request.session["access_token"] = token_data.get("access_token")
    request.session["refresh_token"] = token_data.get("refresh_token")
    request.session["access_token_expires_at"] = time.time() + token_data["expires_in"]
    return RedirectResponse("http://localhost:3000")


@app.get("/me")
async def me(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    expires_at = request.session.get("access_token_expires_at")
    if expires_at and time.time() >= expires_at:
        refresh_token = request.session.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token missing")

        async with httpx.AsyncClient() as client:
            refresh_resp = await client.post(
                "http://localhost:8000/refresh", json={"refresh_token": refresh_token}
            )

        if refresh_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to refresh token")

        token_data = refresh_resp.json()
        request.session["access_token"] = token_data["access_token"]
        request.session["refresh_token"] = token_data["refresh_token"]
        request.session["access_token_expires_at"] = (
            time.time() + token_data["expires_in"]
        )
        access_token = token_data["access_token"]

    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )

    if userinfo_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    return JSONResponse(content=userinfo_resp.json())


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    logout_redirect_uri = "http://localhost:3000"
    logout_url = URL(LOGOUT_URL).include_query_params(redirect_uri=logout_redirect_uri)
    return RedirectResponse(str(logout_url))


class RefreshTokenInput(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int


@app.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, input: RefreshTokenInput):
    refresh_token = input.refresh_token or request.session.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )

        token_data = response.json()
        request.session["access_token"] = token_data.get("access_token")
        request.session["refresh_token"] = token_data.get("refresh_token")
        request.session["access_token_expires_at"] = (
            time.time() + token_data["expires_in"]
        )

        return token_data

    except Exception as e:
        logging.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")


# import logging
# import os
# import base64
# import hashlib
# import secrets
# import time

# from app.middleware import TokenRefreshMiddleware
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import RedirectResponse, JSONResponse
# from dotenv import load_dotenv

# # from app.models import router as models_router
# from starlette.datastructures import URL
# from starlette.middleware.sessions import SessionMiddleware
# import httpx
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from app.battery_packs import router as battery_packs

# # Load environment variables from .env file
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI()

# # ✅ Add TokenRefreshMiddleware first
# app.add_middleware(TokenRefreshMiddleware)

# # ✅ Add SessionMiddleware after so it executes first
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=secrets.token_hex(32),  # Replace with a fixed key in production
#     session_cookie="my_session",
#     same_site="lax",
#     https_only=False,  # Set to True if using HTTPS in production
# )

# # Add CORS middleware for cross-origin support (adjust in prod)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Set specific frontend domains in prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Environment config
# CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
# AUTH_URL = os.getenv("OAUTH_AUTH_URL")
# TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
# USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")
# REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
# LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")

# # app.include_router(models_router)
# app.include_router(battery_packs, tags=["battery_packs"])


# def generate_pkce_pair():
#     code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
#     code_challenge = (
#         base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
#         .decode("utf-8")
#         .rstrip("=")
#     )
#     return code_verifier, code_challenge


# @app.get("/")
# def home():
#     return {"message": "You're logged in!"}


# @app.get("/login")
# def login(request: Request):
#     code_verifier, code_challenge = generate_pkce_pair()
#     request.session["code_verifier"] = code_verifier

#     print("👉 Redirecting to Keycloak")
#     print("   code_verifier:", code_verifier)
#     print("   code_challenge:", code_challenge)

#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": REDIRECT_URI,
#         "scope": "openid profile email",
#         "code_challenge": code_challenge,
#         "code_challenge_method": "S256",
#     }

#     url = URL(AUTH_URL).include_query_params(**params)
#     return RedirectResponse(str(url))


# @app.get("/callback")
# async def callback(request: Request, code: str):
#     print("➡️ /callback hit with code:", code)

#     code_verifier = request.session.get("code_verifier")
#     if not code_verifier:
#         raise HTTPException(status_code=400, detail="Missing code_verifier")

#     print("🧪 Verifying PKCE flow with code_verifier:", code_verifier)

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(
#             TOKEN_URL,
#             data={
#                 "grant_type": "authorization_code",
#                 "client_id": CLIENT_ID,
#                 "code": code,
#                 "redirect_uri": REDIRECT_URI,
#                 "code_verifier": code_verifier,
#             },
#             headers={"Content-Type": "application/x-www-form-urlencoded"},
#         )

#     print("🔁 Token response status:", token_resp.status_code)

#     if token_resp.status_code != 200:
#         print("❌ Failed token exchange:", token_resp.text)
#         raise HTTPException(
#             status_code=token_resp.status_code, detail="Failed to retrieve token"
#         )

#     token_data = token_resp.json()
#     request.session["access_token"] = token_data.get("access_token")
#     request.session["refresh_token"] = token_data.get(
#         "refresh_token"
#     )  # Store refresh token
#     # Set expiry time
#     request.session["access_token_expires_at"] = time.time() + token_data["expires_in"]
#     print("✅ Token stored in session")

#     return RedirectResponse("http://localhost:3000")  # Adjust frontend URL if needed


# @app.get("/me")
# async def me(request: Request):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     # Log the access token (be cautious in production!)
#     print("Access Token:", access_token)

#     # Ensure the access token is valid using middleware
#     current_time = time.time()
#     expires_at = request.session.get("access_token_expires_at")

#     if expires_at and current_time >= expires_at:
#         # If the access token is expired, refresh it using the refresh token
#         refresh_token = request.session.get("refresh_token")
#         if not refresh_token:
#             raise HTTPException(status_code=401, detail="Refresh token missing")

#         # Call the refresh token endpoint
#         async with httpx.AsyncClient() as client:
#             refresh_resp = await client.post(
#                 "http://localhost:8000/refresh",
#                 json={"refresh_token": refresh_token},
#             )

#         if refresh_resp.status_code != 200:
#             raise HTTPException(status_code=401, detail="Failed to refresh token")

#         token_data = refresh_resp.json()

#         # Update session with new tokens and expiry
#         request.session["access_token"] = token_data["access_token"]
#         request.session["refresh_token"] = token_data["refresh_token"]
#         request.session["access_token_expires_at"] = (
#             time.time() + token_data["expires_in"]
#         )

#         # Retry the userinfo request with the new access token
#         access_token = request.session["access_token"]

#     async with httpx.AsyncClient() as client:
#         userinfo_resp = await client.get(
#             USERINFO_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#         )

#     if userinfo_resp.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     return JSONResponse(content=userinfo_resp.json())


# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     logout_redirect_uri = "http://localhost:3000"
#     logout_url = URL(LOGOUT_URL).include_query_params(redirect_uri=logout_redirect_uri)
#     return RedirectResponse(str(logout_url))


# class RefreshTokenInput(BaseModel):
#     refresh_token: str


# class TokenResponse(BaseModel):
#     access_token: str
#     expires_in: int
#     refresh_token: str
#     refresh_expires_in: int


# # Endpoint to refresh access token using refresh token
# @app.post("/refresh", response_model=TokenResponse)
# async def refresh_token(request: Request, input: RefreshTokenInput):
#     refresh_token = input.refresh_token or request.session.get("refresh_token")

#     if not refresh_token:
#         raise HTTPException(status_code=400, detail="Missing refresh_token")

#     data = {
#         "grant_type": "refresh_token",
#         "refresh_token": refresh_token,
#         "client_id": CLIENT_ID,
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(TOKEN_URL, data=data, headers=headers)

#         # Check for successful response
#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code, detail=response.json()
#             )

#         # Parse the new token data
#         token_data = response.json()

#         # Store new tokens in the session
#         request.session["access_token"] = token_data.get("access_token")
#         request.session["refresh_token"] = token_data.get("refresh_token")
#         # Update expiry time
#         request.session["access_token_expires_at"] = (
#             time.time() + token_data["expires_in"]
#         )

#         return token_data

#     except httpx.HTTPStatusError as e:
#         logging.error(f"HTTP error occurred: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="An error occurred while attempting to refresh the token.",
#         )

#     except Exception as e:
#         logging.error(f"Unexpected error occurred: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="An unexpected error occurred while refreshing the token.",
#         )


# import logging
# import os
# import base64
# import hashlib
# import secrets
# import time

# from middleware import TokenRefreshMiddleware
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import RedirectResponse, JSONResponse
# from dotenv import load_dotenv
# from starlette.datastructures import URL
# from starlette.middleware.sessions import SessionMiddleware
# import httpx
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware

# # Load environment variables from .env file
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI()

# # ✅ Add TokenRefreshMiddleware first
# app.add_middleware(TokenRefreshMiddleware)

# # ✅ Add SessionMiddleware after so it executes first
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=secrets.token_hex(32),  # Replace with a fixed key in production
#     session_cookie="my_session",
#     same_site="lax",
#     https_only=False,  # Set to True if using HTTPS in production
# )

# # Add CORS middleware for cross-origin support (adjust in prod)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Set specific frontend domains in prod
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Environment config
# CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
# AUTH_URL = os.getenv("OAUTH_AUTH_URL")
# TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
# USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")
# REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
# LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")


# def generate_pkce_pair():
#     code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
#     code_challenge = (
#         base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
#         .decode("utf-8")
#         .rstrip("=")
#     )
#     return code_verifier, code_challenge


# @app.get("/")
# def home():
#     return {"message": "You're logged in!"}


# @app.get("/login")
# def login(request: Request):
#     code_verifier, code_challenge = generate_pkce_pair()
#     request.session["code_verifier"] = code_verifier

#     print("👉 Redirecting to Keycloak")
#     print("   code_verifier:", code_verifier)
#     print("   code_challenge:", code_challenge)

#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": REDIRECT_URI,
#         "scope": "openid profile email",
#         "code_challenge": code_challenge,
#         "code_challenge_method": "S256",
#     }

#     url = URL(AUTH_URL).include_query_params(**params)
#     return RedirectResponse(str(url))


# @app.get("/callback")
# async def callback(request: Request, code: str):
#     print("➡️ /callback hit with code:", code)

#     code_verifier = request.session.get("code_verifier")
#     if not code_verifier:
#         raise HTTPException(status_code=400, detail="Missing code_verifier")

#     print("🧪 Verifying PKCE flow with code_verifier:", code_verifier)

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(
#             TOKEN_URL,
#             data={
#                 "grant_type": "authorization_code",
#                 "client_id": CLIENT_ID,
#                 "code": code,
#                 "redirect_uri": REDIRECT_URI,
#                 "code_verifier": code_verifier,
#             },
#             headers={"Content-Type": "application/x-www-form-urlencoded"},
#         )

#     print("🔁 Token response status:", token_resp.status_code)

#     if token_resp.status_code != 200:
#         print("❌ Failed token exchange:", token_resp.text)
#         raise HTTPException(
#             status_code=token_resp.status_code, detail="Failed to retrieve token"
#         )

#     token_data = token_resp.json()
#     request.session["access_token"] = token_data.get("access_token")
#     request.session["refresh_token"] = token_data.get(
#         "refresh_token"
#     )  # Store refresh token
#     # Set expiry time
#     request.session["access_token_expires_at"] = time.time() + token_data["expires_in"]
#     print("✅ Token stored in session")

#     return RedirectResponse("http://localhost:3000")  # Adjust frontend URL if needed


# @app.get("/me")
# async def me(request: Request):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     # Ensure the access token is valid using middleware
#     current_time = time.time()
#     expires_at = request.session.get("access_token_expires_at")

#     if expires_at and current_time >= expires_at:
#         raise HTTPException(status_code=401, detail="Access token has expired")

#     async with httpx.AsyncClient() as client:
#         userinfo_resp = await client.get(
#             USERINFO_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#         )

#     if userinfo_resp.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     return JSONResponse(content=userinfo_resp.json())


# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     logout_redirect_uri = "http://localhost:3000"
#     logout_url = URL(LOGOUT_URL).include_query_params(redirect_uri=logout_redirect_uri)
#     return RedirectResponse(str(logout_url))


# class RefreshTokenInput(BaseModel):
#     refresh_token: str


# class TokenResponse(BaseModel):
#     access_token: str
#     expires_in: int
#     refresh_token: str
#     refresh_expires_in: int


# # Endpoint to refresh access token using refresh token
# @app.post("/refresh", response_model=TokenResponse)
# async def refresh_token(request: Request, input: RefreshTokenInput):
#     refresh_token = input.refresh_token or request.session.get("refresh_token")

#     if not refresh_token:
#         raise HTTPException(status_code=400, detail="Missing refresh_token")

#     data = {
#         "grant_type": "refresh_token",
#         "refresh_token": refresh_token,
#         "client_id": CLIENT_ID,
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(TOKEN_URL, data=data, headers=headers)

#         # Check for successful response
#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code, detail=response.json()
#             )

#         # Parse the new token data
#         token_data = response.json()

#         # Store new tokens in the session
#         request.session["access_token"] = token_data.get("access_token")
#         request.session["refresh_token"] = token_data.get("refresh_token")
#         # Update expiry time
#         request.session["access_token_expires_at"] = (
#             time.time() + token_data["expires_in"]
#         )

#         return token_data

#     except httpx.HTTPStatusError as e:
#         logging.error(f"HTTP error occurred: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="An error occurred while attempting to refresh the token.",
#         )

#     except Exception as e:
#         logging.error(f"Unexpected error occurred: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="An unexpected error occurred while refreshing the token.",
#         )


# import os
# import base64
# import hashlib
# import secrets
# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import RedirectResponse, JSONResponse
# from starlette.middleware.sessions import SessionMiddleware
# import httpx
# from dotenv import load_dotenv
# from starlette.datastructures import URL
# from fastapi.middleware.cors import CORSMiddleware

# load_dotenv()

# app = FastAPI()
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=secrets.token_hex(32),
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Environment variables
# CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
# AUTH_URL = os.getenv("OAUTH_AUTH_URL")
# TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
# USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")
# REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
# LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")


# def generate_pkce_pair():
#     code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
#     code_challenge = (
#         base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
#         .decode("utf-8")
#         .rstrip("=")
#     )
#     return code_verifier, code_challenge


# @app.get("/")
# def home():
#     return {"message": "You're logged in!"}


# @app.get("/login")
# def login(request: Request):
#     code_verifier, code_challenge = generate_pkce_pair()
#     request.session["code_verifier"] = code_verifier
#     print("👉 REDIRECT_URI:", REDIRECT_URI)
#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": "http://localhost:8000/callback",
#         "scope": "openid profile email",
#         "code_challenge": code_challenge,
#         "code_challenge_method": "S256",
#     }

#     url = URL(AUTH_URL).include_query_params(**params)
#     return RedirectResponse(str(url))


# @app.get("/callback")
# async def callback(request: Request, code: str):
#     print("➡️ /callback hit with code:", code)
#     code_verifier = request.session.get("code_verifier")
#     print("🧪 code_verifier from session:", code_verifier)
#     if not code_verifier:
#         raise HTTPException(status_code=400, detail="Missing code_verifier")

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(
#             TOKEN_URL,
#             data={
#                 "grant_type": "authorization_code",
#                 "client_id": CLIENT_ID,
#                 "code": code,
#                 "redirect_uri": REDIRECT_URI,
#                 "code_verifier": code_verifier,
#             },
#             headers={"Content-Type": "application/x-www-form-urlencoded"},
#         )
#     print("🔁 token_resp status:", token_resp.status_code)
#     print("🔐 token_resp content:", token_resp.text)
#     token_data = token_resp.json()
#     request.session["access_token"] = token_data.get("access_token")
#     return RedirectResponse("http://localhost:3000")


# @app.get("/me")
# async def me(request: Request):
#     print("Session data:", request.session)
#     access_token = request.session.get("access_token")
#     if not access_token:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     async with httpx.AsyncClient() as client:
#         userinfo_resp = await client.get(
#             USERINFO_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#         )

#     return JSONResponse(content=userinfo_resp.json())


# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     logout_redirect_uri = "http://localhost:3000"  # Where to go after logout
#     logout_url = URL(LOGOUT_URL).include_query_params(redirect_uri=logout_redirect_uri)
#     return RedirectResponse(str(logout_url))
