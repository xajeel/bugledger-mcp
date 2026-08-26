# ruleid: bugledger-cors-allow-all
allow_origins = "*"

# ruleid: bugledger-cors-allow-all
cors_origins = "*"

# ok: bugledger-cors-allow-all
allow_origins = "https://myapp.com"

# ok: bugledger-cors-allow-all
cors_origins = os.environ["ALLOWED_ORIGINS"]
