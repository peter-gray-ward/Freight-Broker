import bcrypt
import jwt
from uuid import uuid4
from datetime import datetime, timedelta
import os
import json
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "env.json"))

with open(env_path, 'r') as file:
    env = json.load(file)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secret = env["jwt"]["secret"]
algorithm = env["jwt"]["algorithm"]

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm=algorithm)

def verify_token(request: Request, token: str = Depends(oauth2_scheme)):
    jwt_token = request.cookies.get("access_token")

    if not jwt_token:
        jwt_token = token

    if not jwt_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(jwt_token, secret, algorithms=[algorithm])
        return payload  # ✅ Valid token, return payload (user data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_role(required_role: str):
	def role_checker(payload: dict = Depends(verify_token)):
		if payload.get("role") != required_role:
			raise HTTPException(status_code=403, detail="Not enough permissions")
		return payload
	return role_checker

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

