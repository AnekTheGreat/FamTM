// ---- the tree, drawn for the PDF -------------------------------------------------------------
// Everything the Map draws -- every family box, every name, every photo, every connector -- as one
// SVG, at the exact geometry the layout engine gives it and on white so it prints. The panel's own
// column widths are put back afterwards, so exporting never disturbs the view you are looking at.
function treeSVG(){
 const full=build();
 const keep=[TW,TH,TGX,TGY,CW];
 let L=null;
 try{TW=176;TH=72;TGX=28;TGY=56;CW=140;L=tlayout(full)}finally{[TW,TH,TGX,TGY,CW]=keep}
 const W=L.W,H=L.H,edges=L.edges,nodes=L.nodes,pos=L.pos;
 const x2=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
 const F='Helvetica,Arial,sans-serif';
 const out=[`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#ffffff"/>`];
 // the connectors first, drawn behind the boxes, on exactly the same formula as the page uses
 edges.forEach(e=>{const a=e[0],b=e[1],x1=edgeX(a,e.rel.map(r=>r[0])),y1=a.py+(a.h||TH),x2b=edgeX(b,e.rel.map(r=>r[1])),y2=b.py+(b.mem&&b.mem.length>1?3:0),my=(y1+y2)/2;
  out.push(`<path d="M${x1} ${y1} V${my} H${x2b} V${y2}" fill="none" stroke="#9fadbb" stroke-width="1.2"/>`)});
 let clip=0;
 nodes.forEach(n=>{const o=pos.get(n),rows=n.mem.length>MAXROW?[...n.mem.slice(0,MAXROW-1),null]:n.mem,cards=[];
  out.push(`<rect x="${o.px}" y="${o.py}" width="${o.w}" height="${o.h}" rx="10" fill="#ffffff" stroke="#c2ccd7"/>`);
  rows.forEach((x,i)=>{const cw=o.cw,cx=o.px+o.il+i*(cw+COLGAP),cy=o.py+8,ch=o.h-16;
   if(!x){cards.push(null);out.push(`<text x="${cx+cw/2}" y="${cy+ch/2+4}" font-family="${F}" font-size="11" fill="#98a5b3" text-anchor="middle">+${n.mem.length-MAXROW+1} more</text>`);return}
   cards.push({cx,cw,cy,ch,x});
   const ph=x.photo?AVW:0;
   out.push(`<rect x="${cx}" y="${cy}" width="${cw}" height="${ch}" rx="8" fill="#f1f5f8" stroke="#dde5ec"/>`);
   if(ph){const id='cl'+(++clip);
    out.push(`<clipPath id="${id}"><rect x="${cx+3}" y="${cy+(ch-34)/2}" width="34" height="34" rx="6"/></clipPath>`);
    out.push(`<image x="${cx+3}" y="${cy+(ch-34)/2}" width="34" height="34" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})" href="${x2(x.photo)}" xlink:href="${x2(x.photo)}"/>`)}
   // The name is wrapped into the one or two lines the box was measured for, with the years after it.
   const nx0=cx+(ph?AVW:5),tw=Math.max(24,cw-(ph?AVW:5)-4),cpl=Math.max(5,Math.floor(tw/6.8));
   const nm=x.name+(x.nick?' (\u201c'+x.nick+'\u201d)':'');
   const lines=nm.length>cpl?split2(nm,cpl):[nm];
   const dt=life(x),last=lines[lines.length-1];
   const inline=dt&&(last.length*6.2+10+dt.length*4.6<=tw);
   if(dt&&!inline)lines[lines.length-1]=last;
   const block=lines.length*13+((dt&&!inline)?11:0);
   let ty=cy+(ch-block)/2+10;
   lines.forEach((ln,k)=>{const withDates=inline&&k===lines.length-1;
    out.push(`<text x="${nx0}" y="${ty}" font-family="${F}" font-size="11" fill="#1d2a38">${x2(ln)}</text>`);
    if(withDates)out.push(`<text x="${nx0+last.length*6.2+8}" y="${ty}" font-family="${F}" font-size="8.5" fill="#7b8896">${x2(dt)}</text>`);
    ty+=13});
   if(dt&&!inline)out.push(`<text x="${nx0}" y="${ty}" font-family="${F}" font-size="8.5" fill="#7b8896">${x2(dt)}</text>`)});
  // one bar per marriage, between the two partners' own cards, as the page draws it
  for(let i=0;i<cards.length;i++)for(let j=i+1;j<cards.length;j++){const a=cards[i],b=cards[j];
   if(a&&b&&a.x.partners.includes(b.x.id))out.push(`<path d="M${a.cx+a.cw} ${a.cy+a.ch/2} H${b.cx}" fill="none" stroke="#b4c0cc" stroke-width="2.5"/>`)}
 });
 out.push('</svg>');
 return {svg:out.join(''),W,H};
}
// A name too long for its column goes on a second line, split at a word like the browser would
const split2=(t,cpl)=>{const w=String(t).split(' ');let a='',b='';for(const p of w){if(!b&&((a?a.length+1:0)+p.length)<=cpl)a=a?a+' '+p:p;else b=b?b+' '+p:p}return b?[a,b]:[a]};
// An SVG as a JPEG, drawn k times its size so the names stay sharp when the page prints them.
const svgShot=(svg,w,h,k)=>new Promise((res,rej)=>{const im=new Image();
 im.onload=()=>{const cv=document.createElement('canvas');cv.width=Math.max(1,Math.round(w*k));cv.height=Math.max(1,Math.round(h*k));
  const g=cv.getContext('2d');g.fillStyle='#ffffff';g.fillRect(0,0,cv.width,cv.height);g.drawImage(im,0,0,cv.width,cv.height);
  try{res({jpg:cv.toDataURL('image/jpeg',.9),w:cv.width,h:cv.height})}catch(e){rej(e)}};
 im.onerror=()=>rej(new Error('the tree could not be drawn'));
 im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg)});
// The export: page one is the family as it is really drawn, then the two lists as before.
async function pdf(){
 if(!P.length)return say('Nothing to export');
 let shot=null;
 try{const g=treeSVG();shot=await svgShot(g.svg,g.W,g.H,Math.min(2,Math.max(1,1800/g.W)))}catch(e){shot=null}
 const W=595,H=842,mg=44,pages=[],o=[],kids=[];
 let nx=5;
 const put=s=>{const i=nx++;o[i]=s;return i};
 const addP=(w,h,ops,res)=>pages.push({w,h,ops,res:res||''});
 // --- the family, drawn: whichever way round the page fits it bigger ---
 if(shot){
  const portrait={w:595,h:842},land={w:842,h:595};
  const fit=p=>Math.min((p.w-2*mg)/shot.w,(p.h-mg-46-mg)/shot.h);
  const pg=fit(portrait)>fit(land)?portrait:land,k=fit(pg),dw=shot.w*k,dh=shot.h*k;
  const bin=atob(shot.jpg.split(',')[1]);
  const im=put(`<</Type/XObject/Subtype/Image/Width ${shot.w}/Height ${shot.h}/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/DCTDecode/Length ${bin.length}>>\nstream\n${bin}\nendstream`);
  addP(pg.w,pg.h,[
   `BT /F2 17 Tf 1 0 0 1 ${mg} ${pg.h-46} Tm (Family Tree) Tj ET`,
   `BT /F1 9 Tf 1 0 0 1 ${mg} ${pg.h-62} Tm (${esc(P.length+' people  -  the whole family, as drawn  -  '+new Date().toLocaleDateString())}) Tj ET`,
   `q ${dw.toFixed(1)} 0 0 ${dh.toFixed(1)} ${((pg.w-dw)/2).toFixed(1)} ${(mg).toFixed(1)} cm /Im1 Do Q`
  ],`/XObject<</Im1 ${im} 0 R>>`);
 }
 // --- the lists, exactly as they were ---
 let cur=[],y=H-mg;
 const chk=()=>{if(y<mg+10){addP(W,H,cur);cur=[];y=H-mg}};
 const T=(t,x,s,b)=>cur.push(`BT /F${b?2:1} ${s} Tf 1 0 0 1 ${x.toFixed(1)} ${y} Tm (${esc(t)}) Tj ET`);
 if(!shot){T('Family Tree',mg,22,1);y-=24;T(P.length+' people  -  '+new Date().toLocaleDateString(),mg,9);y-=26}
 T('Descendant tree',mg,13,1);y-=20;
 const seen=new Set();
 const walk=(n,d)=>{if(seen.has(n.p.id))return;seen.add(n.p.id);chk();const x=mg+Math.min(d,24)*14,nm=n.p.name+n.ps.map(z=>' & '+z.name).join(''),l=life(n.p);T(nm,x,10,1);l&&T(l,x+Math.min(nm.length,60)*5.9+8,9);y-=15;n.kids.forEach(k=>walk(k,d+1))};
 build().forEach(n=>walk(n,0));
 y-=14;chk();T('Everyone (A-Z)',mg,13,1);y-=20;
 [...P].sort((a,b)=>a.name.localeCompare(b.name)).forEach(p=>{chk();T(p.name+(p.nick?' ('+p.nick+')':''),mg,9);T((p.birth?'b. '+fmt(p.birth):'')+(p.death?'    d. '+fmt(p.death):''),mg+300,9);y-=13});
 addP(W,H,cur);
 pages.forEach((p,i)=>p.ops.push(`BT /F1 8 Tf 1 0 0 1 ${p.w/2-30} 24 Tm (Page ${i+1} of ${pages.length}) Tj ET`));
 pages.forEach(p=>{const body=p.ops.join('\n');
  const ci=put(`<</Length ${body.length}>>\nstream\n${body}\nendstream`);
  kids.push(put(`<</Type/Page/Parent 2 0 R/MediaBox[0 0 ${p.w} ${p.h}]/Resources<</Font<</F1 3 0 R/F2 4 0 R>>${p.res}>>/Contents ${ci} 0 R>>`))});
 o[1]='<</Type/Catalog/Pages 2 0 R>>';
 o[2]=`<</Type/Pages/Kids[${kids.map(i=>i+' 0 R').join(' ')}]/Count ${kids.length}>>`;
 o[3]='<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>';
 o[4]=o[3].replace('Helvetica','Helvetica-Bold');
 const size=nx;
 let f='%PDF-1.4\n';const off=[];
 for(let i=1;i<size;i++){off[i]=f.length;f+=`${i} 0 obj\n${o[i]}\nendobj\n`}
 const x=f.length;f+=`xref\n0 ${size}\n0000000000 65535 f \n`+off.slice(1).map(v=>String(v).padStart(10,'0')+' 00000 n \n').join('')+`trailer\n<</Size ${size}/Root 1 0 R>>\nstartxref\n${x}\n%%EOF`;
 dl(new Blob([Uint8Array.from(f,c=>c.charCodeAt(0))],{type:'application/pdf'}),'family-tree.pdf');say('PDF exported')}
