// Reproduces the v1.0.3 change from a pristine FamTM checkout.
// Run from the repository root:  node apply-pdf.mjs <repo-root> <payload-dir>
// It needs pdf-new.js (the new exporter), notes-v103.md and wn-v103.json beside it.
import fs from 'fs';
import path from 'path';
import { createHash } from 'crypto';

const root = process.argv[2] || '.';
const payload = process.argv[3] || path.dirname(new URL(import.meta.url).pathname);
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const write = (p, s) => fs.writeFileSync(path.join(root, p), s);
const must = (ok, what) => { if (!ok) throw new Error('anchor not found: ' + what); };
const sha = s => createHash('sha256').update(s).digest('hex').slice(0, 12);

let html = read('index.html');
console.log('pristine index.html:', html.length, 'bytes', sha(html));

// 1. the exporter, in place of the one that wrote only text
const block = fs.readFileSync(path.join(payload, 'pdf-new.js'), 'utf8');
const from = html.indexOf('function pdf(){');
must(from > 0, 'function pdf(){');
const marker = "'family-tree.pdf');say('PDF exported')}";
const at = html.indexOf(marker, from);
must(at > from, 'the end of the old exporter');
const end = at + marker.length;
must(!html.slice(end).includes('function pdf(){'), 'only one exporter');
html = html.slice(0, from) + block.trimEnd() + html.slice(end);
console.log('  exporter replaced');

// 2. the page carries its own version
const verFrom = "const VER='1.0.2'";
must(html.includes(verFrom), "const VER='1.0.2'");
html = html.replace(verFrom, "const VER='1.0.3'");
console.log('  VER -> 1.0.3');

// 3. the page's own What's New list gains this update at its top
const entry = JSON.parse(fs.readFileSync(path.join(payload, 'wn-v103.json'), 'utf8'));
const re = /(<script id="upd" type="application\/json">)([\s\S]*?)(<\/script>)/;
const m = re.exec(html);
must(m, 'the upd block');
const list = JSON.parse(m[2]);
const json = JSON.stringify([entry, ...list])
  .replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
html = html.replace(re, `$1${json}$3`);
console.log('  upd:', list.length, '->', list.length + 1, 'updates, newest', entry.v);

write('index.html', html);
console.log('index.html:', html.length, 'bytes', sha(html));

// 4. the page the app updates itself from is the same bytes as the page in the repo
const assets = 'app/src/main/assets/index.html';
write(assets, html);
must(read(assets) === read('index.html'), 'the two copies agree');
console.log('  copied to ' + assets + ' (identical)');

// 5. PATCH_NOTES.md gains the section
const section = fs.readFileSync(path.join(payload, 'notes-v103.md'), 'utf8');
const notes = read('PATCH_NOTES.md');
must(!notes.includes('\u2014 v1.0.3:'), 'the v1.0.3 section is already there');
const nAnchor = '\n## 2026-10-13 \u2014 v1.0.2:';
const nAt = notes.indexOf(nAnchor);
must(nAt > 0, 'the v1.0.2 section');
const notesOut = notes.slice(0, nAt + 1) + section + notes.slice(nAt + 1);
write('PATCH_NOTES.md', notesOut);
console.log('PATCH_NOTES.md:', notes.length, '->', notesOut.length, 'bytes');

// 6. the page's own self-check: the archive in the page really holds this update
const check = JSON.parse(/<script id="upd" type="application\/json">([\s\S]*?)<\/script>/.exec(read('index.html'))[1]);
must(check[0].v === '1.0.3' && check[0].x.length === entry.x.length, 'the newest update is in the page');
must(read('index.html') === read(assets), 'the two copies still agree');
console.log('self-check ok: page v' + check[0].v + ', ' + check.length + ' updates, both copies identical');
