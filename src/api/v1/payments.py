from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.dependencies.auth import require_api_key
from src.services.payments import PaymentsService

router = APIRouter(
    route_class=DishkaRoute,
    dependencies=[Depends(require_api_key)],
)


@router.post("/")
async def create_new_payment(service: FromDishka[PaymentsService]):
    pass
