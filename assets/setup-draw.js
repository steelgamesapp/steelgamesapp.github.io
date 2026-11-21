/* SteelGames desk setup drawings. Shared by the Desk Setup Builder (/setups/) in the browser and by
   tools/render_setups.js, which saves a picture of every finished setup to assets/setups/draw/.
   Option ids here must match data/setup_builder.json. */
(function(root){
'use strict';
function make(D){
let S;
const colorHex=id=>(D.colors.find(c=>c.id===id)||D.colors[0]).hex;
const has=x=>S.x.includes(x);
function shade(hex,a){return hex+Math.round(a*255).toString(16).padStart(2,'0');}
function wallpaper(x,y,w,h,id){
  const c=colorHex(S.color);
  return `<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="0 0 400 225" preserveAspectRatio="none">
  <defs><linearGradient id="sky${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1042"/><stop offset=".6" stop-color="${c}"/><stop offset="1" stop-color="#ffd08a"/></linearGradient></defs>
  <rect width="400" height="225" fill="url(#sky${id})"/><circle cx="270" cy="130" r="34" fill="#ffe7b0" opacity=".9"/>
  <path d="M0 225 L0 150 L70 95 L130 140 L190 80 L260 150 L320 110 L400 160 L400 225Z" fill="#160d33" opacity=".85"/>
  <path d="M0 225 L0 185 L90 150 L170 190 L250 160 L330 195 L400 175 L400 225Z" fill="#0c0820"/></svg>`;
}
function screen(x,y,w,h,id,curve){
  const b=9, cv=curve||0;
  const frame=cv?`<path d="M${x} ${y+cv} Q${x+w/2} ${y-cv} ${x+w} ${y+cv} L${x+w} ${y+h-cv} Q${x+w/2} ${y+h+cv} ${x} ${y+h-cv}Z" fill="#0a0912"/>`
               :`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="6" fill="#0a0912"/>`;
  const clip=cv?`<clipPath id="cl${id}"><path d="M${x+b} ${y+cv+b} Q${x+w/2} ${y-cv+b} ${x+w-b} ${y+cv+b} L${x+w-b} ${y+h-cv-b} Q${x+w/2} ${y+h+cv-b} ${x+b} ${y+h-cv-b}Z"/></clipPath>`
               :`<clipPath id="cl${id}"><rect x="${x+b}" y="${y+b}" width="${w-2*b}" height="${h-2*b}" rx="2"/></clipPath>`;
  return frame+`<defs>${clip}</defs><g clip-path="url(#cl${id})">${wallpaper(x+b,y+b-cv,w-2*b,h-2*b+2*cv,id)}</g>`;
}
function monitorGeom(){
  switch(S.monitor){
    case 'curved':return [{x:355,y:128,w:490,h:262,c:12}];
    case 'ultra':return [{x:290,y:168,w:620,h:236,c:10}];
    case 'tv':return [{x:270,y:66,w:660,h:376,c:0}];
    case 'dual':return [{x:262,y:178,w:330,h:194,c:0},{x:608,y:178,w:330,h:194,c:0}];
    default:return [{x:405,y:150,w:390,h:224,c:0}];
  }
}
function drawRoom(){
  const c=colorHex(S.color), on=S.light!=='none';
  let s=`<defs><linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140f2a"/><stop offset="1" stop-color="#1d1638"/></linearGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#120e22"/><stop offset="1" stop-color="#07050f"/></linearGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="${c}" stop-opacity=".75"/><stop offset=".55" stop-color="${c}" stop-opacity=".22"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient></defs>
  <rect width="1200" height="600" fill="url(#wall)"/><rect y="600" width="1200" height="120" fill="url(#floor)"/>`;
  if(!on)return s+`<ellipse cx="600" cy="300" rx="520" ry="260" fill="#fff" opacity=".035"/>`;
  if(S.light==='strip')s+=`<ellipse cx="600" cy="430" rx="600" ry="250" fill="url(#glow)"/>`;
  if(S.light==='bars')s+=`<ellipse cx="380" cy="330" rx="260" ry="230" fill="url(#glow)"/><ellipse cx="820" cy="330" rx="260" ry="230" fill="url(#glow)"/>`;
  if(S.light==='hex'){
    s+=`<ellipse cx="215" cy="150" rx="260" ry="190" fill="url(#glow)"/>`;
    const hx=[[150,90],[210,90],[180,142],[240,142],[270,90],[120,142],[210,194]];
    hx.forEach(([cx,cy],i)=>{const r=30,pts=[0,1,2,3,4,5].map(k=>{const a=Math.PI/3*k+Math.PI/6;return (cx+r*Math.cos(a)).toFixed(1)+','+(cy+r*Math.sin(a)).toFixed(1);}).join(' ');
      s+=`<polygon points="${pts}" fill="${c}" opacity="${(0.55+0.4*((i*37)%7)/7).toFixed(2)}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>`;});
  }
  if(S.light==='lamp')s+=`<ellipse cx="80" cy="360" rx="300" ry="330" fill="url(#glow)"/><rect x="66" y="110" width="22" height="575" rx="11" fill="${c}"/><rect x="72" y="118" width="10" height="560" rx="5" fill="#fff" opacity=".55"/><ellipse cx="77" cy="690" rx="44" ry="9" fill="#2a2440"/>`;
  return s;
}
function drawDesk(){
  const T={black:['#2a2733','#16141d','#0e0d13'],white:['#f3f2f7','#d9d7e2','#bdbbc8'],wood:['#a8703f','#7d4f2b','#5d3a20'],stand:['#3b3a46','#2a2933','#1c1b23']}[S.desk];
  let legs='';
  if(S.desk==='stand')legs=`<rect x="240" y="566" width="26" height="136" fill="#4b4a57"/><rect x="934" y="566" width="26" height="136" fill="#4b4a57"/><rect x="200" y="700" width="106" height="12" rx="6" fill="#3a3946"/><rect x="894" y="700" width="106" height="12" rx="6" fill="#3a3946"/><rect x="980" y="548" width="40" height="12" rx="3" fill="#15141b"/><circle cx="1012" cy="554" r="3" fill="#5CE08A"/>`;
  else legs=`<path d="M128 566 H158 V708 H128Z" fill="${T[2]}"/><path d="M1042 566 H1072 V708 H1042Z" fill="${T[2]}"/>`;
  let s=legs+`<path d="M150 440 H1050 L1090 540 H110Z" fill="${T[0]}"/><rect x="110" y="540" width="980" height="26" rx="3" fill="${T[1]}"/>`;
  if(S.desk==='wood')s+=`<path d="M200 470 H980 M170 505 H1030" stroke="#5d3a20" stroke-opacity=".25" stroke-width="3"/>`;
  if(S.light==='strip'){const c=colorHex(S.color);s+=`<rect x="114" y="563" width="972" height="4" rx="2" fill="${c}"/><rect x="114" y="566" width="972" height="22" fill="${c}" opacity=".18"/>`;}
  return s;
}
function drawBars(){
  if(S.light!=='bars')return '';const c=colorHex(S.color);
  return [380,820].map(x=>`<rect x="${x-9}" y="292" width="18" height="158" rx="7" fill="#1c1a24"/><rect x="${x-5}" y="298" width="10" height="146" rx="5" fill="${c}"/><rect x="${x-2}" y="300" width="4" height="140" rx="2" fill="#fff" opacity=".6"/>`).join('');
}
function drawPlant(){
  if(!has('plant'))return '';
  return `<path d="M168 300 C150 330 150 380 172 420" stroke="#2f8f5b" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M176 290 C200 330 196 380 180 420" stroke="#3fb370" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M160 340 C130 350 130 390 170 420" stroke="#2a7d50" stroke-width="9" fill="none" stroke-linecap="round"/>
  <path d="M188 330 C220 340 214 390 182 420" stroke="#47c47b" stroke-width="9" fill="none" stroke-linecap="round"/>
  <path d="M150 418 H206 L198 466 H158Z" fill="#e8e3d8"/><rect x="148" y="414" width="60" height="9" rx="3" fill="#d7d0c2"/>`;
}
function drawSpeakers(){
  if(!has('spk'))return '';const w=S.desk==='white'?'#f7f7fb':'#22202b', d=S.desk==='white'?'#cfcdd9':'#0f0e14';
  return [[296,392],[864,392]].map(([x,y])=>`<rect x="${x}" y="${y}" width="44" height="76" rx="9" fill="${w}" stroke="${d}" stroke-width="2"/><circle cx="${x+22}" cy="${y+48}" r="13" fill="${d}"/><circle cx="${x+22}" cy="${y+48}" r="5" fill="#555"/><circle cx="${x+22}" cy="${y+18}" r="6" fill="${d}"/>`).join('');
}
function drawMonitor(){
  const g=monitorGeom();let s='';
  if(S.monitor==='dual')s+=`<rect x="592" y="250" width="16" height="210" fill="#1a1922"/><ellipse cx="600" cy="462" rx="64" ry="8" fill="#14131a"/>`;
  else{const m=g[0];s+=`<rect x="590" y="${m.y+m.h-20}" width="20" height="${462-(m.y+m.h-20)}" fill="#1a1922"/><path d="M548 456 H652 L668 470 H532Z" fill="#14131a"/>`;}
  g.forEach((m,i)=>{s+=screen(m.x,m.y,m.w,m.h,'m'+i,m.c);});
  const top=Math.min(...g.map(m=>m.y)), mid=600;
  if(has('lbar'))s+=`<path d="M${mid-150} ${top+8} L${mid+150} ${top+8} L${mid+230} ${top+140} L${mid-230} ${top+140}Z" fill="#fff6dc" opacity=".08"/><rect x="${mid-110}" y="${top-14}" width="220" height="13" rx="6" fill="#20202a"/><rect x="${mid-104}" y="${top-4}" width="208" height="3" rx="1.5" fill="#fff6dc"/>`;
  if(has('cam')){const cx=has('lbar')?mid+150:mid;s+=`<rect x="${cx-26}" y="${top-24}" width="52" height="24" rx="11" fill="#17161e"/><circle cx="${cx}" cy="${top-12}" r="7" fill="#33334a"/><circle cx="${cx}" cy="${top-12}" r="3" fill="#7aa2ff"/><rect x="${cx-8}" y="${top-1}" width="16" height="8" fill="#17161e"/>`;}
  return s;
}
function drawMat(){
  if(S.mat==='none')return '';const c=colorHex(S.color);
  const fill={black:'#0d0c12',rgb:'#0d0c12',felt:'#8d8b96',map:'#2a2540'}[S.mat];
  let s=`<path d="M292 466 H908 L926 532 H274Z" fill="${fill}"/>`;
  if(S.mat==='rgb')s+=`<path d="M292 466 H908 L926 532 H274Z" fill="none" stroke="${c}" stroke-width="4"/>`;
  if(S.mat==='felt')s+=`<path d="M292 466 H908 L926 532 H274Z" fill="none" stroke="#6f6d78" stroke-width="2" stroke-dasharray="3 4"/>`;
  if(S.mat==='map')s+=`<path d="M310 480 L420 500 L520 476 L640 510 L760 482 L900 515 M360 470 L380 530 M560 468 L540 530 M720 468 L760 530 M300 512 L900 494" stroke="${c}" stroke-opacity=".55" stroke-width="2" fill="none"/>`;
  return s;
}
function drawPC(){
  const c=S.light==='none'?'#9fb4ff':colorHex(S.color);
  if(S.pc==='black'||S.pc==='white'){
    const w=S.pc==='white', body=w?'#f1f0f6':'#17161e', edge=w?'#cfcde0':'#2b2a35';
    let fans='';[318,368,418].forEach(y=>{fans+=`<circle cx="992" cy="${y}" r="21" fill="none" stroke="${c}" stroke-width="5"/><circle cx="992" cy="${y}" r="6" fill="${c}" opacity=".8"/>`;});
    return `<rect x="936" y="268" width="112" height="212" rx="8" fill="${body}" stroke="${edge}" stroke-width="3"/><rect x="948" y="282" width="88" height="186" rx="5" fill="#0b0a12" opacity="${w?.82:.9}"/>${fans}<rect x="948" y="282" width="88" height="186" rx="5" fill="${c}" opacity=".12"/><rect x="944" y="478" width="16" height="6" fill="#0b0a10"/><rect x="1024" y="478" width="16" height="6" fill="#0b0a10"/>`;
  }
  if(S.pc==='console')return `<path d="M960 318 Q984 298 1008 318 L1012 472 H956Z" fill="#f4f4f8" stroke="#d8d7e2" stroke-width="2"/><rect x="978" y="314" width="12" height="160" rx="3" fill="#15141c"/><rect x="981" y="330" width="6" height="22" rx="3" fill="${c}"/><rect x="950" y="472" width="68" height="9" rx="4" fill="#15141c"/>`;
  if(S.pc==='handheld')return `<g transform="translate(1000 476) scale(1.3) translate(-1000 -476)"><path d="M940 470 H1060 L1052 482 H948Z" fill="#1b1a22"/><path d="M972 470 L986 436 H1014 L1028 470Z" fill="#24232d"/><rect x="908" y="372" width="184" height="84" rx="30" fill="${S.light==='none'?'#f1f0f6':'#1b1a22'}" stroke="#3a3946" stroke-width="3"/>${wallpaper(944,380,112,66,'hh')}<circle cx="928" cy="398" r="8" fill="#3a3946"/><circle cx="1072" cy="426" r="8" fill="#3a3946"/><circle cx="1066" cy="394" r="3.5" fill="${c}"/><circle cx="1078" cy="402" r="3.5" fill="#5ce08a"/><rect x="920" y="420" width="16" height="5" rx="2" fill="#3a3946"/><rect x="925.5" y="414.5" width="5" height="16" rx="2" fill="#3a3946"/></g>`;
  if(S.pc==='laptop')return `<path d="M918 398 H1058 L1052 494 H924Z" fill="#141319"/>${wallpaper(926,405,124,82,'lp')}<path d="M900 494 H1076 L1088 512 H888Z" fill="#26252f"/><rect x="960" y="500" width="56" height="6" rx="3" fill="#3a3946"/>`;
  return '';
}
function drawHeadset(){
  const st=has('stand'), col={black:['#1b1a22','#2e2c38'],white:['#f2f1f6','#cfcdd9']}[S.headset];
  let s='';
  if(st){const glow=S.light!=='none'?colorHex(S.color):'#8a86a8';s+=`<ellipse cx="240" cy="476" rx="38" ry="8" fill="#15141b"/><rect x="236" y="352" width="8" height="122" fill="#2c2b36"/><rect x="216" y="470" width="48" height="5" rx="2" fill="${glow}"/><path d="M214 352 Q240 338 266 352" stroke="#2c2b36" stroke-width="8" fill="none" stroke-linecap="round"/>`;}
  if(!col)return s;
  if(st)s+=`<path d="M198 380 Q198 322 240 322 Q282 322 282 380" stroke="${col[0]}" stroke-width="12" fill="none" stroke-linecap="round"/><rect x="186" y="372" width="30" height="58" rx="13" fill="${col[0]}" stroke="${col[1]}" stroke-width="3"/><rect x="264" y="372" width="30" height="58" rx="13" fill="${col[0]}" stroke="${col[1]}" stroke-width="3"/>`;
  else s+=`<path d="M196 470 Q240 430 284 470" stroke="${col[0]}" stroke-width="11" fill="none" stroke-linecap="round"/><ellipse cx="200" cy="474" rx="24" ry="13" fill="${col[0]}" stroke="${col[1]}" stroke-width="3"/><ellipse cx="280" cy="474" rx="24" ry="13" fill="${col[0]}" stroke="${col[1]}" stroke-width="3"/>`;
  return s;
}
function drawDeck(){
  if(!has('deck'))return '';const c=S.light==='none'?'#8fb4ff':colorHex(S.color);let k='';
  for(let r=0;r<2;r++)for(let i=0;i<4;i++)k+=`<rect x="${362+i*15}" y="${474+r*11}" width="11" height="8" rx="2" fill="${[c,'#ffb020','#5ce08a','#66c0f4'][(i+r)%4]}"/>`;
  return `<path d="M356 468 H424 L428 498 H352Z" fill="#111018"/>${k}`;
}
function drawKeyboard(){
  if(S.keyboard==='none')return '';
  const c=colorHex(S.color);
  const K={rgb:{x:420,w:300,body:'#121118',key:'#22212b',glow:true},tkl:{x:446,w:248,body:'#121118',key:'#2a2933'},white:{x:466,w:208,body:'#f1f0f6',key:'#ffffff',edge:'#d2d0dc'},retro:{x:446,w:248,body:'#d9ccad',key:'#efe6cf',mod:'#8e8a83',edge:'#b9ab8a'}}[S.keyboard];
  const y=484,h=40;let s=`<path d="M${K.x+6} ${y} H${K.x+K.w-6} L${K.x+K.w} ${y+h} H${K.x}Z" fill="${K.body}" ${K.edge?`stroke="${K.edge}" stroke-width="2"`:''}/>`;
  if(K.glow)s+=`<path d="M${K.x+6} ${y} H${K.x+K.w-6} L${K.x+K.w} ${y+h} H${K.x}Z" fill="${c}" opacity=".35"/>`;
  const cols=Math.round(K.w/17), rows=4;
  for(let r=0;r<rows;r++){const yy=y+4+r*9, inset=6-r*1.4;for(let i=0;i<cols;i++){const xx=K.x+inset+3+i*((K.w-2*inset-6)/cols);
    let f=K.key;if(K.mod&&(i===0||i===cols-1||r===3&&i%5===0))f=K.mod;if(K.glow&&(i+r)%3===0)f=shade(c,.85);
    s+=`<rect x="${xx.toFixed(1)}" y="${yy}" width="${((K.w-2*inset-6)/cols-2.2).toFixed(1)}" height="6.5" rx="1.4" fill="${f}"/>`;}}
  return s;
}
function drawMouse(){
  if(S.mouse==='none')return '';
  const c=colorHex(S.color), f={black:'#141319',white:'#f4f3f8',rgb:'#141319'}[S.mouse];
  const ln=S.mouse==='white'?'#c2c0cc':'#5a5868';
  let s=`<ellipse cx="790" cy="507" rx="23" ry="17" fill="#000" opacity=".35"/><ellipse cx="790" cy="505" rx="21" ry="15" fill="${f}" stroke="${ln}" stroke-width="2.5"/><path d="M790 490 V503" stroke="${ln}" stroke-width="2"/><ellipse cx="783" cy="498" rx="6" ry="3" fill="#fff" opacity=".18"/>`;
  if(S.mouse==='rgb')s+=`<ellipse cx="790" cy="505" rx="19" ry="14" fill="none" stroke="${c}" stroke-width="3"/><rect x="788" y="493" width="4" height="7" rx="2" fill="${c}"/>`;
  return s;
}
function drawController(){
  if(S.controller==='none')return '';const w=S.controller==='white';
  const body=w?'#f4f3f8':'#1a1920', acc=w?'#15141b':'#3a3946';
  return `<path d="M300 506 Q300 496 316 496 H372 Q388 496 388 506 L396 528 Q398 538 388 538 Q380 538 372 528 H316 Q308 538 300 538 Q290 538 292 528Z" fill="${body}" stroke="${w?'#cfcdd9':'#2d2c36'}" stroke-width="2"/>
  ${w?`<path d="M300 506 Q300 496 316 496 H330 L316 530 Q308 538 300 538 Q290 538 292 528Z" fill="#15141b" opacity=".85"/><path d="M388 506 Q388 496 372 496 H358 L372 530 Q380 538 388 538 Q398 538 396 528Z" fill="#15141b" opacity=".85"/>`:''}
  <circle cx="326" cy="512" r="6" fill="${acc}"/><circle cx="362" cy="520" r="6" fill="${acc}"/><circle cx="372" cy="506" r="3" fill="${w?'#66c0f4':'#5ce08a'}"/><circle cx="380" cy="512" r="3" fill="${w?'#ff6b8a':'#ff6b6b'}"/>`;
}
function drawMic(){
  if(!has('mic'))return '';
  return `<rect x="896" y="438" width="20" height="14" rx="3" fill="#1b1a22"/><path d="M906 440 L918 250 L812 300" stroke="#26252f" stroke-width="8" fill="none" stroke-linejoin="round"/><circle cx="918" cy="250" r="7" fill="#33323c"/><rect x="792" y="296" width="40" height="70" rx="18" fill="#1d1c24" stroke="#3a3946" stroke-width="3"/><path d="M798 312 H826 M798 324 H826 M798 336 H826" stroke="#4a4958" stroke-width="2"/>`;
}
function drawChair(){
  if(S.chair==='none')return '';const c=S.light==='none'?'#6a4df0':colorHex(S.color);
  if(S.chair==='mesh')return `<path d="M478 720 L470 600 Q470 572 500 570 H700 Q730 572 730 600 L722 720Z" fill="#2a2933"/><path d="M490 712 L484 604 Q484 586 504 584 H696 Q716 586 716 604 L710 712Z" fill="#3c3b47"/><path d="M500 600 H700 M496 630 H704 M494 660 H706 M492 690 H708 M540 590 V712 M600 586 V712 M660 590 V712" stroke="#23222b" stroke-width="2" opacity=".7"/>`;
  const w=S.chair==='white', body=w?'#f2f1f6':'#18171e', side=w?'#d7d5e0':'#0f0e14';
  return `<path d="M470 720 L456 612 Q452 578 488 572 L512 570 Q520 546 600 546 Q680 546 688 570 L712 572 Q748 578 744 612 L730 720Z" fill="${side}"/>
  <path d="M500 720 L492 614 Q490 590 514 586 Q530 562 600 562 Q670 562 686 586 Q710 590 708 614 L700 720Z" fill="${body}"/>
  <path d="M556 590 H644 L640 720 H560Z" fill="${c}" opacity=".9"/><rect x="560" y="570" width="80" height="26" rx="12" fill="${w?'#e2e0ea':'#26252e'}"/>`;
}

function drawFlag(){
  if(!has('flag'))return '';
  let s=`<rect x="914" y="96" width="206" height="122" rx="5" fill="#3b2a1c"/>`;
  for(let i=0;i<7;i++)s+=`<rect x="922" y="${104+i*15.4}" width="190" height="${i%2?15.4:15.4}" fill="${i%2?'#e9dfc8':'#9b3b33'}"/>`;
  s+=`<rect x="922" y="104" width="84" height="62" fill="#2d3a5c"/>`;
  for(let r=0;r<4;r++)for(let i=0;i<5;i++)s+=`<circle cx="${932+i*16+(r%2?8:0)}" cy="${114+r*14}" r="2.6" fill="#e9dfc8"/>`;
  return s+`<path d="M922 104 H1112 V212 H922Z" fill="#000" opacity=".12"/>`;
}
function drawWheel(){
  if(!has('wheel'))return '';const c=S.light==='none'?'#ff8a1a':colorHex(S.color);
  return `<rect x="566" y="520" width="68" height="46" rx="8" fill="#1b1a22" stroke="#33323c" stroke-width="2"/>
  <circle cx="600" cy="506" r="86" fill="none" stroke="#2c2b36" stroke-width="22"/><circle cx="600" cy="506" r="97" fill="none" stroke="${c}" stroke-width="3" opacity=".8"/><circle cx="600" cy="506" r="75" fill="none" stroke="#4a4958" stroke-width="2"/>
  <path d="M518 506 H682 M600 506 V586" stroke="#2c2b36" stroke-width="18" stroke-linecap="round"/><circle cx="600" cy="506" r="28" fill="#22212b" stroke="${c}" stroke-width="3"/>
  <rect x="595" y="412" width="10" height="16" rx="2" fill="${c}"/><circle cx="587" cy="500" r="4.5" fill="#ff6b6b"/><circle cx="613" cy="500" r="4.5" fill="#5ce08a"/>`;
}

return function(state){S=state;
  return drawRoom()+drawDesk()+drawBars()+drawFlag()+drawPlant()+drawSpeakers()+drawMonitor()+drawMat()+drawMic()+drawPC()+drawHeadset()+drawDeck()+drawKeyboard()+drawMouse()+drawController()+drawWheel()+drawChair();};
}
const api={make};
root.SetupDraw=api;
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
