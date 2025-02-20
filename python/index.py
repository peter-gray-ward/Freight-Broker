from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import bcrypt
import jwt
from uuid import uuid4
from datetime import datetime, timedelta
from models import UserRegister, FreightSchedule, ShipmentRequest, Order
import asyncpg
import json
import asyncio
import os

print('Python Backend API for "Freight Broker" application')


env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "env.json"))
schemas_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schemas.sql"))
stored_procedure_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stored-procedures"))
with open(env_path, 'r') as file:
	env = json.load(file)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
secret = env["jwt"]["secret"]
algorithm = env["jwt"]["algorithm"]



async def connect_db():
    return await asyncpg.connect(
        user=env["db"]["username"],
        port=env["db"]["port"],
        password=env["db"]["password"],
        database=env["db"]["database"],
        host=env["db"]["host"]
    )

async def load_stored_procedures():
    conn = await connect_db()

    with open(schemas_path, 'r', encoding="utf-8") as schemas_sql:
    	try:
    		await conn.execute(schemas_sql.read().strip())
    		print(f"Executed: {schemas_path}")
    	except Exception as e:
    		print(f"Error processing schemas.sql")
    
    for file_name in os.listdir(stored_procedure_directory):
        file_path = os.path.join(stored_procedure_directory, file_name)

        if file_name.endswith(".sql"):
            with open(file_path, 'r', encoding="utf-8") as sql_file:
                sql_content = sql_file.read().strip()
                try:
                    await conn.execute(sql_content)
                    print(f"Executed: {file_name}")
                except Exception as e:
                    print(f"Error executing {file_name}: {e}")

    await conn.close()

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_stored_procedures()
    yield

app = FastAPI(lifespan=lifespan)





@app.post("/users/register")
async def register(request: Request, response: Response):
	body = await request.json()
	name = body["name"]
	email = body["email"]
	password = body["password"]
	role = body.get("role", "Client")

	conn = await connect_db()
	
	existing_user = await conn.fetch("SELECT * FROM get_user_by_name($1)", name)

	if existing_user:
		await conn.close()
		raise HTTPException(status_code=500, detail=f"User {name} already exists")

	password_hash = hash_password(password)

	new_user = await conn.fetch("SELECT * FROM insert_user($1, $2, $3, $4)", name, email, password_hash, role)

	await conn.close()
	return {
		"userid": new_user[0]["userid"], 
		"name": new_user[0]["name"], 
		"email": new_user[0]["email"], 
		"role": new_user[0]["role"]
	}


@app.post("/users/login")
async def login(request: Request, response: Response):
    body = await request.json()
    name = body["name"]
    password = body["password"]

    conn = await connect_db()

    existing_user = await conn.fetch("SELECT * FROM get_user_by_name($1)", name)

    if not existing_user:
        await conn.close()
        raise HTTPException(status_code=400, detail=f"User {name} doesn't exist.")

    user_data = existing_user[0]
    stored_hashed_password = user_data["passwordhash"]

    if not bcrypt.checkpw(password.encode(), stored_hashed_password.encode()):
        await conn.close()
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_jwt_token(
        data={"userid": str(user_data["userid"]), "name": user_data["name"], "role": user_data["role"]},
        expires_delta=timedelta(minutes=30)
    )

    response.set_cookie(
        key="fb_access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=30 * 60
    )

    await conn.close()

    print('user ' + name + ' has LOGGED IN', user_data)

    return {
        "userid": str(user_data["userid"]),
        "name": user_data["name"],
        "email": user_data["email"],
        "role": user_data["role"]
    }



@app.get("/secure-data-test", dependencies=[Depends(verify_token)])
async def security_test():
	return {"message": "Access granted to secure data"}

