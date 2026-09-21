import tempfile
from tempfile import mktemp


# ruleid: bugledger-tempfile-mktemp
path = tempfile.mktemp()

# ruleid: bugledger-tempfile-mktemp
archive_path = tempfile.mktemp(prefix="archive-", suffix=".zip")

# ruleid: bugledger-tempfile-mktemp
legacy_path = mktemp()

# ok: bugledger-tempfile-mktemp
fd, path = tempfile.mkstemp()

# ok: bugledger-tempfile-mktemp
with tempfile.NamedTemporaryFile() as output:
    output.write(b"safe")

# ok: bugledger-tempfile-mktemp
with tempfile.TemporaryDirectory() as directory:
    use(directory)
