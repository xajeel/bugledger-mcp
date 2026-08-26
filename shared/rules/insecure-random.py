import random
import secrets

# ruleid: bugledger-insecure-random-py
token = random.random()

# ruleid: bugledger-insecure-random-py
otp = random.randint(100000, 999999)

# ok: bugledger-insecure-random-py
token = secrets.token_hex(32)

# ok: bugledger-insecure-random-py
code = secrets.token_urlsafe(16)
