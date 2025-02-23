import asyncio
import random
import aiohttp
from datetime import datetime, timedelta
import uuid
import time
import traceback
import math

DAY_LENGTH = 30
BASE_URL = "http://localhost:8000"
REAL_SPEED_KM_H = 50  # Real-world speed (50 km/h)
SECONDS_IN_REAL_DAY = 86400  # 24 hours * 3600 seconds
SIMULATION_SECONDS_PER_DAY = DAY_LENGTH  # 30 seconds in our simulation
SPEED_KM_PER_TICK = (REAL_SPEED_KM_H / 3600) * (SECONDS_IN_REAL_DAY / SIMULATION_SECONDS_PER_DAY)


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
            "status": "available",  # Can be: Available, In Transit, Completed
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


async def handle_user_session(session, user):
    await asyncio.sleep(random.randint(int(DAY_LENGTH / 10), DAY_LENGTH))  # Random start time in the "day"   

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
                start_time = time.monotonic()  # Start time for this day
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

                # Calculate how long the processing took and sleep for the remainder of the day.
                elapsed = time.monotonic() - start_time
                sleep_time = DAY_LENGTH - elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)


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
        "status": "pending"
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




def haversine(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points on the Earth in kilometers.
    """
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

import asyncio
import aiohttp
from datetime import datetime

async def move_freighters_toward_destination():
    async with aiohttp.ClientSession() as session:
        while True:
            # Retrieve all freighter schedules
            async with session.get(f"{BASE_URL}/freighters/schedules") as resp:
                if resp.status != 200:
                    print("Failed to get freighter schedules")
                    await asyncio.sleep(1)
                    continue
                schedules = await resp.json()

            # Retrieve all shipment matches (to track which shipment is in which freighter)
            async with session.get(f"{BASE_URL}/shipments/matches") as resp:
                if resp.status != 200:
                    print("Failed to get shipment matches")
                    await asyncio.sleep(1)
                    continue
                matches = await resp.json()
            
            # Process each freighter that is "In Transit"
            for schedule in schedules:
                if schedule.get("status", "").lower() != "in transit":
                    continue
                if schedule.get("arrivallat") is None or schedule.get("arrivallng") is None:
                    continue

                # Get the shipment associated with this freighter
                match = next((m for m in matches if m["scheduleid"] == schedule["scheduleid"]), None)
                if not match:
                    continue  # Skip if no shipment match is found

                # Retrieve shipment details
                async with session.get(f"{BASE_URL}/shipments/requests?request_id={match['requestid']}") as shipment_resp:
                    if shipment_resp.status != 200:
                        print(f"Failed to get shipment request for {match['requestid']}")
                        continue
                    shipment = await shipment_resp.json()

                # Current and destination coordinates
                current_lat = float(schedule["departurelat"])
                current_lng = float(schedule["departurelng"])
                dest_lat = float(schedule["arrivallat"])
                dest_lng = float(schedule["arrivallng"])

                distance_remaining = haversine(current_lat, current_lng, dest_lat, dest_lng)
                print("\nDISTANCE REMAINING\n", distance_remaining, "\n")

                if distance_remaining <= SPEED_KM_PER_TICK:
                    # Freighter reaches its destination
                    new_lat, new_lng = dest_lat, dest_lng
                    new_status = "completed"
                    shipment_status = "completed"
                else:
                    # Move towards the destination
                    fraction = SPEED_KM_PER_TICK / distance_remaining
                    new_lat = current_lat + fraction * (dest_lat - current_lat)
                    new_lng = current_lng + fraction * (dest_lng - current_lng)
                    new_status = "in transit"
                    shipment_status = "pending"

                print("\nFractional movement\n", fraction, "\n")

                # Update freighter schedule
                updated_schedule = schedule.copy()
                updated_schedule["departurelat"] = float(new_lat)
                updated_schedule["departurelng"] = float(new_lng)
                updated_schedule["status"] = new_status
                updated_schedule["lastupdated"] = str(datetime.utcnow())

                async with session.post(f"{BASE_URL}/freighters/schedules", json=updated_schedule) as update_resp:
                    if update_resp.status == 200:
                        print(f"Updated schedule {schedule['scheduleid']} to status {new_status}")
                    else:
                        error_text = await update_resp.text()
                        print(f"Failed to update schedule {schedule['scheduleid']}: {error_text}")

                # Update shipment position (origin moves as the truck moves)

                updated_shipment = shipment[0].copy()

                updated_shipment["originlat"] = float(new_lat)
                updated_shipment["originlng"] = float(new_lng)
                updated_shipment["status"] = shipment_status
                updated_shipment["lastupdated"] = str(datetime.utcnow())

                async with session.post(f"{BASE_URL}/shipments/requests", json=updated_shipment) as update_resp:
                    if update_resp.status == 200:
                        print(f"Updated shipment {updated_shipment['requestid']} to status {shipment_status}")
                    else:
                        error_text = await update_resp.text()
                        print(f"Failed to update shipment {updated_shipment['requestid']}: {error_text}")

            await asyncio.sleep(0.5)
