import httpx
import requests


# ruleid: bugledger-tls-verify-disabled
response = requests.get("https://api.example.com", verify=False)

# ruleid: bugledger-tls-verify-disabled
response = requests.request("POST", "https://api.example.com", verify=False)

# ruleid: bugledger-tls-verify-disabled
response = httpx.post("https://api.example.com", verify=False)

# ruleid: bugledger-tls-verify-disabled
client = httpx.Client(verify=False)

session = requests.Session()
# ruleid: bugledger-tls-verify-disabled
session.verify = False

# ok: bugledger-tls-verify-disabled
response = requests.get("https://api.example.com", verify=True)

# ok: bugledger-tls-verify-disabled
response = requests.get("https://api.example.com", verify=ca_bundle)

# ok: bugledger-tls-verify-disabled
client = httpx.Client(verify=ssl_context)

# ok: bugledger-tls-verify-disabled
unrelated.verify = False
