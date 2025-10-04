from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from typing import List

from models.models import (
    Reservation as ReservationModel,
    Table as TableModel,
    ReservationTableAssociation,
    Customer as CustomerModel,
    OperatingHour as OperatingHourModel,
    ReservationStatus,
    TableStatus
)


# Check operating hours
def check_operating_hours(res_date: date, res_time: time, db: Session):
    day_name = res_date.strftime("%A")
    hours = db.query(OperatingHourModel).filter(OperatingHourModel.day_of_week == day_name).first()
    if not hours:
        raise HTTPException(status_code=400, detail=f"No operating hours found for {day_name}")
    if not (hours.opening_time <= res_time <= hours.closing_time):
        raise HTTPException(status_code=400, detail="Reservation time is outside operating hours")


# Check table availability
def check_table_availability(table_ids: List[int], res_date: date, res_time: time, duration_hours: int, db: Session):
    requested_start = datetime.combine(res_date, res_time)
    requested_end = requested_start + timedelta(hours=duration_hours)

    for table_id in table_ids:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail=f"Table {table_id} not found")
        if table.status != TableStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail=f"Table {table.table_number} is not available")

        reservations = (
            db.query(ReservationTableAssociation)
            .join(ReservationModel)
            .filter(
                ReservationTableAssociation.table_id == table_id,
                ReservationModel.reservation_date == res_date,
                ReservationModel.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.SEATED])
            )
            .all()
        )

        for rta in reservations:
            existing_start = datetime.combine(rta.reservation.reservation_date, rta.reservation.reservation_time)
            existing_end = existing_start + timedelta(hours=rta.reservation.duration_hours)
            if requested_start < existing_end and existing_start < requested_end:
                raise HTTPException(status_code=400, detail=f"Table {table.table_number} is already booked at this time")


# Check customer reservation conflicts
def check_customer_conflicts(customer_id: int, res_date: date, res_time: time, duration_hours: int, db: Session):
    reservations = db.query(ReservationModel).filter(
        ReservationModel.customer_id == customer_id,
        ReservationModel.reservation_date == res_date,
        ReservationModel.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.SEATED])
    ).all()

    requested_start = datetime.combine(res_date, res_time)
    requested_end = requested_start + timedelta(hours=duration_hours)

    for res in reservations:
        existing_start = datetime.combine(res.reservation_date, res.reservation_time)
        existing_end = existing_start + timedelta(hours=res.duration_hours)
        if requested_start < existing_end and existing_start < requested_end:
            raise HTTPException(status_code=400, detail="Customer has a conflicting reservation")