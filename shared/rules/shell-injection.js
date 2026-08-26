const child_process = require("child_process");

var filename = "report.pdf";

// ruleid: bugledger-shell-injection-js
child_process.exec(`rm -rf ${filename}`);

// ok: bugledger-shell-injection-js
child_process.execFile("rm", ["-rf", filename]);
