const db = require("pg");
const userId = "1";

// ruleid: bugledger-sql-injection-js
db.query(`SELECT * FROM users WHERE id = ${userId}`);

// ruleid: bugledger-sql-injection-js
db.query("SELECT * FROM users WHERE id = " + userId + "");

// ok: bugledger-sql-injection-js
db.query("SELECT * FROM users WHERE id = $1", [userId]);
