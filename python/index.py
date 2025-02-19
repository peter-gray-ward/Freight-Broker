from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import List, Optional

print('Python Backend API for "Freight Broker" application')