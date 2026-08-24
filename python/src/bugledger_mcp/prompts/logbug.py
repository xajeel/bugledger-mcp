from pathlib import Path


def read_logbug_text():
    """ Reads shared/logbug.md from the repo or the packaged copy. """

    for parent in Path(__file__).resolve().parents:
        path = parent / "shared" / "logbug.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError("shared/logbug.md not found")


def logbug():
    """Draft a bug record from this session, wait for confirmation, then call record_bug."""

    return read_logbug_text()
