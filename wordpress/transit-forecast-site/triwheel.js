// Tri-wheel / bi-wheel SVG. Works in the browser (window.TriWheel) and in Node (module.exports).
// inner = the chart whose houses frame the wheel; middle = second person (optional); outer = transits (optional).
(function (root) {
  const GL = (typeof module !== 'undefined' && typeof require !== 'undefined') ? require('./glyphs.js') : root.SR11Glyphs;
  const SIGN_GLYPH = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
  const PG = { Sun: '☉', Moon: '☽', Mercury: '☿', Venus: '♀', Mars: '♂', Jupiter: '♃', Saturn: '♄', Uranus: '♅', Neptune: '♆', Pluto: '♇', Chiron: '⚷', 'North Node': 'NN', 'South Node': 'SN', Ascendant: 'AC', Midheaven: 'MC' };
  const ORDER = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North Node', 'South Node'];
  const ELEM = ['#b5523f', '#5d7a3a', '#c08a2e', '#3f6aa8']; // fire, earth, air, water
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  function spread(list, minGap) { // cluster-based: no two display angles closer than minGap, each group centred on its true positions
    if (list.length < 2) return list.map(p => ({ ...p, d: p.lon }));
    const srt = list.map(p => ({ ...p })).sort((x, y) => x.lon - y.lon);
    let cut = 0, big = -1; // start the line at the widest empty arc so nothing wraps
    srt.forEach((p, i) => { const q = srt[(i + 1) % srt.length], g = (q.lon - p.lon + 360) % 360 || 360; if (g > big) { big = g; cut = (i + 1) % srt.length; } });
    const lin = srt.slice(cut).concat(srt.slice(0, cut)); const base = lin[0].lon;
    lin.forEach(p => p.u = (p.lon - base + 360) % 360);
    let groups = lin.map(p => ({ items: [p] }));
    const place = g => { const n = g.items.length, mean = g.items.reduce((a, p) => a + p.u, 0) / n; g.items.forEach((p, k) => p.v = mean + (k - (n - 1) / 2) * minGap); };
    groups.forEach(place);
    for (let guard = 0; guard < 200; guard++) {
      let merged = false;
      for (let i = 0; i < groups.length - 1; i++) {
        const A = groups[i], B = groups[i + 1];
        if (B.items[0].v - A.items[A.items.length - 1].v < minGap) { const g = { items: A.items.concat(B.items) }; place(g); groups.splice(i, 2, g); merged = true; break; }
      }
      if (!merged) break;
    }
    return lin.map(p => ({ ...p, d: (p.v + base + 360) % 360 }));
  }
  function svg(opt) {
    const S = opt.size || 640, c = S / 2, asc = opt.inner.planets.Ascendant != null ? opt.inner.planets.Ascendant : opt.inner.cusps[0];
    const col = { ink: '#2a2140', soft: '#3f3358', line: '#8f7bb8', faint: '#a996cc', accent: '#5b3f8c', gold: '#a8822f', a: '#5b3f8c', b: '#b0476b', t: '#2f7a78' };
    const ang = lon => Math.PI + (lon - asc) * Math.PI / 180; // Ascendant on the left, counter-clockwise
    const P = (r, lon) => [c + r * Math.cos(ang(lon)), c - r * Math.sin(ang(lon))];
    const n = 1 + (opt.middle ? 1 : 0) + (opt.outer ? 1 : 0), core = n === 3 ? 0.175 : n === 2 ? 0.2 : 0.24, bw = (0.42 - core) / n;
    const rings = { z1: 0.48, z0: 0.42, core };
    const R = k => rings[k] * S;
    const band = k => { const i = k === 'i' ? 0 : k === 'm' ? 1 : (opt.middle ? 2 : 1); return [S * (core + i * bw), S * (core + (i + 1) * bw)]; };
    let o = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-24 -24 ${S + 48} ${S + 48}" width="${S}" height="${S}" font-family="Helvetica, Arial, sans-serif">`;
    o += `<rect x="-24" y="-24" width="${S + 48}" height="${S + 48}" fill="#fff"/>`;
    // zodiac band
    o += `<circle cx="${c}" cy="${c}" r="${R('z1')}" fill="#f7f3fc" stroke="${col.accent}" stroke-width="1.6"/>`;
    o += `<circle cx="${c}" cy="${c}" r="${R('z0')}" fill="#fff" stroke="${col.accent}" stroke-width="1.4"/>`;
    for (let s = 0; s < 12; s++) {
      const [x1, y1] = P(R('z0'), s * 30), [x2, y2] = P(R('z1'), s * 30);
      o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${col.line}" stroke-width="1"/>`;
      const [gx, gy] = P((R('z0') + R('z1')) / 2, s * 30 + 15);
      o += GL.glyph(SIGN_GLYPH[s], gx, gy, S * 0.032, ELEM[s % 4]);
      for (let d = 0; d < 30; d += 5) { const [a1, b1] = P(R('z0'), s * 30 + d), [a2, b2] = P(R('z0') + (d === 0 ? 0 : S * 0.008), s * 30 + d); if (d) o += `<line x1="${a1}" y1="${b1}" x2="${a2}" y2="${b2}" stroke="${col.line}" stroke-width="0.8"/>`; }
    }
    // ring separators
    o += `<circle cx="${c}" cy="${c}" r="${R('core')}" fill="#fff" stroke="${col.accent}" stroke-width="1.4"/>`;
    for (let k = 1; k < n; k++) o += `<circle cx="${c}" cy="${c}" r="${S * (core + k * bw)}" fill="none" stroke="${col.faint}" stroke-width="1.3"/>`;
    // houses of the inner chart
    opt.inner.cusps.forEach((cu, i) => {
      const angle = i % 3 === 0; const [x1, y1] = P(R('core'), cu), [x2, y2] = P(R('z0'), cu);
      o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${angle ? col.accent : col.line}" stroke-width="${angle ? 2 : 1.1}"/>`;
      const next = opt.inner.cusps[(i + 1) % 12], mid = cu + (((next - cu) + 360) % 360) / 2;
      const [hx, hy] = P(R('core') - S * 0.02, mid);
      o += `<text x="${hx}" y="${hy}" font-size="${S * 0.019}" fill="${col.soft}" text-anchor="middle" dominant-baseline="central">${i + 1}</text>`;
    });
    [['AC', opt.inner.planets.Ascendant], ['MC', opt.inner.planets.Midheaven]].filter(x => x[1] != null).forEach(([l, lon]) => { const [x, y] = P(R('z1') + S * 0.018, lon); o += `<text x="${x}" y="${y}" font-size="${S * 0.019}" font-weight="bold" fill="${col.accent}" text-anchor="middle" dominant-baseline="central">${l}</text>`; });
    // planets
    const layer = (chart, which, color) => {
      const [r0, r1] = band(which);
      const pl = { ...chart.planets }; if (pl['North Node'] != null && pl['South Node'] == null) pl['South Node'] = (pl['North Node'] + 180) % 360;
      const list = ORDER.filter(k => pl[k] != null).map(k => ({ k, lon: pl[k] }));
      if (which !== 'i' && chart.planets.Ascendant != null) list.push({ k: 'Ascendant', lon: chart.planets.Ascendant });
      const gap = Math.max(5.5, 360 * S * 0.044 / (2 * Math.PI * (r0 + r1) / 2));
      const cusps = opt.inner.cusps, near = d => cusps.reduce((m, c0) => { const x = ((d - c0 + 540) % 360) - 180; return Math.abs(x) < Math.abs(m) ? x : m; }, 999);
      spread(list, gap).map(p => { const x = near(p.d); if (Math.abs(x) < 2.2) p.d += (x >= 0 ? 1 : -1) * (2.2 - Math.abs(x)); return p; }).forEach(p => {
        const [x, y] = P(r0 + (r1 - r0) * 0.62, p.d), [tx, ty] = P(r1 - S * 0.012, p.lon), [tx2, ty2] = P(r1, p.lon);
        o += `<line x1="${tx}" y1="${ty}" x2="${tx2}" y2="${ty2}" stroke="${color}" stroke-width="1.4"/>`;
        const g = PG[p.k], small = g.length > 1;
        o += small ? `<text x="${x}" y="${y}" font-size="${S * 0.02}" font-weight="bold" fill="${color}" stroke="#fff" stroke-width="${S * 0.009}" stroke-linejoin="round" paint-order="stroke" text-anchor="middle" dominant-baseline="central">${g}</text>` : GL.glyph(g, x, y, S * 0.032, color, S * 0.009);
        const deg = Math.floor(p.lon % 30), [dx, dy] = P(r0 + (r1 - r0) * 0.25, p.d);
        o += `<text x="${dx}" y="${dy}" font-size="${S * 0.0155}" fill="${color}" stroke="#fff" stroke-width="${S * 0.007}" stroke-linejoin="round" paint-order="stroke" text-anchor="middle" dominant-baseline="central">${deg}${chart.retro && chart.retro[p.k] ? 'r' : ''}</text>`;
      });
    };
    if (opt.outer) layer(opt.outer, 't', col.t);
    if (opt.middle) layer(opt.middle, 'm', col.b);
    layer(opt.inner, 'i', col.a);
    // aspect lines between transits and the inner chart (tight orbs) in the core
    if (opt.lines) opt.lines.forEach(l => { const [x1, y1] = P(R('core'), l.a), [x2, y2] = P(R('core'), l.b); o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${l.color || col.gold}" stroke-width="1" opacity="0.8"/>`; });
    o += '</svg>';
    return o;
  }
  // tight transit-to-natal aspects for the core lines
  function aspectLines(transit, natal, orb) {
    const A = [0, 60, 90, 120, 180], out = [], C = { 0: '#a8822f', 60: '#3f6aa8', 120: '#3f6aa8', 90: '#b5523f', 180: '#b5523f' };
    Object.keys(transit.planets).forEach(t => Object.keys(natal.planets).forEach(n => {
      let d = Math.abs(transit.planets[t] - natal.planets[n]) % 360; if (d > 180) d = 360 - d;
      A.forEach(a => { if (Math.abs(d - a) <= orb && !['Moon'].includes(t)) out.push({ a: transit.planets[t], b: natal.planets[n], color: C[a] }); });
    }));
    return out;
  }
  const api = { svg, aspectLines, PG };
  if (typeof module !== 'undefined') module.exports = api; else root.TriWheel = api;
})(typeof window !== 'undefined' ? window : globalThis);
