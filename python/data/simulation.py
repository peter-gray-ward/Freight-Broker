import asyncio
import random
import aiohttp
from datetime import datetime, timedelta

day_length = 10

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
    - Logs in → Waits 10s → Logs out (with retry on failure).
    - Handles server disconnections gracefully.
    """
    await asyncio.sleep(random.randint(1, 60))  # Random start time in the "day"   

    async with aiohttp.ClientSession() as session:
        # Log in user
        async with session.post(f"{BASE_URL}/users/login", json={
            "name": user["name"], "email": user["email"], "password": user["password"]
        }) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"🔓 {user['name']} logged in.", data)
                ACTIVE_SESSIONS[user["userid"]] = resp.cookies.get("fb_access_token").value

                if data['role'] == 'Client':
                    await generate_shipment(data)

                # Stay logged in for 10s
                await asyncio.sleep(10)

                # Log out user (retry up to 3 times)
                for attempt in range(3):
                    try:
                        headers = {"Authorization": f"Bearer {ACTIVE_SESSIONS[user['userid']]}"}  # Token from login
                        async with session.post(f"{BASE_URL}/users/logout", headers=headers) as logout_resp:
                            if logout_resp.status == 200:
                                print(f"🔒 {user['name']} logged out.")
                                del ACTIVE_SESSIONS[user["userid"]]
                                break  # Success, exit retry loop
                            else:
                                print(f"⚠️ Logout failed for {user['name']}: {await logout_resp.text()}")
                    except aiohttp.ClientError as e:
                        print(f"⚠️ Server error during logout ({user['name']}): {e}")

                    if attempt < 2:  # Only wait before retrying if not the last attempt
                        await asyncio.sleep(3)  # Wait before retrying




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

            await move_freighters()

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
    for freighter in FREIGHTERS:
        new_city = random.choice([city for city in CITIES if city != freighter["current_city"]])
        print(f"🚚 {freighter['name']} moving: {freighter['current_city']} → {new_city}")
        freighter["current_city"] = new_city



async def generate_shipment(supplier):
    """
    Simulates suppliers generating shipment requests.
    Only active users can generate shipments.
    """

    origin_city = random.choice(CITIES)
    destination_city = random.choice([city for city in CITIES if city != origin_city])
    weight_kg = random.randint(500, 5000)

    print(f"📦 {supplier['name']} shipping {weight_kg}kg {origin_city} → {destination_city}")

    shipment_data = {
        "clientid": supplier["userid"],
        "origincity": origin_city,
        "originlat": random.uniform(30.0, 50.0),
        "originlng": random.uniform(-120.0, -70.0),
        "destinationcity": destination_city,
        "destinationlat": random.uniform(30.0, 50.0),
        "destinationlng": random.uniform(-120.0, -70.0),
        "weightkg": weight_kg,
        "specialhandling": None,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/shipments/requests", json=shipment_data) as resp:
            if resp.status == 200:
                print(f"✅ Shipment created: {supplier['name']}")
            else:
                print(f"❌ Failed shipment {supplier['name']}: {await resp.text()}")


