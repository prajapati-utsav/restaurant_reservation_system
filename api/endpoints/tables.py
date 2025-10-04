from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db_module.db import get_db
from models.models import Table as TableModel
from schemas.schemas import TableCreate, TableUpdate, Table as TableSchema

router = APIRouter(prefix="/tables", tags=["Tables"])


# Create table
@router.post("/")
async def create_table(table: TableCreate, db: Session = Depends(get_db)):
    try:
        new_table = TableModel(**table.dict())
        db.add(new_table)
        db.commit()
        db.refresh(new_table)
        return {
            "message": "Table created successfully",
            "count": 1,
            "data": TableSchema.from_orm(new_table)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# List tables
@router.get("/")
async def list_tables(db: Session = Depends(get_db)):
    try:
        tables = db.query(TableModel).all()
        return {
            "message": "Tables fetched successfully",
            "count": len(tables),
            "data": [TableSchema.from_orm(tbl) for tbl in tables]
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get single table
@router.get("/{table_id}")
async def get_table(table_id: str, db: Session = Depends(get_db)):
    try:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return {
            "message": "Table fetched successfully",
            "count": 1,
            "data": TableSchema.from_orm(table)
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update table
@router.patch("/{table_id}")
async def update_table(table_id: str, update: TableUpdate, db: Session = Depends(get_db)):
    try:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        for key, value in update.dict(exclude_unset=True).items():
            setattr(table, key, value)

        db.commit()
        db.refresh(table)
        return {
            "message": "Table updated successfully",
            "count": 1,
            "data": TableSchema.from_orm(table)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete table
@router.delete("/{table_id}")
async def delete_table(table_id: str, db: Session = Depends(get_db)):
    try:
        table = db.query(TableModel).filter(TableModel.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        db.delete(table)
        db.commit()
        return {
            "message": "Table deleted successfully",
            "count": 1,
            "data": TableSchema.from_orm(table)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))