import asyncio
import random
import aiohttp
from datetime import datetime, timedelta
import uuid
import traceback

day_length = 10

# Backend API URL
BASE_URL = "http://localhost:8000"

CITIES = [
    ("New York", 40.712784, -74.005941),
    ("Los Angeles", 34.052234, -118.243685),
    ("Chicago", 41.878114, -87.629798),
    ("Houston", 29.760427, -95.369803),
    ("Phoenix", 33.448377, -112.074037),
    ("Philadelphia", 39.952584, -75.165222),
    ("San Antonio", 29.424122, -98.493628),
    ("San Diego", 32.715738, -117.161084),
    ("Dallas", 32.776664, -96.796988),
    ("San Jose", 37.338208, -121.886329),
    ("Austin", 30.267153, -97.743061),
    ("Jacksonville", 30.332184, -81.655651),
    ("Fort Worth", 32.755488, -97.330766),
    ("Columbus", 39.961176, -82.998794),
    ("Indianapolis", 39.768403, -86.158068),
    ("Charlotte", 35.227087, -80.843127),
    ("San Francisco", 37.774929, -122.419416),
    ("Seattle", 47.606209, -122.332071),
    ("Denver", 39.739236, -104.990251),
    ("Washington", 38.907192, -77.036871)
]

ADMIN = {
    "name": "Peter",
    "email": "peterward.pgw@gmail.com",
    "password": "enter",
    "role": "Admin"
}

FREIGHTERS = []

for i in range(20):
    current_city = random.choice(CITIES)
    uid = str(uuid.uuid4())
    FREIGHTERS.append(
        {
            "userid": uid,  # Unique Freighter ID
            "freighterid": uid,
            "name": f"Freighter {i+1}",
            "email": f"freighter{i+1}@test.com",
            "password": "securepass123",
            "maxloadkg": random.randint(10000, 50000),
            "availablekg": random.randint(5000, 25000),
            "departurecity": current_city[0],
            "arrivalcity": None,
            "departurelat": current_city[1],
            "departurelng": current_city[2],
            "arrivallat": None,
            "arrivallng": None,
            "departuredate": None,
            "arrivaldate": None,
            "scheduleid": str(uuid.uuid4()),  # Unique schedule ID
            "status": "Available",  # Can be: Available, In Transit, Completed
            "lastupdated": str(datetime.utcnow()),
            "role": "Freighter"
        }
    )

# 11 Suppliers (Clients)
SUPPLIERS = [
    {
        "userid": uuid.uuid4(),
        "name": f"Supplier {i+1}",
        "email": f"supplier{i+1}@test.com",
        "password": "securepass123",
        "role": "Supplier"
    }
    for i in range(11)
]

# Track active user sessions
ACTIVE_SESSIONS = {}  # {userid: expiration_time}


async def get_access_token(session, email, password, name, role):
    login_url = f"{BASE_URL}/users/login"
    register_url = f"{BASE_URL}/users/register"

    async with session.post(login_url, json={"name": name, "email": email, "password": password}) as resp:
        if resp.status == 200:
            data = await resp.json()
            print(f"✅ Logged in: {name}")
            return data["userid"], data["name"], data["email"], data["role"]

    async with session.post(register_url, json={"name": name, "email": email, "password": password, "role": role}) as resp:
        if resp.status == 200:
            data = await resp.json()
            print(f"✅ Registered: {name}")
            return data["userid"], data["name"], data["email"], data["role"]

    print(f"❌ Registration failed for {name}: {await resp.text()}")
    return None


async def simulate(session, user, resp):
    data = await resp.json()
    ACTIVE_SESSIONS[user["userid"]] = resp.cookies.get("fb_access_token").value

    if data['role'] == 'Supplier':
        await generate_shipment(data)
    elif data['role'] == 'Freighter':
        await update_freighter_schedule(data)

    await asyncio.sleep(day_length)


async def handle_user_session(session, user):
    await asyncio.sleep(random.randint(int(day_length / 10), day_length))  # Random start time in the "day"   

    async with session.post(f"{BASE_URL}/users/login", json={
        "name": user["name"], "email": user["email"], "password": user["password"]
    }) as resp:
        if resp.status == 200:
            print(f"🔓 {user['name']} logged in.")
            await simulate(session, user, resp)
            await logout(session, user)
        else:
            async with session.post(f"{BASE_URL}/users/register", json={
                "userid": str(user["userid"]), "name": user["name"], "email": user["email"], "password": user["password"], "role": user["role"]
            }) as resp:
                if resp.status == 200:
                    print(f"🔓 {user['name']} registered.")
                    await simulate(session, user, resp)
                    await logout(session, user)


async def logout(session, user):
    try:
        headers = {"Authorization": f"Bearer {ACTIVE_SESSIONS[user['userid']]}"}  # Token from login

        async with session.post(f"{BASE_URL}/users/logout", headers=headers) as logout_resp:
            if logout_resp.status == 200:
                print(f"🔒 {user['name']} logged out.")
                del ACTIVE_SESSIONS[user["userid"]]
            else:
                print(f"⚠️ Logout failed for {user['name']}: {await logout_resp.text()}")
    except aiohttp.ClientError as e:
        print(f"⚠️ Server error during logout ({user['name']}): {e}")

async def manage_sessions():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/users/register", json=ADMIN) as resp:
            day = 1
            while True:
                try:
                    print(f"\n⏳ Day {day} starting...")
                    users = FREIGHTERS + SUPPLIERS
                    random.shuffle(users)

                    tasks = [asyncio.create_task(handle_user_session(session, user)) for user in users]
                    await asyncio.gather(*tasks) 

                    print(f"\n🔄 Day {day} complete. Waiting for next cycle...\n")
                    day += 1

                except Exception as e:
                    print(f"❌ ERROR in manage_sessions() on Day {day}: {e}")
                    traceback.print_exc()

                await asyncio.sleep(1)  # Simulate next "day" cycle


async def generate_shipment(supplier):
    origin_city = random.choice(CITIES)
    destination_city = random.choice([city for city in CITIES if city != origin_city])
    weight_kg = random.randint(500, 5000)

    print(f"📦 {supplier['name']} shipping {weight_kg}kg {origin_city} → {destination_city}")

    shipment_data = {
        "clientid": supplier["userid"],
        "origincity": origin_city[0],
        "originlat": origin_city[1],
        "originlng": origin_city[2],
        "destinationcity": destination_city[0],
        "destinationlat": destination_city[1],
        "destinationlng": destination_city[2],
        "weightkg": weight_kg,
        "specialhandling": None,
        "status": "Pending"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/shipments/requests", json=shipment_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data:
                    print(f"📦 Shipment created: {supplier['name']}")
            else:
                print(f"❌ Failed shipment {supplier['name']}: {await resp.text()}")


async def update_freighter_schedule(user):
    freighter = None
    for f in FREIGHTERS:
        if f["userid"] == user["userid"]:
            freighter = f
    if freighter:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/freighters/schedules", json=freighter) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        print(f"🕒 Schedule Updated: {freighter['name']}")
                else:
                    print(f"❌ Failed schedule update {freighter['name']}: {await resp.text()}")
    else:
        raise Exception("failed freighter user id match...")
