import asyncio
import logging

# ruleid: bugledger-empty-catch-py
try:
    do_something()
except:
    pass

# ruleid: bugledger-empty-catch-py
try:
    do_something()
except Exception:
    pass

# ok: bugledger-empty-catch-py
try:
    do_something()
except Exception as e:
    logging.error("failed: %s", e)

# ok: bugledger-empty-catch-py
try:
    import ujson
except ImportError:
    pass


async def stop(task):
    # ok: bugledger-empty-catch-py
    try:
        await task
    except asyncio.CancelledError:
        pass
