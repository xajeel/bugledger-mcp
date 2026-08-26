import os

# ruleid: bugledger-debug-mode
DEBUG = True

# ruleid: bugledger-debug-mode
DEBUG = "true"

# ok: bugledger-debug-mode
DEBUG = os.environ.get("DEBUG", "false")

# ok: bugledger-debug-mode
DEBUG = False
