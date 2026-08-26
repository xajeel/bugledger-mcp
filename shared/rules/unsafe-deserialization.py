import json
import pickle
import yaml

data = b"some bytes"

# ruleid: bugledger-unsafe-deserialize-py
obj = pickle.loads(data)

# ruleid: bugledger-unsafe-deserialize-py
obj = yaml.load(raw_yaml)

# ok: bugledger-unsafe-deserialize-py
obj = json.loads(data)

# ok: bugledger-unsafe-deserialize-py
obj = yaml.safe_load(raw_yaml)
