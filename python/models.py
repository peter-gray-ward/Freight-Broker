from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field
import uuid

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

class FreighterSchedules(SQLModel, table=True):
    scheduleid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    freighterid: Optional[str] = Field(default=None, index=True)
    departurecity: Optional[str] = Field(default=None, max_length=255)
    departurelat: Optional[float] = None
    departurelng: Optional[float] = None
    arrivalcity: Optional[str] = Field(default=None, max_length=255)
    arrivallat: Optional[float] = None
    arrivallng: Optional[float] = None
    departuredate: Optional[datetime] = None
    arrivaldate: Optional[datetime] = None
    maxloadkg: Optional[float] = None
    availablekg: Optional[float] = None
    status: str = "Available"


    def __hash__(self):
        return hash(self.scheduleid)

    def __eq__(self, other):
        if isinstance(other, FreightSchedule):
            return self.scheduleid == other.scheduleid
        return False


class ShipmentRequests(SQLModel, table=True):
    requestid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    clientid: Optional[str] = Field(default=None, index=True)
    origincity: Optional[str] = Field(default=None, max_length=255)
    originlat: Optional[float] = None
    originlng: Optional[float] = None
    destinationcity: Optional[str] = Field(default=None, max_length=255)
    destinationlat: Optional[float] = None
    destinationlng: Optional[float] = None
    weightkg: Optional[float] = None
    specialhandling: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = "Pending"
    createdat: Optional[datetime] = None
    lastupdated: Optional[datetime] = None


    def __hash__(self):
        return hash(self.requestid)

    def __eq__(self, other):
        if isinstance(other, ShipmentRequest):
            return self.requestid == other.requestid
        return False

class ShipmentMatches(SQLModel, table=True):
    matchid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    requestid: Optional[str] = Field(default=None, foreign_key="shipmentrequests.requestid")
    scheduleid: Optional[str] = Field(default=None, foreign_key="freighterschedules.scheduleid")
    status: str = "Pending"