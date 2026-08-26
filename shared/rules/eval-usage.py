import ast
import json

# ruleid: bugledger-eval-usage-py
result = eval(user_input)

# ruleid: bugledger-eval-usage-py
exec("print('hello')")

# ok: bugledger-eval-usage-py
result = ast.literal_eval(user_input)

# ok: bugledger-eval-usage-py
config = json.loads(raw)
