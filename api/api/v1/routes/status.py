from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.brokers import AbstractBroker
from api.core.database import get_db_session
from api.core.utils import logger
from api.schemas import HealthResponse, ReadyComponent, ReadyResponse
from api.services import get_broker

router = APIRouter()


@router.get(
    path="/health", response_model=HealthResponse, summary="Vérifie la santé de l'API"
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    path="/readiness",
    response_model=ReadyResponse,
    summary="Vérifie si les dépendances sont prêtes et que l'API est prête à recevoir du trafic",
)
async def readiness(
    db: Annotated[AsyncSession, Depends(dependency=get_db_session)],
    broker: Annotated[AbstractBroker, Depends(dependency=get_broker)],
) -> ReadyResponse:
    components: dict = {}

    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
        db_details = None
    except Exception as error:
        logger.error(msg=f"Database connection error: {error}")
        db_status = "error"
        db_details = str(error)
    components["database"] = ReadyComponent(status=db_status, details=db_details)

    try:
        broker.ping()
        broker_status = "ok"
        broker_details = None
    except Exception as error:
        logger.error(msg=f"Broker connection error: {error}")
        broker_status = "error"
        broker_details = str(error)
    components["broker"] = ReadyComponent(status=broker_status, details=broker_details)

    global_status: Literal["ok"] | Literal["error"] = (
        "ok"
        if all(component.status == "ok" for component in components.values())
        else "error"
    )
    return ReadyResponse(status=global_status, components=components)
