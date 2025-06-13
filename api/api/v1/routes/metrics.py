from typing import Annotated

from fastapi import APIRouter, Depends

from api.services.metrics_service import MetricsService
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from starlette.responses import Response

router = APIRouter()

@router.get(
    path="/metrics",
)
async def metrics(    
    prom_service: Annotated[MetricsService, Depends(MetricsService)]
):
    await prom_service.update_custom_metrics()
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)