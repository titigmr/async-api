from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.utils import logger
from app.schema.health import HealthComponent, HealthResponse
from app.service.queue_service import get_broker

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Vérifie la santé de l'API, DB et Broker",
)
def health_check(db: Annotated[Session, Depends(get_db_session)]):
    components = {}

    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
        db_details = None
    except Exception as error:
        logger.error(f"Database connection error: {error}")
        db_status = "error"
        db_details = str(error)
    components["database"] = HealthComponent(status=db_status, details=db_details)

    try:
        broker = get_broker()
        broker.ping()
        broker_status = "ok"
        broker_details = None
    except Exception as error:
        logger.error(f"Broker connection error: {error}")
        broker_status = "error"
        broker_details = str(error)
    components["broker"] = HealthComponent(status=broker_status, details=broker_details)

    global_status = (
        "ok"
        if all(component.status == "ok" for component in components.values())
        else "error"
    )

    return HealthResponse(status=global_status, components=components)
