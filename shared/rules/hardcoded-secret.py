import os

# ruleid: bugledger-hardcoded-secret
API_KEY = "sk-proj-abcdefghijklmnop1234"

# ruleid: bugledger-hardcoded-secret
password = "mysupersecretpassword123"

# ruleid: bugledger-hardcoded-secret
client_secret = "AKIAIOSFODNN7EXAMPLE1"

# ruleid: bugledger-hardcoded-secret
api_key = 'sk-live-abcdefghijklmnop'

# ok: bugledger-hardcoded-secret
password = os.environ["PASSWORD"]

# ok: bugledger-hardcoded-secret
api_key = get_secret("api_key")

# ok: bugledger-hardcoded-secret
password = ""

# ok: bugledger-hardcoded-secret
client_secret = "your-oidc-client-secret"

# ok: bugledger-hardcoded-secret
password = "<your password here>"

# ok: bugledger-hardcoded-secret
api_key = "changeme-before-deploy"

# ok: bugledger-hardcoded-secret
client_secret = "abc123..."

# ok: bugledger-hardcoded-secret
client_secret = "my-client-secret"

# ok: bugledger-hardcoded-secret
password = 'password1'
