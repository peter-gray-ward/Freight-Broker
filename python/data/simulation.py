import asyncio
import random
import aiohttp
from datetime import datetime, timedelta

day_length = 3

# Backend API URL
BASE_URL = "http://localhost:8000"

# 20 American cities for shipments
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Indianapolis",
    "Charlotte", "San Francisco", "Seattle", "Denver", "Washington"
]

# 20 Freighters
FREIGHTERS = [
    {
        "userid": f"freighter-{i+1}",
        "name": f"Freighter {i+1}",
        "email": f"freighter{i+1}@test.com",
        "password": "securepass123",
        "max_load_kg": random.randint(10000, 50000),
        "available_kg": random.randint(5000, 25000),
        "current_city": random.choice(CITIES) 
    }
    for i in range(20)
]

# 11 Suppliers (Clients)
SUPPLIERS = [
    {
        "userid": f"supplier-{i+1}",
        "name": f"Supplier {i+1}",
        "email": f"supplier{i+1}@test.com",
        "password": "securepass123"
    }
    for i in range(11)
]

# Track active user sessions
ACTIVE_SESSIONS = {}  # {userid: expiration_time}


async def get_access_token(session, email, password, name, role):
    """
    Attempts to log in. If login fails, registers the user first.
    Returns the user details.
    """
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


async def setup_users():
    """
    Registers all freighters and suppliers in the system.
    """
    async with aiohttp.ClientSession() as session:
        # Register freighters
        for freighter in FREIGHTERS:
            freighter["userid"], freighter["name"], freighter["email"], freighter["role"] = await get_access_token(
                session, freighter["email"], freighter["password"], freighter["name"], "Freighter"
            )

        # Register suppliers
        for supplier in SUPPLIERS:
            supplier["userid"], supplier["name"], supplier["email"], supplier["role"] = await get_access_token(
                session, supplier["email"], supplier["password"], supplier["name"], "Client"
            )


async def handle_user_session(user):
    """
    Manages the session for a single user.
    - Waits for a random time within the day (60s).
    - Logs in the user.
    - Waits for 10 seconds (active session).
    - Logs out the user.
    """
    await asyncio.sleep(random.randint(1, day_length))  # Random start time in the day

    async with aiohttp.ClientSession() as session:
        # Log in user
        async with session.post(f"{BASE_URL}/users/login", json={"name": user["name"], "password": user["password"]}) as resp:
            if resp.status == 200:
                data = await resp.json()

                ACTIVE_SESSIONS[user["userid"]] = resp.cookies.get("fb_access_token").value

                # Stay logged in for 10s
                await asyncio.sleep(day_length / 6)

                # Log out user
                headers = {"Authorization": f"Bearer {ACTIVE_SESSIONS[user["userid"]]}"}

                # print(".... logging out", headers)
                async with session.post(f"{BASE_URL}/users/logout", headers=headers) as logout_resp:
                    if logout_resp.status == 200:
                        # print(f"🔒 {user['name']} logged out.")
                        if user["userid"] in ACTIVE_SESSIONS:
                            del ACTIVE_SESSIONS[user["userid"]]
                    else:
                        print(f"⚠️ Logout failed for {user['name']}: {await logout_resp.text()}")


import traceback

async def manage_sessions():
    """
    Keeps running indefinitely. Ensures users log in and out once per cycle.
    Recovers from errors without stopping.
    """
    day = 1
    while True:
        try:
            print(f"\n⏳ Day {day} starting...")

            # Start login/logout tasks for all users
            tasks = [asyncio.create_task(handle_user_session(user)) for user in FREIGHTERS + SUPPLIERS]
            await asyncio.gather(*tasks)  # Wait for all users to log in/out

            print(f"\n🔄 Day {day} complete. Waiting for next cycle...\n")
            day += 1

        except Exception as e:
            print(f"❌ ERROR in manage_sessions() on Day {day}: {e}")
            traceback.print_exc()

        await asyncio.sleep(1)  # Simulate next "day" cycle



async def move_freighters():
    """
    Simulates freighters moving between cities.
    Only active users can move.
    """
    while True:
        for freighter in FREIGHTERS:
            if freighter["userid"] not in ACTIVE_SESSIONS:
                continue  

            new_city = random.choice([city for city in CITIES if city != freighter["current_city"]])
            print(f"🚚 {freighter['name']} moving: {freighter['current_city']} → {new_city}")
            freighter["current_city"] = new_city

        await asyncio.sleep(5)


async def generate_shipments():
    """
    Simulates suppliers generating shipment requests.
    Only active users can generate shipments.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            for supplier in SUPPLIERS:
                if supplier["userid"] not in ACTIVE_SESSIONS:
                    continue  

                origin_city = random.choice(CITIES)
                destination_city = random.choice([city for city in CITIES if city != origin_city])
                weight_kg = random.randint(500, 5000)

                print(f"📦 {supplier['name']} shipping {weight_kg}kg {origin_city} → {destination_city}")

                shipment_data = {
                    "client_id": supplier["userid"],
                    "origin_city": origin_city,
                    "origin_lat": random.uniform(30.0, 50.0),
                    "origin_lng": random.uniform(-120.0, -70.0),
                    "destination_city": destination_city,
                    "destination_lat": random.uniform(30.0, 50.0),
                    "destination_lng": random.uniform(-120.0, -70.0),
                    "weight_kg": weight_kg,
                    "special_handling": None,
                }

                async with session.post(f"{BASE_URL}/shipments/requests", json=shipment_data) as resp:
                    if resp.status == 200:
                        print(f"✅ Shipment created: {supplier['name']}")
                    else:
                        print(f"❌ Failed shipment {supplier['name']}: {await resp.text()}")

            await asyncio.sleep(5)

