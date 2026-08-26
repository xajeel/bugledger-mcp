const crypto = require("crypto");

// ruleid: bugledger-insecure-random-js
var token = Math.random();

// ok: bugledger-insecure-random-js
var token = crypto.randomUUID();
