from fastapi import APIRouter
from api.endpoints.customers import router as customer_router
from api.endpoints.reservations import router as reservation_router
from api.endpoints.tables import router as table_router
from api.endpoints.operating_hours import router as operating_hours_router

api_v1_router = APIRouter()

api_v1_router.include_router(customer_router)
api_v1_router.include_router(table_router)
api_v1_router.include_router(reservation_router)
api_v1_router.include_router(operating_hours_router)