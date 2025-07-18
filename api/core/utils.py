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
