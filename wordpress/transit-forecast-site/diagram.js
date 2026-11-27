// Small configuration diagram: a few points on a zodiac circle with aspect lines. Node + browser.
(function (root) {
  const GL = (typeof module !== 'undefined' && typeof require !== 'undefined') ? require('./glyphs.js') : root.SR11Glyphs;
  const SG = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
  const SN = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
  const COL = { a: '#5b3f8c', b: '#b0476b', t: '#2f7a78', open: '#8f7bb8' };
  const ACOL = { 180: '#b5523f', 90: '#b5523f', 0: '#a8822f', 120: '#3f6aa8', 60: '#3f6aa8' };
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  function svg(d) {
    const S = 520, SW = 820, c = S / 2, cx0 = SW / 2, R = 150, rot = d.rotate || 0;
    const P = (r, lon) => { const a = Math.PI + (lon - rot) * Math.PI / 180; return [cx0 + r * Math.cos(a), c - r * Math.sin(a)]; };
    let o = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SW} ${S}" width="${SW}" height="${S}" font-family="Helvetica, Arial, sans-serif"><rect width="${SW}" height="${S}" fill="#fff"/>`;
    o += `<circle cx="${cx0}" cy="${c}" r="${R + 22}" fill="#f7f3fc" stroke="#5b3f8c" stroke-width="1.6"/><circle cx="${cx0}" cy="${c}" r="${R}" fill="#fff" stroke="#8f7bb8" stroke-width="1.3"/>`;
    for (let s = 0; s < 12; s++) { const [x1, y1] = P(R, s * 30), [x2, y2] = P(R + 22, s * 30), [gx, gy] = P(R + 11, s * 30 + 15); o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#8f7bb8" stroke-width="1"/>` + GL.glyph(SG[s], gx, gy, 13, '#7a6a9e'); }
    (d.lines || []).forEach(([i, j, asp, dash]) => { const [x1, y1] = P(R - 4, d.points[i].lon), [x2, y2] = P(R - 4, d.points[j].lon); o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${ACOL[asp] || '#888'}" stroke-width="2.4" ${dash ? 'stroke-dasharray="6 5" opacity="0.7"' : ''}/>`; });
    const labs = d.points.map(p => { const [x, y] = P(R - 4, p.lon), [lx, ly] = P(R + 40, p.lon); return { p, x, y, lx, ly, side: lx < cx0 - 20 ? -1 : lx > cx0 + 20 ? 1 : 0 }; });
    [-1, 0, 1].forEach(sd => { const g = labs.filter(l => l.side === sd).sort((a, b) => a.ly - b.ly); for (let i = 1; i < g.length; i++) if (g[i].ly - g[i - 1].ly < 38) g[i].ly = g[i - 1].ly + 38; });
    labs.forEach(({ p, x, y, lx, ly, side }) => {
      const col = COL[p.who];
      if (p.who === 'open') o += `<circle cx="${x}" cy="${y}" r="7" fill="#fff" stroke="${col}" stroke-width="2" stroke-dasharray="3 2"/>`;
      else o += `<circle cx="${x}" cy="${y}" r="7" fill="${col}" stroke="#fff" stroke-width="1.5"/>`;
      const tx = side < 0 ? lx - 6 : side > 0 ? lx + 6 : lx, anchor = side < 0 ? 'end' : side > 0 ? 'start' : 'middle';
      const ty = side === 0 ? (ly < c ? ly - 10 : ly + 14) : ly;
      const deg = Math.floor(p.lon % 30) + '\u00B0 ' + SN[Math.floor(p.lon / 30)];
      o += `<text x="${tx}" y="${ty - 3}" font-size="15" font-weight="bold" fill="${col}" text-anchor="${anchor}">${esc(p.label)}</text><text x="${tx}" y="${ty + 14}" font-size="13" fill="#54476e" text-anchor="${anchor}">${esc(deg)}</text>`;
    });
    if (d.center) o += `<text x="${cx0}" y="${c}" font-size="15" fill="#54476e" text-anchor="middle" dominant-baseline="central" font-style="italic">${esc(d.center)}</text>`;
    return o + '</svg>';
  }
  const api = { svg, COL };
  if (typeof module !== 'undefined') module.exports = api; else root.ConfigDiagram = api;
})(typeof window !== 'undefined' ? window : globalThis);
