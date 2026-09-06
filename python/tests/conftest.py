import os
import tempfile

# Safety net: no test may ever touch the developer's real ~/.bugledger.
os.environ.setdefault("BUGLEDGER_HOME", tempfile.mkdtemp(prefix="bugledger-tests-"))
