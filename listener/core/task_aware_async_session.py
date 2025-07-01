from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import AsyncSessionLocal

ctx_db_session: ContextVar[AsyncSession] = ContextVar("db_session")


# Dynamic proxy for AsyncSession
class TaskAwareAsyncSession:
    def __init__(self) -> None:
        pass

    def _get_wrapped_session(self):
        # New task: new session
        try:
            return ctx_db_session.get()
        except Exception:
            session = AsyncSessionLocal()
            ctx_db_session.set(session)
            return session

    def __getattr__(self, name):
        return getattr(self._get_wrapped_session(), name)
