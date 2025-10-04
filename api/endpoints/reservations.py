from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from typing import List
from db_module.db import get_db
from models.models import Reservation as ReservationModel, Table as TableModel, ReservationTableAssociation, Customer as CustomerModel, OperatingHour as OperatingHourModel, ReservationStatus, TableStatus
from schemas.schemas import ReservationCreate, ReservationUpdate, Reservation as ReservationSchema,MergeTablesRequest
from datetime import date

router = APIRouter(prefix="/reservations", tags=["Reservations"])


# Helper Functions
def check_operating_hours(res_date: datetime.date, res_time: time, db: Session):
    day_name = res_date.strftime("%A")
    hours = db.query(OperatingHourModel).filter(OperatingHourModel.day_of_week == day_name).first()
    if not hours:
        raise HTTPException(status_code=400, detail=f"No operating hours found for {day_name}")
    if not (hours.opening_time <= res_time <= hours.closing_time):
        raise HTTPException(status_code=400, detail="Reservation time is outside operating hours")


def check_table_availability(table_ids: List[int], res_date: datetime.date, res_time: time, duration_hours: int, db: Session):
    for table_id in table_ids:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail=f"Table {table_id} not found")
        if table.status not in [TableStatus.AVAILABLE]:
            raise HTTPException(status_code=400, detail=f"Table {table.table_number} is not available")
        overlapping = (
            db.query(ReservationTableAssociation)
            .join(ReservationModel)
            .filter(
                ReservationTableAssociation.table_id == table_id,
                ReservationModel.reservation_date == res_date,
                ReservationModel.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.SEATED]),
                (ReservationModel.reservation_time <= res_time) & 
                (res_time < (datetime.combine(res_date, ReservationModel.reservation_time) + timedelta(hours=ReservationModel.duration_hours)).time())
            )
            .first()
        )
        if overlapping:
            raise HTTPException(status_code=400, detail=f"Table {table.table_number} is already booked at this time")


def check_customer_conflicts(customer_id: int, res_date: datetime.date, res_time: time, duration_hours: int, db: Session):
    conflict = (
        db.query(ReservationModel)
        .filter(
            ReservationModel.customer_id == customer_id,
            ReservationModel.reservation_date == res_date,
            ReservationModel.status.in_([ReservationStatus.CONFIRMED, ReservationStatus.SEATED]),
            (ReservationModel.reservation_time <= res_time) & 
            (res_time < (datetime.combine(res_date, ReservationModel.reservation_time) + timedelta(hours=ReservationModel.duration_hours)).time())
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=400, detail="Customer has a conflicting reservation")


# Create reservation
@router.post("/")
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == reservation.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    table_ids = [int(tid) for tid in reservation.table_ids]

    check_operating_hours(reservation.reservation_date, reservation.reservation_time, db)
    check_customer_conflicts(reservation.customer_id, reservation.reservation_date, reservation.reservation_time, reservation.duration_hours, db)
    check_table_availability(table_ids, reservation.reservation_date, reservation.reservation_time, reservation.duration_hours, db)

    db_res = ReservationModel(**reservation.dict(exclude={"table_ids"}))
    db.add(db_res)
    db.commit()
    db.refresh(db_res)

    for table_id in table_ids:
        db.add(ReservationTableAssociation(reservation_id=db_res.id, table_id=table_id))
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        table.status = TableStatus.RESERVED
    db.commit()
    db.refresh(db_res)

    return {"message": "Reservation created successfully", "data": ReservationSchema.from_orm(db_res)}


# List reservations
@router.get("/")
def list_reservations(db: Session = Depends(get_db)):
    reservations = db.query(ReservationModel).all()
    return {"message": "Reservations fetched successfully", "count": len(reservations), "data": [ReservationSchema.from_orm(r) for r in reservations]}


# Get single reservation
@router.get("/{reservation_id}")
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    res = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation fetched successfully", "data": ReservationSchema.from_orm(res)}


# Update reservation
@router.patch("/{reservation_id}")
def update_reservation(reservation_id: int, update: ReservationUpdate, db: Session = Depends(get_db)):
    res = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    for key, value in update.dict(exclude_unset=True).items():
        if key == "table_ids":
            new_table_ids = [int(tid) for tid in value]
            check_table_availability(new_table_ids, res.reservation_date, res.reservation_time, res.duration_hours, db)
            for rta in res.tables:
                rta.table.status = TableStatus.AVAILABLE
                db.delete(rta)

            for table_id in new_table_ids:
                db.add(ReservationTableAssociation(reservation_id=res.id, table_id=table_id))
                table = db.query(TableModel).filter(TableModel.id == table_id).first()
                table.status = TableStatus.RESERVED
        else:
            setattr(res, key, value)
    
    db.commit()
    db.refresh(res)
    return {"message": "Reservation updated successfully", "data": ReservationSchema.from_orm(res)}


# Delete reservation
@router.patch("/{reservation_id}/status")
def update_reservation_status(reservation_id: int, status: ReservationStatus, db: Session = Depends(get_db)):
    res = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    res.status = status
    if status in [ReservationStatus.CANCELLED, ReservationStatus.COMPLETED]:
        for rta in res.tables:
            rta.table.status = TableStatus.AVAILABLE
        if status == ReservationStatus.COMPLETED:
            customer = res.customer
            if customer:
                customer.visit_count += 1
                db.add(customer)
    db.commit()
    db.refresh(res)
    return {"message": "Reservation status updated successfully", "data": ReservationSchema.from_orm(res)}


# Table Merge
@router.post("/{reservation_id}/merge-tables")
def merge_tables(reservation_id: int, request: MergeTablesRequest, db: Session = Depends(get_db)):
    table_ids = request.table_ids
    res = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for table_id in table_ids:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table.is_combinable or table.status != TableStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail=f"Table {table.table_number} cannot be merged")
        table.status = TableStatus.RESERVED
        db.add(ReservationTableAssociation(reservation_id=reservation_id, table_id=table_id))
    db.commit()
    return {"message": "Tables merged successfully"}


# Table Demerge
@router.post("/{reservation_id}/demerge-tables")
def demerge_tables(reservation_id: int, db: Session = Depends(get_db)):
    res = db.query(ReservationModel).filter(ReservationModel.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for rta in res.tables:
        rta.table.status = TableStatus.AVAILABLE
        db.delete(rta)
    db.commit()
    return {"message": "Tables demerged successfully"}


# Daily reservation report
@router.get("/daily-report/")
def daily_reservation_report(
    report_date: date = Query(..., description="Date for the report in YYYY-MM-DD format"),  # use `date` here
    db: Session = Depends(get_db)
):
    """
    Generate a daily reservation report for a given date.
    Returns reservation details including customer, table, time, and status.
    """
    reservations = (
        db.query(ReservationModel)
        .filter(ReservationModel.reservation_date == report_date)
        .all()
    )

    report = []
    for res in reservations:
        tables = [rta.table.table_number for rta in res.tables]
        report.append({
            "reservation_id": res.id,
            "customer_name": f"{res.customer.first_name} {res.customer.last_name}",
            "phone_number": res.customer.phone_number,
            "party_size": res.party_size,
            "reservation_time": res.reservation_time.strftime("%H:%M"),
            "tables": tables,
            "status": res.status.value,
            "requested_preference": res.requested_preference.value if res.requested_preference else None,
            "notes": res.notes
        })

    return {
        "message": f"Daily reservation report for {report_date}",
        "date": report_date,
        "total_reservations": len(report),
        "data": report
    }