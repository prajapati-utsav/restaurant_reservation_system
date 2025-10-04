from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db_module.db import Base
from sqlalchemy.sql import func

class TableLocation(str, enum.Enum):
    WINDOW = "Window"
    CENTER = "Center"
    OUTDOOR = "Outdoor"

class TableStatus(str, enum.Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Maintenance"
    SPECIAL_EVENT = "Special Event"
    RESERVED = "Reserved"

class CustomerPreference(str, enum.Enum):
    QUIET_AREA = "Quiet Area"
    WINDOW_SEAT = "Window Seat"
    BOOTH = "Booth"
    NEAR_KITCHEN = "Near Kitchen"

class DietaryRequirement(str, enum.Enum):
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    GLUTEN_FREE = "Gluten-Free"
    DAIRY_FREE = "Dairy-Free"
    NUT_ALLERGY = "Nut Allergy"

class ReservationStatus(str, enum.Enum):
    CONFIRMED = "Confirmed"
    PENDING = "Pending"
    SEATED = "Seated"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# --- ORM Models --- #
class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    location = Column(Enum(TableLocation), nullable=False)
    is_combinable = Column(Boolean, default=False)
    status = Column(Enum(TableStatus), default=TableStatus.AVAILABLE)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reservations = relationship(
        "ReservationTableAssociation",
        back_populates="table",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Table(id={self.id}, number={self.table_number}, capacity={self.capacity}, status={self.status})>"

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(12), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    preferences = Column(String(255), default="")
    dietary_requirements = Column(String(255), default="")
    visit_count = Column(Integer, default=0)
    special_notes = Column(String(255), nullable=True)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    reservations = relationship("Reservation", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.first_name} {self.last_name})>"

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    party_size = Column(Integer, nullable=False)
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    duration_hours = Column(Integer, nullable=False, default=2)
    booking_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.CONFIRMED)
    notes = Column(String(255), nullable=True)
    requested_preference = Column(Enum(CustomerPreference), nullable=True)
    is_walk_in = Column(Boolean, default=False)
    assigned_capacity = Column(Integer, default=0)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    customer = relationship("Customer", back_populates="reservations")
    tables = relationship("ReservationTableAssociation", back_populates="reservation")

    def __repr__(self):
        return f"<Reservation(id={self.id}, customer_id={self.customer_id}, date={self.reservation_date})>"

class ReservationTableAssociation(Base):
    __tablename__ = 'reservation_table_association'

    reservation_id = Column(Integer, ForeignKey('reservations.id'), primary_key=True)
    table_id = Column(Integer, ForeignKey('tables.id'), primary_key=True)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reservation = relationship("Reservation", back_populates="tables")
    table = relationship("Table", back_populates="reservations")

    def __repr__(self):
        return f"<RTA(reservation_id={self.reservation_id}, table_id={self.table_id})>"

class OperatingHour(Base):
    __tablename__ = 'operating_hours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(String(20), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<OperatingHour(day={self.day_of_week}, open={self.opening_time}, close={self.closing_time})>"