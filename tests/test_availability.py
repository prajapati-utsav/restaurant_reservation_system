import pytest
from datetime import date, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, Table, Customer
from api.endpoints.utils import check_table_availability, check_customer_conflicts
from fastapi import HTTPException

# Use in-memory SQLite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def tables(db):
    t1 = Table(table_number=1, capacity=4, location="WINDOW", is_combinable=True)
    t2 = Table(table_number=2, capacity=2, location="CENTER", is_combinable=False)
    db.add_all([t1, t2])
    db.commit()
    db.refresh(t1)
    db.refresh(t2)
    return [t1, t2]


@pytest.fixture
def customer(db):
    cust = Customer(first_name="John", last_name="Doe", phone_number="1234567890")
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust


def test_table_availability_success(db, tables):
    # No reservations yet, table should be available
    check_table_availability([tables[0].id], date(2025, 10, 6), time(12, 0), 2, db)


def test_table_availability_conflict(db, tables):
    # Mark table as RESERVED to simulate conflict
    tables[0].status = "RESERVED"
    db.commit()
    with pytest.raises(HTTPException):
        check_table_availability([tables[0].id], date(2025, 10, 6), time(12, 0), 2, db)


def test_customer_conflict_success(db, customer):
    # No reservations yet, should pass
    check_customer_conflicts(customer.id, date(2025, 10, 6), time(12, 0), 2, db)


def test_customer_conflict_overlap(db, customer, tables):
    from models.models import Reservation, ReservationStatus, ReservationTableAssociation

    # Create a conflicting reservation
    res = Reservation(
        customer_id=customer.id,
        reservation_date=date(2025, 10, 6),
        reservation_time=time(12, 0),
        duration_hours=2,
        status=ReservationStatus.CONFIRMED,
        party_size=2
    )
    db.add(res)
    db.commit()
    db.refresh(res)

    assoc = ReservationTableAssociation(reservation_id=res.id, table_id=tables[0].id)
    db.add(assoc)
    db.commit()

    with pytest.raises(HTTPException):
        check_customer_conflicts(customer.id, date(2025, 10, 6), time(12, 30), 1, db)
