// Saves a drawing of every finished setup in data/setup_ideas.json to assets/setups/draw/<slug>.svg,
// using the same drawing code as the Desk Setup Builder (assets/setup-draw.js).
// Run: node tools/render_setups.js   (then python3 tools/setups_page.py)
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/setup_builder.json'), 'utf8'));
const ideas = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/setup_ideas.json'), 'utf8')).setups;
const draw = require(path.join(ROOT, 'assets/setup-draw.js')).make(D);

function parse(str) {
  const q = new URLSearchParams(str), s = { x: [], o: {}, t: 'mid' }, d = new URLSearchParams(D.default);
  for (const p of D.parts) {
    const ok = v => p.colors ? D.colors.some(c => c.id === v) : p.options.some(o => o.id === v);
    const v = q.get(p.key);
    if (!ok(v)) throw new Error(`bad ${p.key}=${v} in ${str}`);
    s[p.id] = v || d.get(p.key);
  }
  for (const x of (q.get('x') || '').split('.').filter(Boolean)) {
    if (!D.extras.some(e => e.id === x)) throw new Error(`bad extra ${x}`);
    s.x.push(x);
  }
  s.t = q.get('t') || 'mid';
  return s;
}

const out = path.join(ROOT, 'assets/setups/draw');
fs.mkdirSync(out, { recursive: true });
for (const it of ideas) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 720" width="1200" height="720">${draw(parse(it.s))}</svg>`;
  fs.writeFileSync(path.join(out, it.slug + '.svg'), svg.replace(/\n\s*/g, ' '));
}
console.log(`drew ${ideas.length} setups into assets/setups/draw/`);
