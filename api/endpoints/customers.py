from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_module.db import get_db
from models.models import Customer as CustomerModel
from schemas.schemas import CustomerCreate, CustomerUpdate, Customer as CustomerSchema
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/customers", tags=["Customers"])

# Create customer
@router.post("/")
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(CustomerModel).filter(
            (CustomerModel.phone_number == customer.phone_number) |
            (CustomerModel.email == customer.email)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number or email already exists")

        new_customer = CustomerModel(**customer.dict())
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return {
            "message": "Customer created successfully",
            "count": 1,
            "data": CustomerSchema.from_orm(new_customer)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List all customers
@router.get("/")
async def list_customers(db: Session = Depends(get_db)):
    try:
        customers = db.query(CustomerModel).all()
        return {
            "message": "Customers fetched successfully",
            "count": len(customers),
            "data": [CustomerSchema.from_orm(cust) for cust in customers]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get single customer
@router.get("/{customer_id}")
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {
            "message": "Customer fetched successfully",
            "count": 1,
            "data": CustomerSchema.from_orm(customer)
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update customer
@router.put("/{customer_id}")
async def put_customer(customer_id: int, updated_customer: CustomerUpdate, db: Session = Depends(get_db)):
    try:
        customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        for key, value in updated_customer.dict().items():
            setattr(customer, key, value)

        db.commit()
        db.refresh(customer)

        return {
            "message": "Customer fully updated successfully",
            "count": 1,
            "data": CustomerSchema.from_orm(customer)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete customer
@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        db.delete(customer)
        db.commit()
        return {
            "message": "Customer deleted successfully",
            "count": 1,
            "data": CustomerSchema.from_orm(customer)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))