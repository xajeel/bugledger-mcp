import jwt
from jose import jwt as jose_jwt

token = "header.payload.signature"
key = "public-key"

# ruleid: bugledger-jwt-alg-none
jwt.decode(token, key, algorithms=["none"])

# ruleid: bugledger-jwt-alg-none
jwt.decode(token, key, algorithms=["RS256", "none"])

# ruleid: bugledger-jwt-alg-none
jose_jwt.decode(token, key, algorithms=("none", "RS256"))

# ok: bugledger-jwt-alg-none
jwt.decode(token, key, algorithms=["RS256"])

# ok: bugledger-jwt-alg-none
jose_jwt.decode(token, key, algorithms=("ES256",))

# ok: bugledger-jwt-alg-none
jwt.encode({"sub": "123"}, key, algorithm="none")
