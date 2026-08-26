import os

# ruleid: bugledger-hardcoded-secret
API_KEY = "sk-proj-abcdefghijklmnop1234"

# ruleid: bugledger-hardcoded-secret
password = "mysupersecretpassword123"

# ruleid: bugledger-hardcoded-secret
client_secret = "AKIAIOSFODNN7EXAMPLE1"

# ok: bugledger-hardcoded-secret
password = os.environ["PASSWORD"]

# ok: bugledger-hardcoded-secret
api_key = get_secret("api_key")

# ok: bugledger-hardcoded-secret
password = ""
