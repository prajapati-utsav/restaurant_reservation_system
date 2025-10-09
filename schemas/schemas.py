from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, time
from enum import Enum

class TableLocation(str, Enum):
    WINDOW = "Window"
    CENTER = "Center"
    OUTDOOR = "Outdoor"

class TableStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Maintenance"
    SPECIAL_EVENT = "Special Event"
    RESERVED = "Reserved"

class CustomerPreference(str, Enum):
    QUIET_AREA = "Quiet Area"
    WINDOW_SEAT = "Window Seat"
    BOOTH = "Booth"
    NEAR_KITCHEN = "Near Kitchen"

class ReservationStatus(str, Enum):
    CONFIRMED = "Confirmed"
    PENDING = "Pending"
    SEATED = "Seated"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# ----------------------
# Table Schemas
# ----------------------
class TableBase(BaseModel):
    table_number: int
    capacity: int
    location: TableLocation
    status: Optional[TableStatus] = TableStatus.AVAILABLE
    is_combinable: Optional[bool] = False

    @field_validator("table_number")
    def table_number_positive(cls, v):
        if v <= 0:
            raise ValueError("Table number must be greater than 0")
        return v

    @field_validator("capacity")
    def capacity_positive(cls, v):
        if v <= 0:
            raise ValueError("Table capacity must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "table_number": 1,
                "capacity": 4,
                "location": "Window",
                "status": "Available",
                "is_combinable": False
            }
        }

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    capacity: Optional[int]
    location: Optional[TableLocation]
    status: Optional[TableStatus]
    is_combinable: Optional[bool]

class Table(TableBase):
    id: int

    class Config:
        from_attributes = True

class MergeTablesRequest(BaseModel):
    table_ids: List[int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "table_ids": [1, 2]
            }
        }

# ----------------------
# Customer Schemas
# ----------------------
class CustomerBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[str] = None
    preferences: Optional[str] = ""
    dietary_requirements: Optional[str] = ""
    special_notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+1234567890",
                "email": "john@example.com",
                "preferences": "Window Seat",
                "dietary_requirements": "Vegan",
                "special_notes": "Birthday celebration"
            }
        }

class CustomerCreate(CustomerBase):
    first_name: str
    last_name: str
    phone_number: str

    @field_validator("first_name", "last_name")
    def name_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("phone_number")
    def phone_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone number is required")
        return v

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[str] = None
    dietary_requirements: Optional[str] = None
    special_notes: Optional[str] = None

    class Config:
        from_attributes = True

class Customer(CustomerBase):
    id: int
    visit_count: int

    class Config:
        from_attributes = True

# ----------------------
# Reservation Schemas
# ----------------------
class ReservationBase(BaseModel):
    customer_id: int
    party_size: int
    reservation_date: date
    reservation_time: time
    duration_hours: Optional[int] = 2
    status: Optional[ReservationStatus] = ReservationStatus.CONFIRMED
    requested_preference: Optional[CustomerPreference] = None
    is_walk_in: Optional[bool] = False
    notes: Optional[str] = None

    @field_validator("party_size")
    def party_size_positive(cls, v):
        if v <= 0:
            raise ValueError("Party size must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "1",
                "party_size": 4,
                "reservation_date": "2025-10-04",
                "reservation_time": "19:00",
                "duration_hours": 2,
                "status": "Confirmed",
                "requested_preference": "Window Seat",
                "is_walk_in": False,
                "notes": "Birthday dinner"
            }
        }

class ReservationCreate(ReservationBase):
    table_ids: Optional[List[str]] = []

class ReservationUpdate(BaseModel):
    party_size: Optional[int]
    reservation_date: Optional[date]
    reservation_time: Optional[time]
    duration_hours: Optional[int]
    status: Optional[ReservationStatus]
    requested_preference: Optional[CustomerPreference]
    is_walk_in: Optional[bool]
    notes: Optional[str]
    table_ids: Optional[List[str]] = []

class Reservation(ReservationBase):
    id: int
    assigned_capacity: int
    tables: Optional[List[Table]] = []

    class Config:
        from_attributes = True

# ----------------------
# Operating Hours Schemas
# ----------------------
class OperatingHourBase(BaseModel):
    day_of_week: str
    opening_time: time
    closing_time: time

    @field_validator("day_of_week")
    def day_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Day of week is required")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": "Monday",
                "opening_time": "10:00",
                "closing_time": "22:00"
            }
        }

class OperatingHourCreate(OperatingHourBase):
    pass

class OperatingHourUpdate(BaseModel):
    opening_time: Optional[time]
    closing_time: Optional[time]

class OperatingHour(OperatingHourBase):
    class Config:
        from_attributes = True