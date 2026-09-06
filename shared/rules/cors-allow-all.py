import os

# ruleid: bugledger-cors-allow-all
allow_origins = "*"

# ruleid: bugledger-cors-allow-all
allow_origins = ["*"]

# ruleid: bugledger-cors-allow-all
cors_origins = "*"

# ruleid: bugledger-cors-allow-all
CORS_ALLOW_ALL_ORIGINS = True

# ok: bugledger-cors-allow-all
allow_origins = "https://myapp.com"

# ok: bugledger-cors-allow-all
allow_origins = ["https://myapp.com", "https://admin.myapp.com"]

# ok: bugledger-cors-allow-all
cors_origins = os.environ["ALLOWED_ORIGINS"]
