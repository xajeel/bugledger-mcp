const cors = require("cors");

// ruleid: bugledger-cors-allow-all
app.use(cors({ origin: "*" }));

// ruleid: bugledger-cors-allow-all
res.setHeader("Access-Control-Allow-Origin", "*");

// ok: bugledger-cors-allow-all
app.use(cors({ origin: "https://myapp.com" }));

// ok: bugledger-cors-allow-all
res.setHeader("Access-Control-Allow-Origin", "https://myapp.com");
