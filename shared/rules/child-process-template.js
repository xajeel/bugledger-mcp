const child_process = require("child_process");
const { exec, execFile, execSync } = require("node:child_process");

const filename = "report.pdf";

// ruleid: bugledger-child-process-template
child_process.exec(`rm -rf ${filename}`);

// ruleid: bugledger-child-process-template
child_process.execSync("cat " + filename);

// ruleid: bugledger-child-process-template
require("child_process").exec(`open ${filename}`);

// ruleid: bugledger-child-process-template
exec(`convert ${filename}`);

// ruleid: bugledger-child-process-template
execSync(`cat ${filename}`);

// ok: bugledger-child-process-template
child_process.exec("date");

// ok: bugledger-child-process-template
child_process.execFile("rm", ["-rf", filename]);

// ok: bugledger-child-process-template
execFile("convert", [filename]);
