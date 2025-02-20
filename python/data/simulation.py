import asyncio
import random
import time
import asyncpg
import aiohttp
from datetime import datetime, timedelta

# Backend API URL
BASE_URL = "http://localhost:8000"

# 20 American cities for shipments
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Indianapolis",
    "Charlotte", "San Francisco", "Seattle", "Denver", "Washington"
]

# 20 Freighters with unique capacities and starting locations
FREIGHTERS = [
    {
        "id": f"freighter-{i+1}",
        "name": f"Freighter {i+1}",
        "email": f"freighter{i+1}@test.com",
        "password": "securepass123",
        "max_load_kg": random.randint(10000, 50000),  # Random max load
        "available_kg": random.randint(5000, 25000),  # Random available load
        "current_city": random.choice(CITIES),  # Start in a random city
    }
    for i in range(20)
]

# 11 Suppliers (Clients)
SUPPLIERS = [
    {
        "id": f"supplier-{i+1}",
        "name": f"Supplier {i+1}",
        "email": f"supplier{i+1}@test.com",
        "password": "securepass123",
    }
    for i in range(11)
]


async def get_access_token(session, email, password, name, role):
    """
    Attempts to log in. If login fails, registers the user first.
    Returns the JWT access token.
    """
    login_url = f"{BASE_URL}/users/login"
    register_url = f"{BASE_URL}/users/register"

    # Try logging in first
    async with session.post(login_url, json={"name": name, "email": email, "password": password}) as resp:
        if resp.status == 200:
            data = await resp.json()
            print(f"✅ Logged in: {name}")
            return data["userid"], data["name"], data["email"], data["role"]
        else:
            print(f"❌ Login failed for {name}. Registering...")

    # Register if login fails
    async with session.post(register_url, json={"name": name, "email": email, "password": password, "role": role}) as resp:
        if resp.status == 200:
            data = await resp.json()
            print(f"✅ Registered: {name}")
            return data["userid"], data["name"], data["email"], data["role"]
        else:
            print(f"❌ Registration failed for {name}: {await resp.text()}")
            return None


async def setup_users():
    """
    Ensures that all freighters and suppliers exist in the system.
    """
    async with aiohttp.ClientSession() as session:
        # Authenticate or register all freighters
        for freighter in FREIGHTERS:
            freighter["user_id"], freighter["name"], freighter["email"], freighter["role"] = await get_access_token(
                session, freighter["email"], freighter["password"], freighter["name"], "Freighter"
            )

        # Authenticate or register all suppliers
        for supplier in SUPPLIERS:
            supplier["user_id"], supplier["name"], supplier["email"], supplier["role"] = await get_access_token(
                session, supplier["email"], supplier["password"], supplier["name"], "Client"
            )

        print('FREIGHTERS', FREIGHTERS)
        print('SUPPLIERS', SUPPLIERS)


async def move_freighters():
    """
    Simulates freighters moving between cities.
    """
    while True:
        for freighter in FREIGHTERS:
            # Pick a new destination city (must be different from current)
            new_city = random.choice([city for city in CITIES if city != freighter["current_city"]])

            print(f"🚚 {freighter['name']} is moving from {freighter['current_city']} → {new_city}")

            # Update the freighter's current location
            freighter["current_city"] = new_city

        await asyncio.sleep(5)  # Wait before next update (simulating real-time movement)



async def generate_shipments():
    """
    Simulates suppliers generating shipment requests.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            for supplier in SUPPLIERS:
                # Generate a random shipment
                origin_city = random.choice(CITIES)
                destination_city = random.choice([city for city in CITIES if city != origin_city])
                weight_kg = random.randint(500, 5000)

                print(f"📦 {supplier['name']} is shipping {weight_kg}kg from {origin_city} to {destination_city}")

                shipment_data = {
                    "client_id": supplier["user_id"],
                    "origin_city": origin_city,
                    "origin_lat": random.uniform(30.0, 50.0),  # Simulated lat/lng
                    "origin_lng": random.uniform(-120.0, -70.0),
                    "destination_city": destination_city,
                    "destination_lat": random.uniform(30.0, 50.0),
                    "destination_lng": random.uniform(-120.0, -70.0),
                    "weight_kg": weight_kg,
                    "special_handling": None,
                }

                # Call API to create shipment request
                async with session.post(f"{BASE_URL}/shipments/requests", json=shipment_data) as resp:
                    if resp.status == 200:
                        print(f"✅ Shipment request created by {supplier['name']}")
                    else:
                        print(f"❌ Failed to create shipment for {supplier['name']}: {await resp.text()}")

            await asyncio.sleep(5)  # Generate shipments every 5 seconds


