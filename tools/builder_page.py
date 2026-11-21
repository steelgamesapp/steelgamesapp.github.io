"""Desk Setup Builder (/setups/): visitors pick each part of a desk and see a drawn preview update live,
then shop every pick on Amazon at a budget, mid or premium tier.

Parts, options and Amazon picks live in data/setup_builder.json. The pictures are simple drawings made
in assets/setup-draw.js (shared with tools/render_setups.js); an option id there must match the JSON. Rebuild with
    python3 tools/builder_page.py
The finished-setup gallery that used to be here now lives at /setups/ideas/ (tools/setups_page.py).
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import layout  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = layout.SITE
TAG = "steelgames-20"

CSS = r"""
.sb-top{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin:0 0 14px}
.sb-top h1{margin:0}
.sb-top .lede{margin:6px 0 0;max-width:640px}
.sb-pre{display:flex;flex-wrap:wrap;gap:8px}
.sb-pre button,.sb-pre a,.sb-act button,.sb-act a{font:600 13px/1 var(--body);color:#fff;background:var(--raised);border:1px solid var(--line-strong);border-radius:999px;padding:9px 14px;cursor:pointer;text-decoration:none}
.sb-pre button:hover,.sb-pre a:hover,.sb-act button:hover,.sb-act a:hover{background:var(--line)}
.sb{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:20px;align-items:start}
.sb-stage{position:sticky;top:12px;z-index:5}
.sb-view{border-radius:18px;overflow:hidden;border:1px solid var(--line);background:#120d26;box-shadow:0 18px 50px rgba(0,0,0,.45)}
.sb-view svg{display:block;width:100%;height:auto}
.sb-note{font-size:12px;color:var(--muted);margin:8px 2px 0}
.sb-act{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.sb-act .go{background:var(--grad-cta);color:var(--accent-ink);border:0}
.sb-ctl{display:flex;flex-direction:column;gap:12px}
.sb-part{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.sb-part h2{font:700 13px/1.2 var(--body);letter-spacing:.06em;text-transform:uppercase;color:var(--steel);margin:0 0 9px}
.sb-opts{display:flex;flex-wrap:wrap;gap:7px}
.sb-opts button{display:inline-flex;align-items:center;gap:7px;font:600 14px/1 var(--body);color:#fff;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:10px;padding:9px 12px;cursor:pointer;min-height:40px}
.sb-opts button:hover{border-color:var(--line-strong)}
.sb-opts button[aria-pressed=true]{background:var(--chip);border-color:#9C86FF;box-shadow:0 0 0 2px rgba(156,134,255,.35)}
.sb-opts i{width:14px;height:14px;border-radius:50%;flex:none;border:1px solid rgba(255,255,255,.35)}
.sb-sw button{width:40px;height:40px;padding:0;justify-content:center;border-radius:50%}
.sb-sw button i{width:24px;height:24px;border:0}
.sb-sw button[aria-pressed=true]{background:transparent;box-shadow:0 0 0 3px #fff}
.sb-list{margin-top:26px}
.sb-list-h{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;margin:0 0 12px}
.sb-list-h h2{margin:0}
.sb-tier{display:inline-flex;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:3px}
.sb-tier button{font:600 13px/1 var(--body);color:var(--muted);background:none;border:0;border-radius:999px;padding:8px 12px;cursor:pointer}
.sb-tier button[aria-pressed=true]{background:var(--chip);color:#fff}
.sb-rows{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.sb-row{display:grid;grid-template-columns:auto minmax(0,1fr) auto auto;align-items:center;gap:12px;padding:10px 12px;border-radius:14px;background:var(--surface);border:1px solid var(--line)}
.sb-row .ic{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:var(--raised);font:700 13px/1 var(--body);color:var(--steel)}
.sb-row .k{display:block;font-size:12px;color:var(--muted)}
.sb-row .n{display:block;font-weight:600;color:#fff;overflow-wrap:anywhere}
.sb-row .sb-tier{padding:2px}.sb-row .sb-tier button{padding:6px 9px;font-size:12px}
.sb-row .buy{font:700 13px/1 var(--body);white-space:nowrap;color:var(--accent-ink);background:var(--grad-cta);border-radius:10px;padding:10px 13px;text-decoration:none}
.sb-foot{font-size:13px;color:var(--muted);margin:14px 2px 0}
.sb-toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);background:#fff;color:#111;font:600 14px/1 var(--body);padding:12px 16px;border-radius:999px;box-shadow:0 8px 30px rgba(0,0,0,.4);opacity:0;pointer-events:none;transition:opacity .2s;z-index:60}
.sb-toast.on{opacity:1}
@media (max-width:900px){
 .sb{grid-template-columns:minmax(0,1fr)}
 .sb-stage{top:0;margin:0 -16px;padding:8px 16px 6px;background:var(--bg);box-shadow:0 10px 18px -12px rgba(0,0,0,.7)}
 .sb-view{border-radius:14px}
 .sb-stage .sb-note,.sb-stage .sb-act{display:none}
 .sb-act.m{display:flex}
 .sb-row{grid-template-columns:auto minmax(0,1fr) auto;row-gap:8px}
 .sb-row .sb-tier{grid-column:2/3;justify-self:start}
}
@media (min-width:901px){.sb-act.m{display:none}}
@media (prefers-reduced-motion:reduce){.sb-toast{transition:none}}
"""

# Drawing + UI. DATA is injected as JSON. Every picture is drawn here; option ids match data/setup_builder.json.
JS = r"""
<script src="/assets/setup-draw.js"></script>
<script>
(()=>{
'use strict';
const D=window.SB_DATA, TAG='steelgames-20', TIERS=['budget','mid','premium'], TL={budget:'Budget',mid:'Mid',premium:'Premium'};
const svgEl=document.getElementById('sbsvg'), listEl=document.getElementById('sbrows'), ctl=document.getElementById('sbctl');
const parts=D.parts, extras=D.extras, byKey={}, partById={};
parts.forEach(p=>{byKey[p.key]=p;partById[p.id]=p;});
const colorHex=id=>(D.colors.find(c=>c.id===id)||D.colors[0]).hex;
let S={};

/* ---------- state <-> url ---------- */
function parse(str){
  const q=new URLSearchParams(str.replace(/^[#?]/,'')), s={x:[],o:{},t:'mid'};
  parts.forEach(p=>{
    const v=q.get(p.key);
    if(p.colors){s[p.id]=D.colors.some(c=>c.id===v)?v:null;}
    else s[p.id]=p.options.some(o=>o.id===v)?v:null;
  });
  (q.get('x')||'').split('.').forEach(x=>{if(extras.some(e=>e.id===x))s.x.push(x);});
  const t=q.get('t'); if(TIERS.includes(t))s.t=t;
  (q.get('o')||'').split('.').forEach(pair=>{const [k,v]=pair.split('-'); if(k&&TIERS.includes(v))s.o[k]=v;});
  return s;
}
function fill(s){const d=parse(D.default);parts.forEach(p=>{if(!s[p.id])s[p.id]=d[p.id];});return s;}
function ser(s){
  const q=[];parts.forEach(p=>q.push(p.key+'='+s[p.id]));
  q.push('x='+s.x.join('.'));q.push('t='+s.t);
  const o=Object.keys(s.o).filter(k=>s.o[k]!==s.t).map(k=>k+'-'+s.o[k]);
  if(o.length)q.push('o='+o.join('.'));
  return q.join('&');
}
function save(){try{history.replaceState(null,'','#'+ser(S));}catch(e){}}

/* ---------- drawing (assets/setup-draw.js) ---------- */
const drawAll=SetupDraw.make(D);
const has=x=>S.x.includes(x);
function draw(){
  svgEl.innerHTML=drawAll(S);
  svgEl.setAttribute('aria-label','Drawing of your desk setup: '+rows().map(r=>r.k).join(', '));
}

/* ---------- product list ---------- */
function link(p){return p.asin?`https://www.amazon.com/dp/${p.asin}?tag=${TAG}`:`https://www.amazon.com/s?k=${encodeURIComponent(p.q).replace(/%20/g,'+')}&tag=${TAG}`;}
function rows(){
  const r=[];
  parts.forEach(p=>{if(p.colors)return;const o=p.options.find(o=>o.id===S[p.id]);if(o&&o.p)r.push({id:p.id,k:p.label,opt:o.label,p:o.p});});
  extras.forEach(e=>{if(has(e.id))r.push({id:e.id,k:e.label,opt:'',p:e.p});});
  return r;
}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function list(){
  const R=rows();document.getElementById('sbcount').textContent=R.length;
  listEl.innerHTML=R.map(r=>{const t=S.o[r.id]||S.t, i=TIERS.indexOf(t), p=r.p[i]||r.p[r.p.length-1];
    return `<li class="sb-row"><span class="ic" aria-hidden="true">${esc(r.k.slice(0,2))}</span><span><span class="k">${esc(r.k)}${r.opt?' · '+esc(r.opt):''}</span><span class="n">${esc(p.name)}</span></span>
    <span class="sb-tier" role="group" aria-label="${esc(r.k)} price level">${TIERS.map(x=>`<button type="button" data-row="${r.id}" data-t="${x}" aria-pressed="${x===t}">${TL[x]}</button>`).join('')}</span>
    <a class="buy" href="${link(p)}" target="_blank" rel="sponsored noopener" data-row="${r.id}">${p.asin?'See price':'Shop'} on Amazon</a></li>`;}).join('');
  document.querySelectorAll('#sbtier button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.t===S.t)));
}

/* ---------- controls ---------- */
function controls(){
  let h='';
  parts.forEach(p=>{
    h+=`<section class="sb-part"><h2 id="h-${p.id}">${esc(p.label)}</h2><div class="sb-opts${p.colors?' sb-sw':''}" role="group" aria-labelledby="h-${p.id}">`;
    if(p.colors)h+=D.colors.map(c=>`<button type="button" data-p="${p.id}" data-v="${c.id}" aria-label="${esc(c.label)}" title="${esc(c.label)}"><i style="background:${c.hex}"></i></button>`).join('');
    else h+=p.options.map(o=>`<button type="button" data-p="${p.id}" data-v="${o.id}">${esc(o.label)}</button>`).join('');
    h+='</div></section>';
  });
  h+=`<section class="sb-part"><h2 id="h-x">Extras</h2><div class="sb-opts" role="group" aria-labelledby="h-x">`+extras.map(e=>`<button type="button" data-x="${e.id}">${esc(e.label)}</button>`).join('')+'</div></section>';
  ctl.innerHTML=h;
}
function sync(){
  ctl.querySelectorAll('button[data-p]').forEach(b=>b.setAttribute('aria-pressed',String(S[b.dataset.p]===b.dataset.v)));
  ctl.querySelectorAll('button[data-x]').forEach(b=>b.setAttribute('aria-pressed',String(has(b.dataset.x))));
}
function render(){draw();list();sync();save();}
function toast(t){const e=document.getElementById('sbtoast');e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('on'),1800);}
function gc(path){try{if(window.goatcounter&&goatcounter.count)goatcounter.count({path,event:true});}catch(e){}}

ctl.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.p){S[b.dataset.p]=b.dataset.v;if(b.dataset.p==='color'&&S.light==='none')S.light='bars';}
  else if(b.dataset.x){const x=b.dataset.x;S.x=has(x)?S.x.filter(y=>y!==x):S.x.concat(x);}
  render();
});
listEl.addEventListener('click',e=>{
  const b=e.target.closest('button[data-row]');if(b){S.o[b.dataset.row]=b.dataset.t;render();return;}
  const a=e.target.closest('a.buy');if(a)gc('builder-buy-'+a.dataset.row);
});
document.getElementById('sbtier').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;S.t=b.dataset.t;S.o={};render();});
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{S=fill(parse(b.dataset.preset));render();gc('builder-preset');toast(b.textContent.trim()+' loaded');}));
document.querySelectorAll('[data-act=random]').forEach(b=>b.addEventListener('click',()=>{
  const pick=a=>a[Math.floor(Math.random()*a.length)];
  parts.forEach(p=>{S[p.id]=p.colors?pick(D.colors).id:pick(p.options.filter(o=>o.id!=='none'||Math.random()<.25)).id;});
  S.x=extras.filter(()=>Math.random()<.4).map(e=>e.id);S.o={};render();gc('builder-random');}));
document.querySelectorAll('[data-act=share]').forEach(b=>b.addEventListener('click',async()=>{
  const url=location.href.split('#')[0]+'#'+ser(S);gc('builder-share');
  if(navigator.share){try{await navigator.share({title:'My desk setup',text:'Check out the gaming setup I built on SteelGames',url});return;}catch(e){if(e&&e.name==='AbortError')return;}}
  try{await navigator.clipboard.writeText(url);toast('Link copied');}catch(e){prompt('Copy this link',url);}
}));
document.querySelectorAll('[data-act=list]').forEach(b=>b.addEventListener('click',()=>document.getElementById('sblist').scrollIntoView({behavior:'smooth'})));
window.addEventListener('hashchange',()=>{const n=ser(fill(parse(location.hash)));if(n!==ser(S)){S=fill(parse(location.hash));render();}});

controls();
S=fill(parse(location.hash.length>2?location.hash:D.default));
render();
})();
</script>
"""


def build(preview=False):
    data = json.load(open(os.path.join(ROOT, "data", "setup_builder.json")))
    e = html.escape
    title = "Desk Setup Builder: Design Your Gaming Setup and Shop the Gear | SteelGames"
    desc = ("Build your dream gaming desk. Pick the back light, desk, monitor, PC, keyboard, mouse and more, "
            "watch it come together, then shop every piece on Amazon at budget, mid or premium prices.")
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "SteelGames Desk Setup Builder",
          "url": f"{SITE}/setups/", "applicationCategory": "LifestyleApplication", "operatingSystem": "Any",
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    extra = f'<style>{CSS}</style>\n<script type="application/ld+json">{json.dumps(ld)}</script>\n'
    head = layout.head(title, desc, f"{SITE}/setups/", extra=extra)
    if preview:  # review copy that works off-site: site styles inlined, site links made absolute
        css = "".join(open(os.path.join(ROOT, "assets", f)).read() for f in ("pages.css", "mobile.css"))
        head = head.replace('<link rel="stylesheet" href="/assets/pages.css">', '<meta name="robots" content="noindex"><style>' + css + '</style>')
        head = head.replace('<link rel="stylesheet" href="/assets/mobile.css">', '')
    presets = "".join(f'<button type="button" data-preset="{e(p["s"])}">{e(p["name"])}</button>' for p in data["presets"])
    n_ideas = len(json.load(open(os.path.join(ROOT, "data", "setup_ideas.json")))["setups"])
    presets += f'<a href="/setups/ideas/#ds-h">See {n_ideas} more setups</a>'
    acts = ('<button type="button" class="go" data-act="share">Share my setup</button>'
            '<button type="button" data-act="random">Surprise me</button>'
            '<button type="button" data-act="list">Shop this setup</button>')
    body = f"""<main id="main">
<section class="block"><div class="wrap">
<div class="sb-top"><div><h1>Desk Setup Builder</h1>
<p class="lede">Pick each piece and watch your setup come together. Every pick links to real gear on Amazon, at the price level you choose.</p></div>
<div class="sb-pre" aria-label="Start from a setup">{presets}</div></div>
<div class="sb">
<div class="sb-stage"><div class="sb-view"><svg id="sbsvg" viewBox="0 0 1200 720" role="img" aria-label="Drawing of your desk setup"></svg></div>
<p class="sb-note">A simple drawing to help you picture it, not the exact products. Prices are on Amazon.</p>
<div class="sb-act">{acts}</div></div>
<div><div class="sb-ctl" id="sbctl"></div><div class="sb-act m">{acts}</div></div>
</div>
<div class="sb-list" id="sblist">
<div class="sb-list-h"><h2>Your setup (<span id="sbcount">0</span> items)</h2>
<span class="sb-tier" id="sbtier" role="group" aria-label="Price level for every item"><button type="button" data-t="budget">Budget</button><button type="button" data-t="mid">Mid</button><button type="button" data-t="premium">Premium</button></span></div>
<ul class="sb-rows" id="sbrows"></ul>
<p class="sb-foot">Prices are on Amazon and change daily, so tap through to see today's price. As an Amazon Associate, SteelGames earns from qualifying purchases at no extra cost to you. Want ideas first? See <a href="/setups/ideas/">finished setups you can shop</a> or our <a href="/gear.html">gear guides</a>.</p>
</div>
</div></section>
</main>
<div class="sb-toast" id="sbtoast" role="status" aria-live="polite"></div>
<script>window.SB_DATA={json.dumps(data, separators=(",", ":"))};</script>
"""
    page = head + layout.header("setups") + body + JS + layout.footer()
    if preview:
        page = page.replace('href="/', f'href="{SITE}/').replace('src="/assets', f'src="{SITE}/assets').replace(f'href="{SITE}/#main"', 'href="#main"')
    return page


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "setups"), exist_ok=True)
    open(os.path.join(ROOT, "setups", "index.html"), "w").write(build())
    print("built /setups/ (builder)")
    if "--preview" in sys.argv:
        os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
        open(os.path.join(ROOT, "preview", "setup-builder.html"), "w").write(build(preview=True))
        print("built preview/setup-builder.html")
