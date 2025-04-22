import os
import base64
import hashlib
import secrets
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx
from dotenv import load_dotenv
from starlette.datastructures import URL
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
AUTH_URL = os.getenv("OAUTH_AUTH_URL")
TOKEN_URL = os.getenv("OAUTH_TOKEN_URL")
USERINFO_URL = os.getenv("OAUTH_USERINFO_URL")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode("utf-8")
        .rstrip("=")
    )
    return code_verifier, code_challenge


@app.get("/")
def home():
    return {"message": "You're logged in!"}


@app.get("/login")
def login(request: Request):
    code_verifier, code_challenge = generate_pkce_pair()
    request.session["code_verifier"] = code_verifier
    print("👉 REDIRECT_URI:", REDIRECT_URI)
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/callback",
        "scope": "openid profile email",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    url = URL(AUTH_URL).include_query_params(**params)
    return RedirectResponse(str(url))


@app.get("/callback")
async def callback(request: Request, code: str):
    print("➡️ /callback hit with code:", code)
    code_verifier = request.session.get("code_verifier")
    print("🧪 code_verifier from session:", code_verifier)
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
    print("🔁 token_resp status:", token_resp.status_code)
    print("🔐 token_resp content:", token_resp.text)
    token_data = token_resp.json()
    request.session["access_token"] = token_data.get("access_token")
    return RedirectResponse("http://localhost:3000")


@app.get("/me")
async def me(request: Request):
    print("Session data:", request.session)
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return JSONResponse(content=userinfo_resp.json())


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    logout_redirect_uri = "http://localhost:3000"  # Where to go after logout
    logout_url = URL(LOGOUT_URL).include_query_params(redirect_uri=logout_redirect_uri)
    return RedirectResponse(str(logout_url))
