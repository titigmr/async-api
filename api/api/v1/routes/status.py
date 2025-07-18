from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db_session
from api.logging_config import logger
from api.schemas import HealthResponse, ReadyComponent, ReadyResponse
from api.services.queue_service import QueueSender

router = APIRouter()


@router.get(path="/health", summary="Vérifie la santé de l'API")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    path="/readiness",
    summary="Vérifie si les dépendances sont prêtes et que l'API est prête à recevoir du trafic",
)
async def readiness(
    db: Annotated[AsyncSession, Depends(dependency=get_db_session)],
    queue_sender: Annotated[QueueSender, Depends(dependency=QueueSender)],
) -> ReadyResponse:
    components: dict = {}

    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
        db_details = None
    except Exception as error:
        logger.error(f"Database connection error: {error}")
        db_status = "error"
        db_details = str(error)
    components["database"] = ReadyComponent(status=db_status, details=db_details)

    try:
        await queue_sender.ping()
        broker_status = "ok"
        broker_details = None
    except Exception as error:
        logger.error(f"Broker connection error: {error}")
        broker_status = "error"
        broker_details = str(error)
    components["broker"] = ReadyComponent(status=broker_status, details=broker_details)

    global_status: Literal["ok", "error"] = (
        "ok" if all(component.status == "ok" for component in components.values()) else "error"
    )
    return ReadyResponse(status=global_status, components=components)
