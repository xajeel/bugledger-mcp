import os

# ruleid: bugledger-password-in-url
DATABASE_URL = "postgresql://admin:supersecret@db.example.com:5432/mydb"

# ruleid: bugledger-password-in-url
REDIS_URL = "redis://default:mypassword@redis.internal:6379"

# ok: bugledger-password-in-url
DATABASE_URL = os.environ["DATABASE_URL"]

# ok: bugledger-password-in-url
DOCS_URL = "https://docs.example.com/guide"

# ok: bugledger-password-in-url
TEMPLATE = "postgresql://admin:${DB_PASSWORD}@db.example.com:5432/mydb"

# ok: bugledger-password-in-url
EXAMPLE = "postgres://user:password@host:5432/db"
