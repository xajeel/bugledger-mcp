import importlib.resources
from pathlib import Path


def _repo_shared_path(*parts):
    for parent in Path(__file__).resolve().parents:
        path = parent.joinpath("shared", *parts)
        if path.is_file() or path.is_dir():
            return path
    return None


def read_shared_text(*parts):
    """Read a file from the packaged shared/ copy, or repo shared/ in dev."""

    try:
        root = importlib.resources.files("bugledger_mcp.shared")
        path = root.joinpath(*parts)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass

    path = _repo_shared_path(*parts)
    if path and path.is_file():
        return path.read_text(encoding="utf-8")

    raise FileNotFoundError(f"shared/{'/'.join(parts)} not found")


def list_shared_files(*parts, suffix=""):
    """List files under shared/ from the package or repo."""

    try:
        root = importlib.resources.files("bugledger_mcp.shared")
        folder = root.joinpath(*parts)
        if folder.is_dir():
            for item in folder.iterdir():
                if not suffix or item.name.endswith(suffix):
                    yield item
            return
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        pass

    path = _repo_shared_path(*parts)
    if path and path.is_dir():
        for item in sorted(path.glob(f"*{suffix}")):
            yield item
        return

    raise FileNotFoundError(f"shared/{'/'.join(parts)} not found")
