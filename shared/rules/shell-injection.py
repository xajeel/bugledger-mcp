import os
import subprocess
import shlex

filename = "report.pdf"

# ruleid: bugledger-shell-injection-py
os.system(f"rm -rf {filename}")

# ruleid: bugledger-shell-injection-py
os.system("convert " + filename + " output.png")

# ok: bugledger-shell-injection-py
subprocess.run(["rm", "-rf", filename])

# ok: bugledger-shell-injection-py
os.system(f"rm -rf {shlex.quote(filename)}")
