
import asyncio


class HealthCheckServer:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handler_health_check, self.host, self.port)
        await server.start_serving()

    async def handler_health_check(self,reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            await reader.readuntil(b'\r\n\r\n')
        except asyncio.IncompleteReadError:
            writer.close()
            await writer.wait_closed()
            return

        body = '{"status": "ok"}'
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )

        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()