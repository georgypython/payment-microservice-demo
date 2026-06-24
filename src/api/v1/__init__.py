from fastapi import APIRouter

from src.api.v1 import payments

router = APIRouter()

router.include_router(payments.router, prefix="/payments")
