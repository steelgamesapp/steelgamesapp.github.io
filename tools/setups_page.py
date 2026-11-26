"""Shop the Setup gallery (/setups/ideas/): an Instagram-style grid of desk setups,
gear spotlights and wallpapers. Every post lives in data/setups_gallery.json.

Add a post: put the picture in assets/setups/<slug>.jpg (any shape), add an entry
to data/setups_gallery.json with its real width/height, then run
    python3 tools/setups_page.py
Setup and gear posts take "items" with x/y (the dot's position, in percent of the
picture from the left and top). Wallpapers take "downloads".
"""
import html
import json
import re
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://steelgamesapp.com"
TAG = "steelgames-20"
e = html.escape
KIND = {"setup": "Setup", "gear": "Gear", "wallpaper": "Wallpaper", "shot": "Screenshot"}

BAG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h12l1 13H5z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>'
DL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>'


def link(it):
    if it.get("asin"):
        return f"https://www.amazon.com/dp/{it['asin']}?tag={TAG}"
    return f"https://www.amazon.com/s?k={urllib.parse.quote_plus(it['q'])}&tag={TAG}"


def thumbs(posts):
    """Square-ish 4:5 grid thumbnails, made once per picture."""
    try:
        from PIL import Image
    except Exception:
        return
    tdir = os.path.join(ROOT, "assets", "setups", "thumb")
    os.makedirs(tdir, exist_ok=True)
    for p in posts:
        src = os.path.join(ROOT, p["img"].lstrip("/"))
        out = os.path.join(tdir, p["slug"] + ".jpg")
        if not os.path.exists(src) or (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src)):
            continue
        im = Image.open(src).convert("RGB")
        w, h = im.size
        tw, th = 4, 5
        if w / h > tw / th:
            nw = int(h * tw / th); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w * th / tw); top = int((h - nh) * 0.4); im = im.crop((0, top, w, top + nh))
        im.resize((640, 800), Image.LANCZOS).save(out, quality=78, optimize=True, progressive=True)


def side(x, y):
    c = []
    if y < 32:
        c.append("below")
    if x > 70:
        c.append("left")
    elif x < 30:
        c.append("right")
    return " ".join(c)


def post_html(p, by_slug):
    kind = p.get("type", "setup")
    items = p.get("items", [])
    spots, rows, k = [], [], 0
    for it in items:
        u = e(link(it))
        if "x" in it:
            k += 1
            n = str(k)
            spots.append(f'<div class="hs {side(it["x"], it["y"])}" style="left:{it["x"]}%;top:{it["y"]}%" data-i="{n}">'
                         f'<button class="dot" type="button" aria-label="{e(it["what"])}: {e(it["name"])}">{n}</button>'
                         f'<span class="tip"><small>{e(it["what"])}</small><b>{e(it["name"])}</b>'
                         f'<a href="{u}" target="_blank" rel="sponsored nofollow noopener">See price on Amazon</a></span></div>')
            num = f'<span class="n">{n}</span>'
        else:
            n, num = "", '<span class="n off">+</span>'
        rows.append(f'<li data-i="{n}">{num}<span class="t"><small>{e(it["what"])}</small><span>{e(it["name"])}</span></span>'
                    f'<a class="go" href="{u}" target="_blank" rel="sponsored nofollow noopener">{"See price" if it.get("asin") else "Shop similar"}</a></li>')
    extra = ""
    if items:
        extra += f'<ul class="gear">{"".join(rows)}</ul>'
    for d in p.get("downloads", []):
        extra += f'<a class="dl" href="{e(d["href"])}" download>{DL}Download {e(d["label"])}</a>'
    if p.get("tip"):
        extra += f'<p class="ptip">{e(p["tip"])}</p>'
    if p.get("pair") in by_slug:
        q = by_slug[p["pair"]]
        extra += f'<a class="pair" href="#{e(q["slug"])}" data-open="{e(q["slug"])}">Shop the matching desk: {e(q["title"])}</a>'
    icon = BAG if items else (DL if p.get("downloads") else "")
    ai = '<span class="aitag">AI-made picture</span>' if p.get("ai") else ""
    alt = ("AI-made picture: " if p.get("ai") else "") + p["title"]
    count = f'<span class="cnt">{BAG}{k}</span>' if items else ""
    return (f'<article class="post" id="{e(p["slug"])}" data-kind="{e(kind)}">'
            f'<a class="tile" href="#{e(p["slug"])}" data-open="{e(p["slug"])}" aria-label="Open {e(p["title"])}">'
            f'<img src="/assets/setups/thumb/{e(p["slug"])}.jpg" width="640" height="800" loading="lazy" alt="{e(alt)}">'
            f'<span class="ov"><span class="ovk">{e(KIND.get(kind, kind))}</span><span class="ovt">{e(p["title"])}</span>{count}</span>'
            f'<span class="badge-i">{icon}</span></a>'
            f'<div class="full" hidden><div class="stage"><div class="pic">'
            f'<img data-src="{e(p["img"])}" width="{p["w"]}" height="{p["h"]}" alt="{e(alt)}">{ai}{"".join(spots)}</div></div>'
            f'<div class="side"><p class="kind">{e(KIND.get(kind, kind))}</p><h2>{e(p["title"])}</h2>'
            f'<p class="cap">{e(p.get("caption", ""))}</p>{extra}</div></div></article>')


CSS = """
.ig-top{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.ig-ava{flex:none;width:86px;height:86px;border-radius:50%;padding:3px;background:conic-gradient(#FF4FA3,#FFB347,#6A4DF0,#2FD3FF,#FF4FA3)}
.ig-ava span{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:#0F0A24;border:3px solid #0F0A24}
.ig-meta h1{font-size:clamp(26px,4vw,40px);margin:0}
.ig-stats{display:flex;gap:18px;color:var(--steel);font-size:15px;margin:6px 0 0}
.ig-stats b{color:#fff}
.ig-tabs{display:flex;gap:6px;margin:22px 0 14px;border-top:1px solid var(--line);padding-top:12px;overflow-x:auto}
.ig-tabs button{flex:none;background:none;border:0;color:var(--muted);font:700 13px var(--body);letter-spacing:1px;text-transform:uppercase;padding:9px 14px;border-radius:999px;cursor:pointer}
.ig-tabs button[aria-pressed=true]{color:#fff;background:var(--raised)}
.ig-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
@media(min-width:760px){.ig-grid{gap:14px}}
.post{min-width:0}
.post[hidden]{display:none}
.tile{position:relative;display:block;aspect-ratio:4/5;overflow:hidden;border-radius:6px;background:#1A1342}
@media(min-width:760px){.tile{border-radius:14px}}
.tile img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease,filter .3s}
.tile:hover img,.tile:focus-visible img{transform:scale(1.05);filter:saturate(1.15)}
.ov{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;gap:4px;padding:14px;background:linear-gradient(transparent 45%,rgba(8,5,22,.88));opacity:0;transition:opacity .25s}
.tile:hover .ov,.tile:focus-visible .ov{opacity:1}
@media(hover:none){.ov{opacity:1;background:linear-gradient(transparent 60%,rgba(8,5,22,.8));padding:8px}.ovk,.cnt{display:none}.ovt{font-size:12px}}
.ovk{color:var(--accent-soft);font:700 11px var(--body);letter-spacing:1px;text-transform:uppercase}
.ovt{color:#fff;font:700 16px var(--display,var(--body));line-height:1.2}
.cnt{display:inline-flex;gap:5px;align-items:center;color:#fff;font-size:13px;font-weight:600}
.badge-i{position:absolute;top:8px;right:8px;color:#fff;filter:drop-shadow(0 1px 3px rgba(0,0,0,.7))}
.badge-i:empty{display:none}
.how{background:var(--surface);border:1px solid var(--line-strong);border-radius:14px;padding:14px 16px;color:var(--steel);font-size:14px;margin-top:22px}
/* viewer */
.vw{position:fixed;inset:0;z-index:100;display:none;background:rgba(6,4,16,.92)}
.vw.on{display:flex;align-items:center;justify-content:center}
.vw .amb{position:absolute;inset:-10%;background-size:cover;background-position:center;filter:blur(70px) saturate(1.8);opacity:.55;transform:scale(1.1)}
.vw .box{position:relative;display:grid;grid-template-columns:minmax(0,auto) 360px;max-width:min(1400px,96vw);max-height:94vh;background:rgba(15,10,36,.72);border:1px solid rgba(255,255,255,.12);border-radius:18px;overflow:hidden;box-shadow:0 30px 90px rgba(0,0,0,.6)}
.vw .stage{display:flex;align-items:center;justify-content:center;background:#000;min-width:0}
.vw .pic{position:relative;display:inline-block;line-height:0}
.vw .pic img{display:block;max-width:min(1040px,calc(96vw - 360px));max-height:94vh;width:auto;height:auto}
.vw .side{overflow-y:auto;max-height:94vh;padding:22px 20px;display:flex;flex-direction:column;gap:12px}
.vw .kind{color:var(--accent-soft);font:700 12px var(--body);letter-spacing:1px;text-transform:uppercase;margin:0}
.vw h2{margin:0;font-size:24px}
.vw .cap{color:var(--steel);margin:0}
.vw .x,.vw .nav-b{position:absolute;z-index:3;display:grid;place-items:center;width:44px;height:44px;border-radius:50%;border:0;background:rgba(15,10,36,.8);color:#fff;font-size:22px;cursor:pointer}
.vw .x{top:14px;right:14px}
.vw .prev{left:14px;top:50%;transform:translateY(-50%)}
.vw .next{right:14px;top:50%;transform:translateY(-50%)}
@media(max-width:860px){
 .vw.on{align-items:stretch}
 .vw .box{grid-template-columns:1fr;grid-template-rows:auto 1fr;max-width:100vw;max-height:100vh;width:100vw;border-radius:0;border:0;overflow-y:auto}
 .vw .pic img{max-width:100vw;max-height:72vh}
 .vw .side{max-height:none;overflow:visible;padding:18px 16px 40px}
 .vw .prev,.vw .next{top:36vh}
}
.aitag{position:absolute;left:10px;top:10px;background:rgba(10,6,28,.78);color:#fff;font:600 12px/1.2 var(--body);padding:5px 9px;border-radius:8px}
.hs{position:absolute;transform:translate(-50%,-50%);z-index:2;line-height:1.3}
.hs:hover,.hs:focus-within,.hs.open{z-index:5}
.dot{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;border:2px solid #fff;background:rgba(106,77,240,.92);color:#fff;font:700 13px var(--body);cursor:pointer;animation:pulse 2.2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(255,255,255,.25)}50%{box-shadow:0 0 0 10px rgba(255,255,255,.05)}}
@media(prefers-reduced-motion:reduce){.dot{animation:none}.tile img{transition:none}}
.tip{display:none;position:absolute;left:50%;bottom:38px;transform:translateX(-50%);width:220px;background:#120C2E;border:1px solid var(--line-strong);border-radius:12px;padding:11px 12px;box-shadow:0 10px 30px rgba(0,0,0,.5);text-align:left}
.hs.below .tip{bottom:auto;top:38px}
.hs.left .tip{left:auto;right:-8px;transform:none}
.hs.right .tip{left:-8px;transform:none}
.hs:hover .tip,.hs:focus-within .tip,.hs.open .tip{display:block}
.tip small{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.6px}
.tip b{display:block;color:#fff;font-size:14px;margin:3px 0 8px}
.tip a{display:inline-flex;min-height:34px;align-items:center;padding:0 11px;border-radius:9px;background:var(--grad-cta);color:var(--accent-ink);font-weight:700;font-size:13px;text-decoration:none}
.gear{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:7px}
.gear li{display:flex;gap:10px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px 10px}
.gear .n{flex:none;display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:rgba(106,77,240,.92);color:#fff;font:700 12px var(--body)}
.gear .n.off{background:var(--raised)}
.gear .t{flex:1;min-width:0}
.gear .t small{display:block;color:var(--muted);font-size:11px}
.gear .t span{display:block;color:#fff;font-size:14px;font-weight:600;line-height:1.3}
.gear a.go{flex:none;font-size:12px;font-weight:700;text-decoration:none;padding:7px 9px;border-radius:9px;border:1px solid var(--line-strong);color:#fff;background:var(--raised)}
.dl{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:0 16px;border-radius:12px;background:var(--grad-cta);color:var(--accent-ink);font-weight:700;text-decoration:none}
.ptip{color:var(--steel);font-size:14px;margin:0}
.pair{color:var(--accent-soft);font-weight:600;font-size:14px}
.earns{font-size:12px;color:var(--muted);margin:0}
body.vw-open{overflow:hidden}
.ds-head{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin:40px 0 6px}
.ds-head h2{margin:0;font-size:clamp(22px,3vw,30px)}
.ds-head p{margin:6px 0 0;color:var(--steel);max-width:640px}
.ds-build{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:12px;background:var(--grad-cta);color:var(--accent-ink);font-weight:700;text-decoration:none}
.ds-chips{display:flex;gap:7px;overflow-x:auto;padding:12px 0 14px;scrollbar-width:none}
.ds-chips button{flex:none;font:600 13px/1 var(--body);color:var(--steel);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:9px 13px;cursor:pointer}
.ds-chips button[aria-pressed=true]{color:#fff;background:var(--chip);border-color:#9C86FF}
.ds-chips button span{opacity:.65;font-weight:500;margin-left:3px}
.ds-sec{margin:6px 0 26px}.ds-sec[hidden]{display:none}
.ds-sh{font-size:20px;margin:6px 0 12px;scroll-margin-top:80px}
.ds-n{margin:4px 0 6px;font-size:13px;color:var(--steel)}
.ds-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(290px,100%),1fr));gap:16px}
.ds{display:flex;flex-direction:column;min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;scroll-margin-top:80px}
.ds[hidden]{display:none}
.ds-pic{display:block;aspect-ratio:5/3;background:#140f2a}
.ds{position:relative}.ds-cr{position:absolute;top:8px;right:8px;font-size:11px;line-height:1.4;background:rgba(0,0,0,.6);color:#fff;padding:2px 7px;border-radius:6px;text-decoration:none}
.ds-pic img{display:block;width:100%;height:100%;object-fit:cover}
.ds-b{display:flex;flex-direction:column;gap:8px;padding:12px 14px 14px;flex:1}
.ds-k{margin:0;color:var(--accent-soft);font:700 11px var(--body);letter-spacing:1px;text-transform:uppercase}
.ds h3{margin:0;font-size:19px}
.ds-d{margin:0;color:var(--steel);font-size:14px}
.ds details{border-top:1px solid var(--line);padding-top:8px;margin-top:auto}
.ds summary{cursor:pointer;color:#fff;font-weight:600;font-size:14px;min-height:36px;display:flex;align-items:center}
.ds-l{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:6px}
.ds-l li{display:flex;align-items:center;gap:10px;justify-content:space-between}
.ds-l .t{min-width:0}
.ds-l small{display:block;color:var(--muted);font-size:11px}
.ds-l span{display:block;color:#fff;font-size:13px;line-height:1.3}
.ds-l a{flex:none;font-size:12px;font-weight:700;text-decoration:none;padding:7px 9px;border-radius:9px;border:1px solid var(--line-strong);color:#fff;background:var(--raised)}
.ds-open{display:inline-flex;align-self:flex-start;align-items:center;min-height:40px;padding:0 13px;border-radius:10px;border:1px solid var(--line-strong);color:#fff;font-weight:700;font-size:14px;text-decoration:none;background:var(--raised)}
.ds-open:hover,.ds-l a:hover{background:var(--line)}

"""

JS = """<script>
(function(){
var posts=[].slice.call(document.querySelectorAll('.post'));
var vw=document.getElementById('vw'),box=vw.querySelector('.box'),amb=vw.querySelector('.amb'),cur=-1;
function vis(){return posts.filter(function(p){return !p.hidden})}
function open(slug,push){
  var p=document.getElementById(slug);if(!p||!p.classList.contains('post'))return;
  var full=p.querySelector('.full').cloneNode(true);full.hidden=false;
  var im=full.querySelector('img[data-src]');im.src=im.getAttribute('data-src');
  box.querySelectorAll('.stage,.side').forEach(function(n){n.remove()});
  [].slice.call(full.children).forEach(function(c){box.appendChild(c)});
  var side=box.querySelector('.side');var t=document.createElement('p');t.className='earns';
  if(side.querySelector('.gear'))t.textContent='Links go to Amazon, where you see today\\u2019s price. We earn a commission if you buy.';
  if(t.textContent)side.appendChild(t);
  amb.style.backgroundImage='url('+im.src+')';
  wire(box);cur=vis().indexOf(p);vw.classList.add('on');document.body.classList.add('vw-open');
  if(push!==false)history.replaceState(null,'','#'+slug);
  vw.querySelector('.x').focus({preventScroll:true});
  if(window.goatcounter&&goatcounter.count)goatcounter.count({path:'/setups/ideas/#'+slug,event:true});
}
function close(){vw.classList.remove('on');document.body.classList.remove('vw-open');history.replaceState(null,'',location.pathname);}
function step(d){var v=vis();if(!v.length)return;cur=(cur+d+v.length)%v.length;open(v[cur].id)}
function wire(root){
  root.querySelectorAll('.dot').forEach(function(b){b.addEventListener('click',function(ev){var h=b.parentNode,o=h.classList.contains('open');
    root.querySelectorAll('.hs.open').forEach(function(x){x.classList.remove('open')});if(!o)h.classList.add('open');ev.stopPropagation();})});
  root.querySelectorAll('.gear li[data-i]').forEach(function(li){var i=li.getAttribute('data-i');if(!i)return;
    li.addEventListener('mouseenter',function(){var h=root.querySelector('.hs[data-i="'+i+'"]');if(h)h.classList.add('open')});
    li.addEventListener('mouseleave',function(){var h=root.querySelector('.hs[data-i="'+i+'"]');if(h)h.classList.remove('open')});});
  root.querySelectorAll('[data-open]').forEach(function(a){a.addEventListener('click',function(ev){ev.preventDefault();open(a.getAttribute('data-open'))})});
}
document.querySelectorAll('.tile').forEach(function(a){a.addEventListener('click',function(ev){ev.preventDefault();open(a.getAttribute('data-open'))})});
vw.querySelector('.x').addEventListener('click',close);
vw.querySelector('.prev').addEventListener('click',function(){step(-1)});
vw.querySelector('.next').addEventListener('click',function(){step(1)});
vw.addEventListener('click',function(ev){if(ev.target===vw||ev.target===amb)close();if(!ev.target.closest('.hs'))box.querySelectorAll('.hs.open').forEach(function(x){x.classList.remove('open')})});
document.addEventListener('keydown',function(ev){if(!vw.classList.contains('on'))return;if(ev.key==='Escape')close();if(ev.key==='ArrowRight')step(1);if(ev.key==='ArrowLeft')step(-1)});
var sx=null;box.addEventListener('touchstart',function(ev){if(!ev.target.closest('.side'))sx=ev.touches[0].clientX},{passive:true});
box.addEventListener('touchend',function(ev){if(sx===null)return;var dx=ev.changedTouches[0].clientX-sx;sx=null;if(Math.abs(dx)>60)step(dx<0?1:-1)});
document.querySelectorAll('.ig-tabs button').forEach(function(b){b.addEventListener('click',function(){
  document.querySelectorAll('.ig-tabs button').forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');
  var k=b.getAttribute('data-k');posts.forEach(function(p){p.hidden=!(k==='all'||p.getAttribute('data-kind')===k)});});});
if(location.hash.length>1)open(decodeURIComponent(location.hash.slice(1)),false);
})();
</script>
"""


TIERS = ["budget", "mid", "premium"]
TL = {"budget": "Budget", "mid": "Mid-range", "premium": "Premium"}


def idea_items(B, state, it=None):
    """The shopping list for a builder state, in the same order the builder shows it.
    it may carry swap (replace a row by its label, for brand setups) and add (extra rows)."""
    q = dict(urllib.parse.parse_qsl(state))
    t = TIERS.index(q.get("t", "mid"))
    x = q.get("x", "").split(".")
    out = []
    for part in B["parts"]:
        if part.get("colors"):
            continue
        o = next((o for o in part["options"] if o["id"] == q.get(part["key"])), None)
        if o and o.get("p"):
            out.append((part["label"], o["p"][min(t, len(o["p"]) - 1)]))
    for ex in B["extras"]:
        if ex["id"] in x:
            out.append((ex["label"], ex["p"][min(t, len(ex["p"]) - 1)]))
    if it:
        sw = it.get("swap", {})
        labels = {k for k, _ in out}
        missing = set(sw) - labels
        if missing:
            raise SystemExit(f"{it['slug']}: swap labels not in its list: {missing}")
        out = [(k, sw.get(k, p)) for k, p in out]
        out += [(a["label"], a) for a in it.get("add", [])]
    for k, p in out:
        if not (p.get("asin") or p.get("q")):
            raise SystemExit(f"no asin or q for {k}")
    return out


PREVIEW = os.environ.get("PHOTO_PREVIEW") == "1"
PX = "https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&cs=tinysrgb&w=900&h=540&fit=crop"

GROUPS = ["Styles and colors", "Games", "Who it's for", "Spaces", "Console and handheld", "Brands", "Budgets"]


def ideas_html():
    """The drawn setups from data/setup_ideas.json (pictures: node tools/render_setups.js), in sections by group."""
    B = json.load(open(os.path.join(ROOT, "data", "setup_builder.json")))
    ideas = json.load(open(os.path.join(ROOT, "data", "setup_ideas.json")))["setups"]
    ideas = [i for i in ideas if i.get("photo")]  # only setups with a real photo are shown
    groups = [g for g in GROUPS if any(i["group"] == g for i in ideas)]
    bad = [i["slug"] for i in ideas if i["group"] not in GROUPS]
    if bad:
        raise SystemExit(f"unknown group on {bad}")
    gid = lambda g: "g-" + re.sub(r"[^a-z]+", "-", g.lower()).strip("-")
    chips = f'<button type="button" data-g="all" aria-pressed="true">All {len(ideas)}</button>' + "".join(
        f'<button type="button" data-g="{gid(g)}" aria-pressed="false">{e(g)} <span>{sum(i["group"] == g for i in ideas)}</span></button>'
        for g in groups)
    secs, n = [], 0
    for g in groups:
        cards = []
        for it in [i for i in ideas if i["group"] == g]:
            items = idea_items(B, it["s"], it)
            n += len(items)
            t = dict(urllib.parse.parse_qsl(it["s"])).get("t", "mid")
            lis = "".join(
                f'<li><span class="t"><small>{e(k)}</small><span>{e(p["name"])}</span></span>'
                f'<a href="{e(link(p))}" target="_blank" rel="sponsored nofollow noopener">{"See price" if p.get("asin") else "Shop"}</a></li>'
                for k, p in items)
            bl = e("/setups/#" + it["s"])
            nm, sl = e(it["name"]), e(it["slug"])
            note = ('<p class="ds-n">The builder shows our usual picks. The list below is the brand version.</p>'
                    if it.get("swap") else "")
            cards.append(
                f'<article class="ds" id="{sl}">' +
                (f'<a class="ds-pic" href="{bl}" aria-label="Open {nm} in the setup builder"><img src="{PX.format(int(it["photo"]))}" width="900" height="540" loading="{'eager' if PREVIEW else 'lazy'}" alt="Photo of a desk setup in the {nm} style"></a>'
                 f'<a class="ds-cr" href="https://www.pexels.com/photo/{int(it["photo"])}/" target="_blank" rel="noopener">Photo: Pexels</a>'
                 ) +
                f'<div class="ds-b"><p class="ds-k">{e(it["look"])} &middot; {TL[t]} picks</p><h3>{nm}</h3><p class="ds-d">{e(it["blurb"])}</p>'
                f'<details><summary>Shop all {len(items)} pieces</summary>{note}<ul class="ds-l">{lis}</ul></details>'
                f'<a class="ds-open" href="{bl}">Open in builder</a></div></article>\n')
        secs.append(f'<section class="ds-sec" id="{gid(g)}" aria-labelledby="{gid(g)}-h"><h3 class="ds-sh" id="{gid(g)}-h">{e(g)}</h3>'
                    f'<div class="ds-grid">\n{"".join(cards)}</div></section>\n')
    sec = (f'<div class="ds-head"><div><h2 id="ds-h">{len(ideas)} more setups to shop</h2>'
           '<p>Every look below is made in our Desk Setup Builder. Pick a group, open a setup to swap any piece or change the price level, or shop the whole list right here.</p></div>'
           '<a class="ds-build" href="/setups/">Build your own</a></div>'
           f'<div class="ds-chips" role="toolbar" aria-label="Show setups by group">{chips}</div>'
           + "".join(secs))
    return sec, len(ideas), n


DS_JS = """<script>
(function(){var cs=document.querySelectorAll('.ds-chips button'),secs=document.querySelectorAll('.ds-sec');
function show(k){cs.forEach(function(x){x.setAttribute('aria-pressed',String(x.getAttribute('data-g')===k))});
secs.forEach(function(c){c.hidden=!(k==='all'||c.id===k)});}
cs.forEach(function(b){b.addEventListener('click',function(){show(b.getAttribute('data-g'))})});
var h=location.hash.slice(1);if(h.indexOf('g-')===0&&document.getElementById(h))show(h);
document.querySelectorAll('.ds a').forEach(function(a){a.addEventListener('click',function(){try{if(window.goatcounter&&goatcounter.count)goatcounter.count({path:'/setups/ideas/'+(a.closest('li')?'buy':'open-builder')+'-'+a.closest('.ds').id,event:true})}catch(err){}})});
})();
</script>
"""


def build():
    data = json.load(open(os.path.join(ROOT, "data", "setups_gallery.json")))
    posts = data["posts"]
    thumbs(posts)
    by_slug = {p["slug"]: p for p in posts}
    kinds = [k for k in ["setup", "gear", "wallpaper", "shot"] if any(p.get("type") == k for p in posts)]
    n_items = sum(len(p.get("items", [])) for p in posts)
    title = "Shop the Setup: Gaming Desk Setups with Gear Links | SteelGames"
    desc = "Real gaming desk setups you can shop: all-white, RGB neon, cozy wood, pink, console TV, handheld, sim racing, retro and more, with every piece linked on Amazon."
    ld = {"@context": "https://schema.org", "@type": "ImageGallery", "name": "SteelGames Setups", "url": f"{SITE}/setups/ideas/",
          "image": [{"@type": "ImageObject", "contentUrl": SITE + p["img"], "name": p["title"]} for p in posts]}
    og = f'<meta property="og:image" content="{SITE}{posts[0]["img"]}">'
    head = layout.head(title, desc, f"{SITE}/setups/ideas/",
                       extra=f'<style>{CSS}</style>\n<script type="application/ld+json">{json.dumps(ld)}</script>\n')
    head = head.replace(f'<meta property="og:image" content="{SITE}/assets/og-steelgames.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">', og)
    head = head.replace(f'<meta name="twitter:image" content="{SITE}/assets/og-steelgames.png">', f'<meta name="twitter:image" content="{SITE}{posts[0]["img"]}">')
    tabs = ('<div class="ig-tabs" role="toolbar" aria-label="Filter posts"><button type="button" data-k="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-k="{k}" aria-pressed="false">{KIND[k]}s</button>' for k in kinds) + '</div>') if len(kinds) > 1 else '<div class="ig-tabs"></div>'
    n_dl = sum(len(p.get("downloads", [])) for p in posts)
    ds_sec, n_ideas, n_idea_items = ideas_html()
    body = f"""<main id="main">
<section class="block"><div class="wrap">
<div class="ig-top"><div class="ig-ava"><span>{layout.LOGO}</span></div>
<div class="ig-meta"><h1>Shop the Setup</h1>
<p class="ig-stats"><span><b>{len(posts) + n_ideas}</b> setups</span><span><b>{n_items + n_idea_items}</b> shoppable items</span>{f'<span><b>{n_dl}</b> free wallpapers</span>' if n_dl else ''}</p>
<p class="lede" style="margin:8px 0 0">Dream gaming desks you can actually build. Tap a setup, then tap the dots to find each piece.</p></div></div>
{tabs}
<div class="ig-grid">
{"".join(post_html(p, by_slug) for p in posts)}
</div>
{ds_sec}
<div class="how"><b>About these pictures.</b> Pictures marked AI-made, and the drawings, are ideas, not photos of real desks. Each dot links to real gear that looks and works like what you see, mostly picks from our <a href="/gear.html">gear guides</a>. Links go to Amazon, where you can see today's price. As an Amazon Associate, SteelGames earns from qualifying purchases at no extra cost to you.</div>
</div></section>
</main>
<div class="vw" id="vw" role="dialog" aria-modal="true" aria-label="Post viewer"><div class="amb"></div>
<button class="nav-b prev" type="button" aria-label="Previous post">&#8249;</button><button class="nav-b next" type="button" aria-label="Next post">&#8250;</button>
<div class="box"><button class="x" type="button" aria-label="Close">&#215;</button></div></div>
"""
    return head + layout.header("setups") + body + JS + DS_JS + layout.footer()


if __name__ == "__main__":
    out = "ideas-preview" if PREVIEW else "ideas"
    html = build()
    html = html.replace("Pictures marked AI-made, and the drawings, are ideas, not photos of real desks.", "Pictures marked AI-made are ideas. The setup photos are free stock photos from Pexels that show the look, not the exact gear listed.", 1)
    if PREVIEW:
        html = html.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
    if "ram-ticker.js" not in html:  # keep the site-wide RAM ticker another job adds
        html = html.replace('<link rel="stylesheet" href="/assets/mobile.css">', '<link rel="stylesheet" href="/assets/mobile.css"><script src="/assets/ram-ticker.js" defer></script>\n', 1)
    os.makedirs(os.path.join(ROOT, "setups", out), exist_ok=True)
    open(os.path.join(ROOT, "setups", out, "index.html"), "w").write(html)
    print("built /setups/" + out + "/")
