from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect, Security, Query
from contextlib import asynccontextmanager
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import json
import asyncio
from typing import Annotated, Optional

from models import User, UserRegister, FreighterSchedules, ShipmentRequests, ShipmentMatches
from security import create_jwt_token, verify_token, verify_role, hash_password, verify_admin
from startup import connect_db, load_stored_procedures
from data.simulation import manage_sessions, move_freighters_toward_destination
from fastapi.middleware.cors import CORSMiddleware
from service import match_freighters_to_shipments_async


print('Python Backend API for "Freight Broker" application')

active_connections = set()
active_users = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_stored_procedures()

    print("LOADED STORED PROCEDURES")

    # Start the session management task (runs forever)
    loop = asyncio.get_event_loop()
    loop.create_task(manage_sessions())
    loop.create_task(match_freighters_to_shipments_async())
    loop.create_task(move_freighters_toward_destination())
    loop.create_task(send_match_updates())

    yield  # FastAPI continues running while this task runs in the background



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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    # print("Client connected!")

    try:
        while True:
            data = await websocket.receive_text()
            # print(f"Received: {data}")

            message = json.loads(json)


            for connection in active_connections:
                await connection.send_text(json.dumps(message))

    except WebSocketDisconnect:
        # print("Client disconnected!")
        active_connections.remove(websocket)

async def alert_user_connect(user, which):
    if which == 'login':
        active_users.add(user)
    elif user in active_users:
        active_users.remove(user)

    message = json.dumps({ "type": "user_" + which, "payload": user.dict() })
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message {e}")


async def alert_shipment(shipments):
    shipments = [
        {
            **s.dict(),
            "createdat": str(s.createdat),
            "lastupdated": str(s.lastupdated),
        }
        for s in shipments
    ]

    message = json.dumps({ "type": "shipment_update", "payload": shipments })
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message {e}")

async def alert_schedule(schedules):
    schedules = [
        {
            **s.dict(),
            "departurelat": float(s.departurelat),
            "departurelng": float(s.departurelng),
            "arrivallat": float(s.arrivallat) if s.arrivallat else "",
            "arrivallng": float(s.arrivallng) if s.arrivallng else "",
            "maxloadkg": float(s.maxloadkg),
            "availablekg": float(s.availablekg)
        }
        for s in schedules
    ]
    message = json.dumps({ "type": "freighter_update", "payload": schedules })
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message {e}")

async def alert_matches(matches):
    matches = list(map(lambda s: s.dict(), matches))
    message = json.dumps({ "type": "match_update", "payload": matches })
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Failed to send message {e}")

async def send_match_updates():
    conn = await connect_db()
    matches = await conn.fetch("SELECT * FROM get_shipment_matches()")
    await conn.close()
    await alert_matches(matches)

register_tokens = dict()

@app.post("/users/register")
async def register(request: Request, response: Response):
    body = await request.json()
    userid = body.get("userid", None)
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

    new_user = []

    if userid:
        new_user = await conn.fetch("SELECT * FROM insert_user_with_id($1, $2, $3, $4, $5)", uuid.UUID(userid), name, email, password_hash, role)
    else:
        new_user = await conn.fetch("SELECT userid, name, role, email FROM insert_user($1, $2, $3, $4)", name, email, password_hash, role)

    if (len(new_user) < 1):
        raise HTTPException(status_code=500, detail=f"Internal Server Error")

    new_user = new_user[0]

    uid = str(new_user["userid"])

    access_token = create_jwt_token(
        data={"userid": uid, "name": new_user["name"], "role": new_user["role"]},
        expires_delta=timedelta(minutes=30)
    )

    register_tokens[uid] = access_token

    response.set_cookie(
        key="fb_access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=30 * 60
    )

    await conn.close()

    user = user = User(**{
        "userid": str(new_user["userid"]),
        "name": new_user["name"],
        "email": new_user["email"],
        "role": new_user["role"]
    })

    if user not in active_users:
        await alert_user_connect(user, 'login')

    return {
        "userid": new_user["userid"], 
        "name": new_user["name"], 
        "email": new_user["email"], 
        "role": new_user["role"]
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

    uid = str(user_data["userid"])

    access_token = register_tokens[uid] if uid in register_tokens else create_jwt_token(
        data={"userid": uid, "name": user_data["name"], "role": user_data["role"]},
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

    departuredate = datetime.strptime(body["departuredate"], "%Y-%m-%d %H:%M:%S.%f") if body["departuredate"] else None
    arrivaldate = datetime.strptime(body["arrivaldate"], "%Y-%m-%d %H:%M:%S.%f") if body["arrivaldate"] else None
    freighterid = body["freighterid"]
    departurelat = body["departurelat"]
    departurelng = body["departurelng"]

    current_departure = await conn.fetch(
        """
            SELECT departurelat, departurelng
            FROM freighterschedules
            WHERE freighterid = $1
        """,
        freighterid
    )

    if not len(current_departure):
        current_departure = None
    else:
        current_departure = current_departure[0]

    if not current_departure or float(current_departure["departurelat"]) != departurelat or float(current_departure["departurelng"]) != departurelng:

        has_schedule = await conn.fetch("SELECT 1 FROM freighterschedules WHERE freighterid = $1", body["freighterid"])

        new_schedule = await conn.fetch(
            "SELECT * FROM " + ("insert" if len(has_schedule) == 0 else "update") + "_freighter_schedule($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
            body["freighterid"], body["departurecity"], body["departurelat"], body["departurelng"],
            body["arrivalcity"], body["arrivallat"], body["arrivallng"],
            departuredate, arrivaldate, body["maxloadkg"], body["availablekg"], body["status"]
        )


        schedules = await conn.fetch("""SELECT * FROM freighterschedules""")

        await conn.close()

        await alert_schedule([
            FreighterSchedules(**{
                "scheduleid": str(s["scheduleid"]),
                "freighterid": str(s["freighterid"]),
                "departurecity": s["departurecity"],
                "departurelat": float(s["departurelat"]),
                "departurelng": float(s["departurelng"]),
                "arrivalcity": s["arrivalcity"],
                "arrivallat": s["arrivallat"],
                "arrivallng": s["arrivallng"],
                "departuredate": s["departuredate"],
                "arrivaldate": s["arrivaldate"],
                "maxloadkg": float(s["maxloadkg"]),
                "availablekg": float(s["availablekg"]),
                "status": s.get("status", "Available")  # Default status to "Available"
            }) for s in schedules
        ])

        return new_schedule[0]
    return None

@app.get("/freighters/schedules")
async def get_freighter_schedules():
    conn = await connect_db()
    schedules = await conn.fetch("SELECT * FROM get_all_freighter_schedules()")
    await conn.close()
    return schedules

# ==============================
# ✅ Shipment Requests
# ==============================

@app.get("/shipments/requests")
async def get_shipment_request(request_id: Optional[str] = Query(None)):
    conn = await connect_db()

    if request_id:
        requests = await conn.fetch(
            "SELECT * FROM shipmentrequests WHERE requestid = $1", request_id
        )
    else:
        requests = await conn.fetch("SELECT * FROM shipmentrequests")

    await conn.close()
    return requests


@app.post("/shipments/requests")
async def post_shipment_request(request: Request):
    body = await request.json()
    conn = await connect_db()

    requestid = body.get("requestid", uuid.uuid4())

    has_shipment = await conn.fetch("SELECT 1 FROM shipmentrequests WHERE requestid = $1", requestid)

    new_request = await conn.fetch(
        "SELECT * FROM " + ("insert" if len(has_shipment) == 0 else "update") + "_shipment_request($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
        requestid, body["clientid"], body["origincity"], body["originlat"], body["originlng"],
        body["destinationcity"], body["destinationlat"], body["destinationlng"],
        body["weightkg"], body["specialhandling"], body["status"]
    )

    requests = await conn.fetch("""SELECT * FROM shipmentrequests""")

    await conn.close()


    await alert_shipment([
        ShipmentRequests(**{
            "requestid": str(s["requestid"]),  # Ensure correct field names
            "clientid": str(s["clientid"]),  # Ensure client_id is correctly mapped
            "origincity": s["origincity"],
            "originlat": float(s["originlat"]),
            "originlng": float(s["originlng"]),
            "destinationcity": s["destinationcity"],
            "destinationlat": float(s["destinationlat"]),
            "destinationlng": float(s["destinationlng"]),
            "weightkg": float(s["weightkg"]),
            "specialhandling": "none",  # Optional field
            "status": s["status"],
            "createdat": s["createdat"],
            "lastupdated": s["lastupdated"],
        }) for s in requests
    ])


    return new_request[0]

@app.get("/shipments/matches")
async def get_shipment_matches():
    conn = await connect_db()
    matches = await conn.fetch("SELECT * FROM shipmentmatches")
    await conn.close()
    return matches



