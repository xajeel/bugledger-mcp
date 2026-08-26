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
