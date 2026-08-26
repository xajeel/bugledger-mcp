import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
user_id = "1"

# ruleid: bugledger-sql-injection-py
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ruleid: bugledger-sql-injection-py
cursor.execute("SELECT * FROM users WHERE id = " + user_id + "")

# ok: bugledger-sql-injection-py
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
