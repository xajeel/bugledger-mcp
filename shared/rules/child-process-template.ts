import { exec, execFile, execSync } from "node:child_process";
import * as child_process from "child_process";

const filename: string = "report.pdf";

// ruleid: bugledger-child-process-template
exec(`convert ${filename}`);

// ruleid: bugledger-child-process-template
execSync(`cat ${filename}`);

// ruleid: bugledger-child-process-template
child_process.exec(`open ${filename}`);

// ok: bugledger-child-process-template
exec("date");

// ok: bugledger-child-process-template
execFile("convert", [filename]);

// ok: bugledger-child-process-template
child_process.spawn("open", [filename]);
