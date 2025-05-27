from pathlib import Path

import toml


def get_version():
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    print(pyproject_path)
    try:
        with open(pyproject_path, "r") as f:
            data = toml.loads(f.read())
            return data["project"]["version"], data["project"]["name"]
    except Exception:
        return "0.0.0", ""
