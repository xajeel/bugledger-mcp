import json
import pickle

data = b"some bytes"

# ruleid: bugledger-unsafe-deserialize-py
obj = pickle.loads(data)

# ok: bugledger-unsafe-deserialize-py
obj = json.loads(data)
