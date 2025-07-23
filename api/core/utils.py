from pathlib import Path

import toml


def get_version() -> tuple[str, str]:
    pyproject_path: Path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    try:
        with Path.open(pyproject_path) as f:
            data: dict[str, str] = toml.loads(s=f.read())
            return data["project"]["version"], data["project"]["name"]  # type: ignore
    except Exception:
        return "0.0.0", ""


ASYNC_TO_SYNC_DRIVERS: dict[str, str] = {
    "postgresql+asyncpg://": "postgresql+psycopg2://",
    "mysql+aiomysql://": "mysql+pymysql://",
    "sqlite+aiosqlite://": "sqlite+pysqlite://",
}


def make_sync_url(url: str) -> str:
    for async_prefix, sync_prefix in ASYNC_TO_SYNC_DRIVERS.items():
        if url.startswith(async_prefix):
            return url.replace(async_prefix, sync_prefix, 1)
    return url
