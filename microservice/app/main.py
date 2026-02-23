
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3
import os

from db import init_db
from auth import create_token, verify_token, verify_password

app = FastAPI()
security = HTTPBearer()
DB_PATH = os.getenv("DB_PATH", "/data/sqlite.db")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
def login(payload: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (payload["username"],))
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(payload["password"], row[0]):
        return {"token": create_token(payload["username"])}
    raise HTTPException(status_code=401)

@app.get("/verify")
def verify_public():
    return {"message": "public verify endpoint"}

@app.get("/users")
def get_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    decoded = verify_token(token)
    if not decoded:
        raise HTTPException(status_code=401)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()

    return {"users": users}
