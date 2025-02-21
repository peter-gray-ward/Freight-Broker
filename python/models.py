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
    scheduleid: str | None
    freighterid: str | None
    departurecity: str | None
    departurelat: float | None
    departurelng: float | None
    arrivalcity: str | None
    arrivallat: float | None
    arrivallng: float | None
    departuredate: str | None
    arrivaldate: str | None
    maxloadkg: float | None
    availablekg: float | None
    status: str = "Available"

    def __hash__(self):
        return hash(self.scheduleid)

    def __eq__(self, other):
        if isinstance(other, FreightSchedule):
            return self.scheduleid == other.scheduleid
        return False

class ShipmentRequest(BaseModel):
    requestid: str | None
    clientid: str | None
    origincity: str | None
    originlat: float | None
    originlng: float | None
    destinationcity: str | None
    destinationlat: float | None
    destinationlng: float | None
    weightkg: float | None
    specialhandling: str | None
    status: str | None = "Pending"
    createdat: str | None
    lastupdated: str | None

    def __hash__(self):
        return hash(self.requestid)

    def __eq__(self, other):
        if isinstance(other, ShipmentRequest):
            return self.requestid == other.requestid
        return False

class Order(BaseModel):
    match_id: str
    client_id: str
    freighter_id: str
    order_status: str = "In Transit"