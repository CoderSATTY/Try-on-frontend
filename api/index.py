from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import backend_utils as backend

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    name: str

class VerifyRequest(BaseModel):
    email: str
    code: str

@app.post("/api/login")
async def api_login(req: LoginRequest):
    success, msg = backend.register_user(req.email, req.name)
    return {"success": success, "message": msg}

@app.post("/api/verify")
async def api_verify(req: VerifyRequest):
    success, msg = backend.verify_code(req.email, req.code)
    return {"success": success, "message": msg}

# Mount Static Files (Login Page)
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")