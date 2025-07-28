import asyncio
from collections.abc import Callable
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Application, AppRunner, Request, Response, TCPSite
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.enum import ReadyStatus
from api.schemas.status import HealthResponse, ReadyComponent, ReadyResponse
from listener.core.logger import logger
from listener.services.queue_listener import QueueListener


class HealthCheckServer:
    def __init__(
        self,
        host: str,
        port: int,
        queue_listener: QueueListener,
        db_session: Callable[[], AsyncSession],
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.queue_listener: QueueListener = queue_listener
        self.db_session: Callable[[], AsyncSession] = db_session
        self.app: Application = web.Application()
        self.runner: AppRunner | None = None
        self.site: TCPSite | None = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get(path="/health", handler=self._handle_health)
        self.app.router.add_get(path="/ready", handler=self._handle_ready)

    async def start(self) -> None:
        logger.info(f"Starting health check server on {self.host}:{self.port}")
        self.runner = AppRunner(app=self.app)
        await self.runner.setup()

        self.site = TCPSite(runner=self.runner, host=self.host, port=self.port)
        await self.site.start()
        logger.info(f"Health check server started on http://{self.host}:{self.port}")

    async def stop(self) -> None:
        logger.info("Stopping health check server")
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Health check server stopped")

    @staticmethod
    async def _handle_health(_request: Request) -> Response:
        health_response = HealthResponse(status=ReadyStatus.OK)
        return web.json_response(health_response.model_dump())

    async def _handle_ready(self, _request: Request) -> Response:
        """Endpoint pour vérifier que le service est prêt (connexion RabbitMQ et DB)"""
        components: dict[str, ReadyComponent] = {}
        try:
            components["database"] = await asyncio.wait_for(self._check_database(), timeout=5.0)
        except TimeoutError:
            components["database"] = ReadyComponent(status=ReadyStatus.ERROR, details="Database check timeout")
        except Exception as e:
            components["database"] = ReadyComponent(status=ReadyStatus.ERROR, details=f"Database check failed: {e}")

        try:
            components["broker"] = await asyncio.wait_for(self._check_broker(), timeout=5.0)
        except TimeoutError:
            components["broker"] = ReadyComponent(status=ReadyStatus.ERROR, details="Broker check timeout")
        except Exception as e:
            components["broker"] = ReadyComponent(status=ReadyStatus.ERROR, details=f"Broker check failed: {e}")

        global_status: ReadyStatus = (
            ReadyStatus.OK if all(comp.status == ReadyStatus.OK for comp in components.values()) else ReadyStatus.ERROR
        )
        ready_response = ReadyResponse(status=global_status, components=components)
        status_code: HTTPStatus = HTTPStatus.OK if global_status == ReadyStatus.OK else HTTPStatus.SERVICE_UNAVAILABLE

        return web.json_response(data=ready_response.model_dump(), status=status_code)

    async def _check_database(self) -> ReadyComponent:
        """Check database connectivity"""
        try:
            session: AsyncSession = self.db_session()
            logger.debug(f"Healthcheck session: {id(session)}")
            async with session:
                await session.execute(text("SELECT 1"))
            return ReadyComponent(status=ReadyStatus.OK)
        except Exception as e:
            logger.error(f"Healthcheck failed, error: {e}")
            return ReadyComponent(status=ReadyStatus.ERROR, details=f"Database error: {e!s}")

    async def _check_broker(self) -> ReadyComponent:
        """Check broker connectivity"""
        if not self.queue_listener:
            return ReadyComponent(status=ReadyStatus.ERROR, details="No queue listener configured")

        try:
            await self.queue_listener.ping()
            return ReadyComponent(status=ReadyStatus.OK)
        except ConnectionError as e:
            return ReadyComponent(status=ReadyStatus.ERROR, details=f"Broker connection failed: {e}")
        except Exception as e:
            return ReadyComponent(status=ReadyStatus.ERROR, details=f"Unexpected error: {e}")
