from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str  # "Client" or "Freighter"


class User(BaseModel):
    userid: str
    name: str
    role: str

    def __hash__(self):
        return hash(self.userid)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.userid == other.userid
        return False

class FreightSchedule(BaseModel):
    freighter_id: str
    departure_city: str
    departure_lat: float
    departure_lon: float
    arrival_city: str
    arrival_lat: float
    arrival_lon: float
    departure_date: datetime
    arrival_date: datetime
    max_load_kg: float
    available_kg: float
    status: str = "Available"

class ShipmentRequest(BaseModel):
    client_id: str
    origin_city: str
    origin_lat: float
    origin_lon: float
    destination_city: str
    destination_lat: float
    destination_lon: float
    weight_kg: float
    special_handling: Optional[str]
    status: str = "Pending"

class Order(BaseModel):
    match_id: str
    client_id: str
    freighter_id: str
    order_status: str = "In Transit"