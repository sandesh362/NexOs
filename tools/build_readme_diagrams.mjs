import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const moduleOption = process.argv.indexOf('--sharp-module');
const sharp = require(moduleOption >= 0 ? process.argv[moduleOption + 1] : 'sharp');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'docs', 'assets');
await mkdir(out, { recursive: true });

const C = {
  bg: '#F4F7FA', paper: '#FFFFFF', ink: '#162B3D', muted: '#4C6375',
  line: '#CAD7E1', blue: '#1D5678', pale: '#E7F0F6', teal: '#146A65',
  tealPale: '#E2F0EC', navy: '#122D42', white: '#FFFFFF',
};

const esc = (s) => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
function text(x, y, content, size = 22, fill = C.ink, weight = 400, anchor = 'start') {
  const lines = Array.isArray(content) ? content : [content];
  return `<text x="${x}" y="${y}" fill="${fill}" font-family="Segoe UI, Arial, sans-serif" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}">${lines.map((l, i) => `<tspan x="${x}" dy="${i ? Math.round(size * 1.42) : 0}">${esc(l)}</tspan>`).join('')}</text>`;
}
function rect(x, y, w, h, fill = C.paper, stroke = C.line, r = 14) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
}
function card(x, y, w, h, title, detail, options = {}) {
  return rect(x, y, w, h, options.fill ?? C.paper)
    + text(x + 24, y + 38, title, options.titleSize ?? 24, C.ink, 650)
    + text(x + 24, y + 73, detail, options.size ?? 20, C.muted);
}
function line(points, options = {}) {
  const pts = points.map(p => p.join(',')).join(' ');
  return `<polyline points="${pts}" fill="none" stroke="${options.color ?? C.blue}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" ${options.dashed ? 'stroke-dasharray="8 7"' : ''} marker-end="url(#arrow)" ${options.both ? 'marker-start="url(#arrowStart)"' : ''}/>`;
}
function frame(title, subtitle, height, body, description) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="${height}" viewBox="0 0 1600 ${height}" role="img" aria-labelledby="title description">
    <title id="title">${esc(title)}</title><desc id="description">${esc(description)}</desc>
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="${C.blue}" stroke-width="1.5"/></marker>
      <marker id="arrowStart" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="${C.blue}" stroke-width="1.5"/></marker>
    </defs>
    ${rect(0, 0, 1600, height, C.bg, C.bg, 0)}
    ${text(64, 54, 'NEXOS  /  ARCHITECTURE BLUEPRINT', 17, C.blue, 650)}
    ${text(64, 108, title, 38, C.ink, 650)}
    ${text(64, 147, subtitle, 21, C.muted)}
    ${body}
    ${text(64, height - 27, 'Planned design  |  18 October 2026  |  Diagram describes the target system', 17, C.muted)}
  </svg>`;
}

let body = '';
body += rect(64, 193, 1472, 464, C.paper);
body += text(104, 294, 'NEXOS', 80, C.ink, 700);
body += text(108, 350, ['An AI assisted Linux desktop', 'for tasks with verified outcomes.'], 31, C.blue, 500);
body += text(108, 465, ['Native interface. Local engine. Controlled tools.', 'An Ubuntu foundation packaged as a bootable ISO.'], 22, C.muted);
body += rect(108, 536, 550, 65, C.navy, C.navy, 10);
body += text(383, 577, 'Request  >  Plan  >  Execute  >  Verify', 22, C.white, 500, 'middle');
body += card(830, 233, 654, 111, '01  Native desktop', ['Qt / PySide6 / QML and Linux session integration']);
body += card(830, 368, 654, 111, '02  Agent execution layer', ['Python engine, Ollama, permissions and task evidence'], { fill: C.pale });
body += card(830, 503, 654, 111, '03  Distribution delivery', ['Required ISO; offline demo and optional VM export']);
const overview = frame('The product we are building', 'Linux supplies the operating system foundation. NEXOS supplies the controlled AI workflow.', 740, body,
  'NEXOS is a planned Ubuntu based distribution with a native Qt desktop, Python agent engine and Ollama, packaged as bootable ISO media.');

body = rect(48, 178, 1504, 824, C.paper);
body += text(80, 213, 'NEXOS GUEST OPERATING SYSTEM  /  installed VM or native Linux', 17, C.blue, 650);
body += card(80, 245, 360, 132, 'Native desktop and CLI', ['Request, plan, approvals', 'Progress, history and evidence']);
body += card(530, 245, 580, 132, 'nexosd user service', ['Intent, typed plans and durable task graph', 'Specialist roles, scheduler and recovery'], { fill: C.pale });
body += card(1200, 245, 320, 132, 'Ollama service', ['One selected local model', 'Inference only']);
body += card(80, 490, 360, 132, 'SQLite and memory', ['Task state and provenance', 'Records, indexes and artifacts']);
body += card(530, 490, 580, 132, 'Permission broker', ['Tool schema, resource scope and action grant', 'No model output can grant authority'], { fill: C.tealPale });
body += card(1200, 490, 320, 132, 'Desktop keyring', ['OAuth and provider secrets', 'No credentials in prompts']);
body += card(80, 745, 360, 132, 'Sandboxed local tools', ['Granted files and diagnostics', 'No default network or root']);
body += card(530, 745, 580, 132, 'Deterministic connectors', ['Approved API operations and reconciliation', 'Google Calendar and Meet after the core']);
body += card(1200, 745, 320, 132, 'Verifier and audit', ['Observed postconditions', 'Evidence before success']);
body += line([[440, 310], [530, 310]], { both: true });
body += text(485, 292, 'IPC', 16, C.muted, 500, 'middle');
body += line([[1110, 310], [1200, 310]], { both: true });
body += text(1155, 292, 'Local API', 15, C.muted, 500, 'middle');
body += line([[820, 377], [820, 490]]);
body += text(838, 437, 'Every action', 17, C.muted);
body += line([[580, 377], [580, 431], [260, 431], [260, 490]], { both: true });
body += line([[650, 622], [650, 685], [260, 685], [260, 745]]);
body += line([[820, 622], [820, 745]]);
body += line([[1360, 622], [1360, 681], [1030, 681], [1030, 745]], { dashed: true });
body += line([[1110, 811], [1200, 811]]);
body += line([[260, 877], [260, 938], [1360, 938], [1360, 877]]);
body += text(300, 928, 'Tool results are checked independently; verification is recorded in the task journal.', 18, C.muted);
body += text(80, 982, 'Separate privileges for inference, local tools and external credentials. Optional cloud inference requires user choice.', 18, C.muted);
const architecture = frame('Runtime architecture inside NEXOS', 'A native desktop and user daemon coordinate tools; Ollama provides model inference.', 1080, body,
  'The native desktop communicates with nexosd over a private socket. Every action passes a permission broker before local tools or remote connectors. Model inference has no authority. A verifier records observable outcomes.');

body = '';
const positions = [64, 452, 840, 1228];
const w = 308;
const top = [
  ['01  Understand', ['Capture outcome and scope', 'Resolve required parameters']],
  ['02  Plan', ['Build a typed dependency graph', 'Use registered tool contracts']],
  ['03  Validate', ['Check schema, targets and budget', 'Reject unsafe or unknown tools']],
  ['04  Authorize', ['Check scope and live capabilities', 'Preview sensitive actions']],
];
for (let i = 0; i < 4; i++) body += card(positions[i], 220, w, 170, top[i][0], top[i][1], { titleSize: 25, size: 18, fill: i === 3 ? C.tealPale : C.paper });
for (let i = 0; i < 3; i++) body += line([[positions[i] + w, 305], [positions[i + 1], 305]]);
const bottom = [
  ['08  Report', ['Return verified outcomes', 'State partial or failed work']],
  ['07  Record', ['Persist evidence and task state', 'Retain memory with provenance']],
  ['06  Verify', ['Observe the real postcondition', 'A claim is not proof']],
  ['05  Execute', ['Schedule and lock resources', 'Use scoped adapters']],
];
for (let i = 0; i < 4; i++) body += card(positions[i], 510, w, 170, bottom[i][0], bottom[i][1], { titleSize: 25, size: 18, fill: i === 2 ? C.pale : C.paper });
body += line([[1382, 390], [1382, 510]]);
for (let i = 3; i > 0; i--) body += line([[positions[i], 595], [positions[i - 1] + w, 595]]);
body += rect(64, 743, 1472, 100, C.navy, C.navy);
body += text(96, 783, 'Failure handling is part of the workflow', 25, C.white, 650);
body += text(96, 819, 'Bound retries, checkpoint before writes, reconcile uncertain effects and stop safely on cancellation.', 21, C.white);
const workflow = frame('From a request to verified work', 'Sensitive operations require an exact action grant. Task success requires independent evidence.', 915, body,
  'Eight steps run from understand, plan, validate and authorize, through execution, independent verification, durable records and the user report. Retries and cancellation remain bounded.');

body = '';
body += card(64, 220, 420, 152, '01  Verified Ubuntu base', ['Exact Desktop ISO and checksum', 'Inherited kernel, boot assets and installer']);
body += card(590, 220, 420, 152, '02  NEXOS packages', ['Engine, Qt interface and integration', 'Versioned inputs and dependency lists']);
body += card(1116, 220, 420, 152, '03  Customize live image', ['Cubic on an Ubuntu builder', 'Overlays, services and first run setup']);
body += line([[484, 296], [590, 296]]);
body += line([[1010, 296], [1116, 296]]);
body += line([[1326, 372], [1326, 477]]);
body += card(1116, 477, 420, 152, '04  Assemble bootable ISO', ['SquashFS and ISO tooling', 'Model choice: setup or bundled demo'], { fill: C.pale });
body += card(590, 477, 420, 152, '05  Test both boot paths', ['Live session and clean installation', 'Eject ISO, reboot and check persistence']);
body += card(64, 477, 420, 152, '06  Release evidence', ['ISO, SHA256 and version manifests', 'Optional sanitized prebuilt VM export'], { fill: C.tealPale });
body += line([[1116, 553], [1010, 553]]);
body += line([[590, 553], [484, 553]]);
body += rect(64, 695, 1472, 116, C.paper);
body += text(96, 738, 'Core ISO', 25, C.ink, 650);
body += text(96, 774, 'Includes Ollama runtime; selects or downloads a model during setup.', 21, C.muted);
body += text(855, 738, 'Offline demo ISO', 25, C.ink, 650);
body += text(855, 774, 'Includes one tested model and local fixtures.', 21, C.muted);
const pipeline = frame('Build and deliver a bootable distribution', 'Build application packages first. Integrate the same packages into the required ISO release.', 885, body,
  'The release pipeline verifies the Ubuntu base, packages NEXOS, customizes the filesystem, assembles the bootable ISO, tests live and installed boot paths, and produces checksums and release evidence.');

const diagrams = {
  'nexos-overview': overview,
  'nexos-architecture': architecture,
  'nexos-task-workflow': workflow,
  'nexos-iso-pipeline': pipeline,
};
for (const [name, svg] of Object.entries(diagrams)) {
  await writeFile(path.join(out, `${name}.svg`), svg, 'utf8');
  await sharp(Buffer.from(svg)).png().toFile(path.join(out, `${name}.png`));
}
console.log(JSON.stringify({ outputDirectory: out, diagrams: Object.keys(diagrams), files: 8 }));
