from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, Security
from contextlib import asynccontextmanager
import bcrypt
import jwt
from uuid import uuid4
from datetime import datetime, timedelta
import json
import asyncio
from typing import Annotated

from models import User, UserRegister, FreightSchedule, ShipmentRequest, Order
from security import create_jwt_token, verify_token, verify_role, hash_password, verify_admin
from startup import connect_db, load_stored_procedures
from data.simulation import setup_users, move_freighters, generate_shipments, manage_sessions
from fastapi.middleware.cors import CORSMiddleware



print('Python Backend API for "Freight Broker" application')

active_connections = set()
active_users = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
	await load_stored_procedures()

	# simulation
	asyncio.create_task(manage_sessions())
	# asyncio.create_task(move_freighters())
	# asyncio.create_taslk(generate_shipments())

	yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  # Next.js local development
    "https://your-production-domain.com",  # Add your deployed frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific frontend domains
    allow_credentials=True,  # Allow cookies & authentication
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.websocket("/ws")  # ✅ Use raw WebSocket (not `/socket.io`)
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print("Client connected!")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")

            message = json.loads(json)


            for connection in active_connections:
                await connection.send_text(json.dumps(message))

    except WebSocketDisconnect:
        print("Client disconnected!")
        active_connections.remove(websocket)

async def alert_user_connect(user, which):
    print("alert user connect ---- ", user)
    if which == 'login':
        active_users.add(user)
    else:
        active_users.remove(user)

    message = json.dumps({ "type": "user_" + which, "payload": user.dict() })
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message {e}")

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

    

    connected_user = {
        "userid": str(user_data["userid"]),
        "name": user_data["name"],
        "email": user_data["email"],
        "role": user_data["role"]
    }

    user = User(**connected_user)

    if user not in active_users:
        await alert_user_connect(user, 'login')

    return connected_user

@app.post("/users/logout")
async def logout(request: Request):
    user = verify_token(request)

    print('/users/logout', user)

    await alert_user_connect(User(**user), 'logout')

@app.get("/secure-data-test")
async def security_test(request: Request):
    user = verify_role(request, "Admin")
    return {"message": "Access granted to secure data"}

@app.get("/active-users")
def get_active_users(request: Request):
    user = verify_role(request, "Admin")
    return active_users

# ==============================
# ✅ Freighter Schedules
# ==============================

@app.post("/freighters/schedules")
async def post_freighter_schedule(request: Request):
    body = await request.json()
    conn = await connect_db()

    new_schedule = await conn.fetch(
        "SELECT * FROM insert_freighter_schedule($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        body["freighter_id"], body["departure_city"], body["departure_lat"], body["departure_lon"],
        body["arrival_city"], body["arrival_lat"], body["arrival_lon"],
        body["departure_date"], body["arrival_date"]
    )

    await conn.close()
    return new_schedule[0]

@app.get("/freighters/schedules")
async def get_freighter_schedules():
    conn = await connect_db()
    schedules = await conn.fetch("SELECT * FROM get_all_freighter_schedules()")
    await conn.close()
    return schedules

@app.put("/freighters/schedules/{id}")
async def update_freighter_schedule(id: str, request: Request):
    body = await request.json()
    conn = await connect_db()

    updated_schedule = await conn.fetch(
        "SELECT * FROM update_freighter_schedule($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        id, body["freighter_id"], body["departure_city"], body["departure_lat"], body["departure_lon"],
        body["arrival_city"], body["arrival_lat"], body["arrival_lon"],
        body["departure_date"], body["arrival_date"]
    )

    await conn.close()
    return updated_schedule[0]

# ==============================
# ✅ Shipment Requests
# ==============================

@app.post("/shipments/requests")
async def post_shipment_request(request: Request):
    body = await request.json()
    conn = await connect_db()

    new_request = await conn.fetch(
        "SELECT * FROM insert_shipment_request($1, $2, $3, $4, $5, $6, $7)",
        body["client_id"], body["origin_city"], body["origin_lat"], body["origin_lon"],
        body["destination_city"], body["destination_lat"], body["destination_lon"]
    )

    await conn.close()
    return new_request[0]

@app.get("/shipments/matches/{request_id}")
async def get_shipment_matches(request_id: str):
    conn = await connect_db()
    matches = await conn.fetch("SELECT * FROM get_shipment_matches($1)", request_id)
    await conn.close()
    return matches

# ==============================
# ✅ Orders
# ==============================

@app.post("/orders")
async def place_order(request: Request):
    body = await request.json()
    conn = await connect_db()

    new_order = await conn.fetch(
        "SELECT * FROM insert_order($1, $2, $3, $4)",
        body["client_id"], body["shipment_request_id"], body["freighter_schedule_id"], body["status"]
    )

    await conn.close()
    return new_order[0]

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    conn = await connect_db()
    order = await conn.fetch("SELECT * FROM get_order($1)", order_id)
    await conn.close()
    return order[0] if order else None
