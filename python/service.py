import math
import asyncio
import uuid
from sqlalchemy import select
from startup import connect_db_sync
from models import FreighterSchedules, ShipmentRequests, ShipmentMatches 


def haversine(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance between two points 
    on the Earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def match_freighters_to_shipments():
    session = connect_db_sync()
    try:
        # Retrieve all available freighter schedules (assumed "available" status)
        result = session.execute(
            select(FreighterSchedules).where(FreighterSchedules.status == "available")
        )
        freighters = result.scalars().all()

        # Retrieve all pending shipment requests
        result = session.execute(
            select(ShipmentRequests).where(ShipmentRequests.status == "pending")
        )
        shipments = result.scalars().all()

        for freighter in freighters:
            available_capacity = freighter.availablekg

            # Filter and sort pending shipments by proximity to the freighter's departure location
            pending_shipments = [s for s in shipments if s.status == "pending"]
            pending_shipments.sort(
                key=lambda s: haversine(freighter.departurelat, freighter.departurelng, s.originlat, s.originlng)
            )

            for shipment in pending_shipments:
                if shipment.weightkg <= available_capacity:
                    print("\n", "CREATING A MATCH!!!", "\n")

                    # Create a match record in the shipment_matches table.
                    match_record = ShipmentMatches(
                        matchid=str(uuid.uuid4()),
                        clientid=str(shipment.clientid),
                        freighterid=str(freighter.freighterid),
                        requestid=str(shipment.requestid),
                        scheduleid=str(freighter.scheduleid),
                        status="matched"  # or "pending" based on your workflow
                    )
                    session.add(match_record)

                    # Update the shipment so that it won't be used again.
                    shipment.status = "matched"

                    # Deduct the shipment's weight from the available capacity.
                    available_capacity -= float(shipment.weightkg)
                    freighter.availablekg = float(available_capacity)
                    freighter.arrivallat = float(shipment.destinationlat)
                    freighter.arrivallng = float(shipment.destinationlng)
                    freighter.status = "in transit"

                    print("\n", freighter, shipment, "\n")

                    # If the freighter is fully loaded, break out of the loop.
                    if available_capacity <= 0:
                        break

        session.commit()
    finally:
        session.close()

async def match_freighters_to_shipments_async():
    while True:
        await asyncio.to_thread(match_freighters_to_shipments)
        await asyncio.sleep(3)
