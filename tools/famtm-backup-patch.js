// One-off: applies the "export everything / import into what is here" change to the FamTM page.
//
// The page is 120 KB of hand-written JS in one file, so it is edited by anchors rather than copied:
// every anchor below must appear exactly once, and the result is checked before anything is written.
// If the page has moved on, this fails loudly and changes nothing.
const fs = require('fs');

const F = 'app/src/main/assets/index.html';
let s = fs.readFileSync(F, 'utf8');
const was = s.length;

function swap(start, end, text, label) {
  const i = s.indexOf(start);
  if (i < 0) throw new Error('start not found: ' + label);
  if (s.indexOf(start, i + 1) >= 0) throw new Error('start is not unique: ' + label);
  const j = s.indexOf(end, i);
  if (j < 0) throw new Error('end not found: ' + label);
  s = s.slice(0, i) + text + s.slice(j + end.length);
}

function insertBefore(anchor, text, label) {
  if (s.split(anchor).length !== 2) throw new Error('anchor is not unique: ' + label);
  s = s.replace(anchor, () => text + anchor);
}

// 1. the two menu rows say what they now do
swap('data-act="json">Backup (JSON)', 'Restore from backup</button>',
 'data-act="json">Export everything</button><button class="btn" data-act="restore">Import a backup</button>', 'menu labels');

// 2. the exported file carries the settings as well as the people and notes
swap("json:()=>{D.close();dl(new Blob([JSON.stringify({v:3,", "'family-tree-backup.json')},",
 "json:()=>{D.close();dl(new Blob([JSON.stringify({v:3,app:'family-tree',at:new Date().toISOString(),people:P,notes:N,settings:{autopar:autoOn(),bdays:bdOn(),seen:seenVer()}})],{type:'application/json'}),'family-tree-backup.json');say('Exported '+P.length+' people, '+N.length+' notes and your settings')},", 'export action');

// 3. the two answers an imported file is offered
insertBefore(" restore:()=>$('#file').click(),", [
" bakadd:()=>{const b=bak;bak=null;D.close();if(!b)return;",
"  const m=mergeIn(P,b.people),q=bakNotesAdd(N,b.notes);P=m.people;N=q.notes;commit();",
"  say('Added '+m.add.length+' people'+(m.same?' \u2013 '+m.same+' were already here':'')+(q.add.length?' and '+q.add.length+' notes':'')+(b.settings?' \u2013 your settings are unchanged':''))},",
" bakrep:()=>{const b=bak;bak=null;D.close();if(!b)return;P=b.people;N=b.notes;",
"  const st=b.settings;",
"  if(st){if(typeof st.autopar=='boolean')autoSet(st.autopar);if(typeof st.bdays=='boolean')bdSet(st.bdays);if(st.seen)try{localStorage.setItem(KEY+'.ver',str(st.seen))}catch(e){}}",
"  commit();say('Restored '+P.length+' people'+(N.length?' and '+N.length+' notes':''))},"].join('\n'), 'new actions');

// 4. the reader: one file, two answers
swap("$('#file').onchange=async e=>{", "catch(err){say('Not a valid backup file')}};", [
"// ---- Importing a backup -----------------------------------------------------",
"// One reader for every backup this app has ever made and one for the file it writes now: people (each",
"// with their photo, dates, note and links), the notes list, and the settings this phone had. The shape",
"// has only ever grown fields, so a backup from any earlier version lands here, and an older version of",
"// the app simply ignores what it does not know.",
"let bak=null;                                    // the file just read, waiting to hear what to do with it",
"const bakPeople=a0=>arr(Array.isArray(a0)?a0:a0&&a0.people).filter(x=>x&&(x.name||x.nick)).map(normPerson);",
"const bakNotes=a0=>arr(a0&&a0.notes).filter(x=>x&&x.t).map(x=>({id:str(x.id)||uid(),t:str(x.t)}));",
"// A link that points at someone the file does not carry is dropped rather than left pointing at a stranger,",
"// and nobody is ever their own parent or partner.",
"const bakTidy=n=>{const ids=new Set(n.map(x=>x.id));n.forEach(x=>{",
" x.parents=[...new Set(x.parents)].filter(i=>ids.has(i)&&i!==x.id).slice(0,2);",
" x.partners=[...new Set(x.partners)].filter(i=>ids.has(i)&&i!==x.id);",
" if(x.sibs){x.sibs=[...new Set(x.sibs)].filter(i=>ids.has(i)&&i!==x.id);if(!x.sibs.length)delete x.sibs}});return n};",
"// Adding a file to a family that is already here. An id is made from the clock and never repeats, so",
"// anyone this phone already has is the same person and is left exactly as they are \u2014 which is what keeps",
"// the same file from being added twice. Everyone else comes in with the links they arrived with, and those",
"// links are then crossed with the family already here, so a wife the file knows about and a child this",
"// phone already had end up in one family instead of two.",
"function mergeIn(cur,imp){",
" const have=new Set(cur.map(p=>p.id)),add=imp.filter(p=>!have.has(p.id));",
" const all=cur.concat(add),ids=new Set(all.map(p=>p.id));",
" add.forEach(p=>{p.parents=p.parents.filter(i=>ids.has(i)&&i!==p.id);p.partners=p.partners.filter(i=>ids.has(i)&&i!==p.id);",
"  if(p.sibs){p.sibs=p.sibs.filter(i=>ids.has(i)&&i!==p.id);if(!p.sibs.length)delete p.sibs}});",
" return{people:all,add,same:imp.length-add.length}}",
"const bakNotesAdd=(cur,imp)=>{const have=new Set(cur.map(n=>n.id)),add=imp.filter(n=>!have.has(n.id));",
" return{notes:cur.concat(add),add,same:imp.length-add.length}};",
"$('#file').onchange=async e=>{const f=e.target.files[0];e.target.value='';if(!f)return;",
" try{const a0=JSON.parse(await f.text()),n=bakTidy(bakPeople(a0)),nn=bakNotes(a0);",
"  if(!n.length&&!nn.length){say('That backup has nobody in it');return}",
"  const st=a0&&a0.settings&&typeof a0.settings=='object'?a0.settings:null;",
"  bak={people:n,notes:nn,settings:st};",
"  show(`<h2>Import a backup</h2><p class=\"m\">This file holds ${n.length} people${nn.length?' and '+nn.length+' note'+(nn.length==1?'':'s'):''}${st?' and the settings of the phone it was written on':''}.</p><p class=\"m\"><b>Add</b> brings in everyone who is not already here and leaves your ${P.length} people exactly as they are.<br><b>Replace</b> throws this family away and puts the backup in its place.</p><div class=\"menu\"><button class=\"btn p\" data-act=\"bakadd\">Add to my family</button><button class=\"btn d\" data-act=\"bakrep\">Replace everything</button><button class=\"btn\" data-act=\"close\">Cancel</button></div>`)",
" }catch(err){say('Not a valid backup file')}};"].join('\n'), 'import reader');

// Nothing is written unless the page really came out with all of it.
const must = [
  'data-act="json">Export everything<',
  'data-act="restore">Import a backup<',
  "settings:{autopar:autoOn(),bdays:bdOn(),seen:seenVer()}",
  'function mergeIn(cur,imp){',
  'const bakNotesAdd=',
  'data-act="bakadd"',
  'data-act="bakrep"',
  'bak={people:n,notes:nn,settings:st};',
];
for (const m of must) if (!s.includes(m)) throw new Error('missing after patch: ' + m);
if (s.length < was + 2000 || s.length > was + 6000) throw new Error('unexpected size: ' + s.length);
if (s.indexOf('Import a backup') !== s.lastIndexOf('Import a backup')) throw new Error('label written twice');

fs.writeFileSync(F, s);
console.log('patched ' + was + ' -> ' + s.length + ' bytes');
