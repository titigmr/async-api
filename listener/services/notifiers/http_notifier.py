import asyncio
import ssl
from typing import Literal

import aiohttp
from pydantic import BaseModel, Field

from listener.core.logger import logger
from listener.services.notifier_service import BaseNotifier, NotificationException


class HttpCallback(BaseModel):
    type: Literal["http"]
    url: str = Field(default=..., description="Url.")
    skip_tls: bool = Field(default=False, description="Disable TLS check.")


# ---------------------------------
# Http Notifier
# ---------------------------------


class HttpNotifier(BaseNotifier):
    def __init__(self, max_reties) -> None:
        self.max_reties = max_reties

    def unmarshall_callback(self, callback: dict) -> HttpCallback | None:
        try:
            return HttpCallback.model_validate(callback)
        except Exception:
            return None

    def accept(self, callback: dict):
        return self.unmarshall_callback(callback) is not None

    async def notify(self, callback: dict, message: dict) -> None:
        http_callback = self.unmarshall_callback(callback)
        if http_callback is None:
            msg = f"Http notifier cannot handle callback: {callback}"
            raise NotificationException(msg)
        await self.notify_retry(http_callback, message, 0)

    async def notify_retry(self, http_callback: HttpCallback, message: dict, retry: int) -> None:
        connector = aiohttp.TCPConnector(ssl=self.ssl_context(http_callback.skip_tls))
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(http_callback.url, data=message) as response:
                    if response.status != 200:
                        msg = f"Bad response status '{response.status}' for callback: {http_callback}"
                        raise NotificationException(
                            msg,
                        )
                    logger.debug("Http notification send successfully.")
        except Exception as e:
            if retry < self.max_reties:
                wait_time = pow(retry + 1, 2)
                logger.debug(f"Failure, about to retry n°{retry + 1}/{self.max_reties} in {wait_time}s...")
                await asyncio.sleep(wait_time)
                await self.notify_retry(http_callback, message, retry + 1)
                return
            logger.debug("No more retries")
            msg = f"Error during the http call for callback: {http_callback}"
            raise NotificationException(msg, e)

    def ssl_context(self, skip_tls: bool):
        ssl_context = ssl.create_default_context()
        if skip_tls:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
