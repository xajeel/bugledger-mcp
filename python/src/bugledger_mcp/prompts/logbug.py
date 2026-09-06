from bugledger_mcp.utils.shared_files import read_shared_text


def read_logbug_text():
    """Reads shared/logbug.md from the packaged copy or repo shared/."""

    return read_shared_text("logbug.md")


def logbug():
    """Draft a bug record from this session, wait for confirmation, then call record_bug."""

    return read_logbug_text()
