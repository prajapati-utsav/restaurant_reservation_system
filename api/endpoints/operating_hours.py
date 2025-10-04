from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db_module.db import get_db
from models.models import OperatingHour as OperatingHourModel
from schemas.schemas import OperatingHourCreate, OperatingHourUpdate, OperatingHour as OperatingHourSchema

router = APIRouter(prefix="/operating-hours", tags=["Operating Hours"])


# Create operating hours
@router.post("/")
def create_hours(hours: OperatingHourCreate, db: Session = Depends(get_db)):
    try:
        new_hours = OperatingHourModel(**hours.dict())
        db.add(new_hours)
        db.commit()
        db.refresh(new_hours)
        return {
            "message": "Operating hours created successfully",
            "count": 1,
            "data": OperatingHourSchema.from_orm(new_hours)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List all operating hours
@router.get("/")
def list_hours(db: Session = Depends(get_db)):
    try:
        hours_list = db.query(OperatingHourModel).all()
        return {
            "message": "Operating hours fetched successfully",
            "count": len(hours_list),
            "data": [OperatingHourSchema.from_orm(hour) for hour in hours_list]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get single operating hours
@router.get("/{day_of_week}")
def get_hours(day_of_week: str, db: Session = Depends(get_db)):
    try:
        hours = db.query(OperatingHourModel).filter(OperatingHourModel.day_of_week == day_of_week).first()
        if not hours:
            raise HTTPException(status_code=404, detail=f"No operating hours found for {day_of_week}")
        return {
            "message": "Operating hours fetched successfully",
            "count": 1,
            "data": OperatingHourSchema.from_orm(hours)
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update operating hours
@router.put("/{day_of_week}")
def update_hours(day_of_week: str, update: OperatingHourUpdate, db: Session = Depends(get_db)):
    try:
        hours = db.query(OperatingHourModel).filter(OperatingHourModel.day_of_week == day_of_week).first()
        if not hours:
            raise HTTPException(status_code=404, detail=f"No operating hours found for {day_of_week}")

        for key, value in update.dict(exclude_unset=True).items():
            setattr(hours, key, value)

        db.commit()
        db.refresh(hours)
        return {
            "message": "Operating hours updated successfully",
            "count": 1,
            "data": OperatingHourSchema.from_orm(hours)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete operating hours
@router.delete("/{day_of_week}")
def delete_hours(day_of_week: str, db: Session = Depends(get_db)):
    try:
        hours = db.query(OperatingHourModel).filter(OperatingHourModel.day_of_week == day_of_week).first()
        if not hours:
            raise HTTPException(status_code=404, detail=f"No operating hours found for {day_of_week}")

        db.delete(hours)
        db.commit()
        return {
            "message": f"Operating hours for {day_of_week} deleted successfully",
            "count": 1,
            "data": OperatingHourSchema.from_orm(hours)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))