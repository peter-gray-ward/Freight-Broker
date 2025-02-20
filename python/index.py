from fastapi import FastAPI, Depends, HTTPException, Request, Response
from contextlib import asynccontextmanager
import bcrypt
import jwt
from uuid import uuid4
from datetime import datetime, timedelta
import json
import asyncio

from models import UserRegister, FreightSchedule, ShipmentRequest, Order
from security import create_jwt_token, verify_token, verify_role, hash_password
from startup import connect_db, load_stored_procedures
from data.simulation import setup_users, move_freighters, generate_shipments


print('Python Backend API for "Freight Broker" application')


@asynccontextmanager
async def lifespan(app: FastAPI):
	await load_stored_procedures()

	# simulation
	asyncio.create_task(setup_users())
	# asyncio.create_task(move_freighters())
	# asyncio.create_taslk(generate_shipments())

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


# ==============================
# ✅ Freighter Schedules
# ==============================

@app.post("/freighters/schedules", dependencies=[Depends(verify_role("Freighter"))])
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

@app.get("/freighters/schedules", dependencies=[Depends(verify_token)])
async def get_freighter_schedules():
    conn = await connect_db()
    schedules = await conn.fetch("SELECT * FROM get_all_freighter_schedules()")
    await conn.close()
    return schedules

@app.put("/freighters/schedules/{id}", dependencies=[Depends(verify_role("Freighter"))])
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

@app.post("/shipments/requests", dependencies=[Depends(verify_role("Client"))])
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

@app.get("/shipments/matches/{request_id}", dependencies=[Depends(verify_role("Client"))])
async def get_shipment_matches(request_id: str):
    conn = await connect_db()
    matches = await conn.fetch("SELECT * FROM get_shipment_matches($1)", request_id)
    await conn.close()
    return matches

# ==============================
# ✅ Orders
# ==============================

@app.post("/orders", dependencies=[Depends(verify_role("Client"))])
async def place_order(request: Request):
    body = await request.json()
    conn = await connect_db()

    new_order = await conn.fetch(
        "SELECT * FROM insert_order($1, $2, $3, $4)",
        body["client_id"], body["shipment_request_id"], body["freighter_schedule_id"], body["status"]
    )

    await conn.close()
    return new_order[0]

@app.get("/orders/{order_id}", dependencies=[Depends(verify_role("Client"))])
async def get_order(order_id: str):
    conn = await connect_db()
    order = await conn.fetch("SELECT * FROM get_order($1)", order_id)
    await conn.close()
    return order[0] if order else None
