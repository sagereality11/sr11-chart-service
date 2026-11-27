// Monthly Transit Forecast PDF. Same kit and look as AlmPDF / SectPDF / FirdPDF (Times body, Helvetica labels,
// purple accent, double-border white cover, two-pass clickable Contents, lined journal prompts, bookmarks pane).
let lib = null;
function clean(t) { return String(t == null ? '' : t).replace(/[′’‘]/g, "'").replace(/[“”]/g, '"').replace(/[–—]/g, ', ').replace(/…/g, '...').replace(/[^\x20-\x7E -ÿ]/g, '').replace(/ {2,}/g, ' ').trim(); }
const NUMS = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve'];

async function make(r, L) {
  lib = L || (typeof window !== 'undefined' && window.PDFLib) || require('pdf-lib');
  async function render(pages, withToc) {
    const doc = await lib.PDFDocument.create();
    doc.setTitle((r.title || 'Your Monthly Transit Forecast') + ', ' + r.month); doc.setAuthor('Tiff, Sage Reality 11');
    const St = lib.StandardFonts, rgb = lib.rgb;
    const F = { r: await doc.embedFont(St.TimesRoman), i: await doc.embedFont(St.TimesRomanItalic), b: await doc.embedFont(St.TimesRomanBold), m: await doc.embedFont(St.Helvetica), mb: await doc.embedFont(St.HelveticaBold) };
    const C = { INK: rgb(0.17, 0.10, 0.32), DIM: rgb(0.38, 0.32, 0.50), ACC: rgb(0.42, 0.25, 0.72), LINE: rgb(0.86, 0.81, 0.94), WASH: rgb(0.961, 0.941, 0.988) };
    const W = 612, H = 792, M = 70, CW = W - 2 * M;
    const header = 'SAGE REALITY 11  ·  ' + (r.title || 'Your Monthly Transit Forecast').toUpperCase() + '  ·  ' + r.month.toUpperCase();
    const K = { page: null, y: 0, pageNo: 0 }, found = {}, tocLinks = [];
    const imgs = {}; for (const p of r.parts) for (const sec of p.sections) for (const f of [sec.image && sec.image.file, sec.natal && 'n_' + sec.natal.key + '.png', sec.diagram && sec.diagram.file]) if (f && !imgs[f]) imgs[f] = await doc.embedPng(await r._loadImage(f));
    K.newPage = () => { K.page = doc.addPage([W, H]); K.pageNo++; K.y = H - M; if (K.pageNo > 1) { K.page.drawText(header, { x: M, y: H - 40, size: 7, font: F.m, color: C.ACC }); K.page.drawText(String(K.pageNo), { x: W - M - 8, y: 36, size: 8, font: F.m, color: C.DIM }); } };
    K.affIdx = 0;
    K.ensure = h => { if (K.y - h < M) { if (!K.noFill && K.y - M > 105) K.fill(); K.newPage(); } };
    // fill a large leftover gap with an affirmation and writing lines instead of white space
    K.fill = () => {
      K.noFill = true; K.fillN = (K.fillN || 0) + 1; const aff = K.fillN % 2 === 1 ? (r.affirmations || [])[K.affIdx] : null;
      K.y -= 8;
      if (aff && K.y - M > 210) {
        K.affIdx++; const ls = K.wrap(aff, F.i, 13, CW - 40), bh = ls.length * 19 + 34;
        K.page.drawRectangle({ x: M, y: K.y - bh, width: CW, height: bh, color: C.WASH, borderColor: C.LINE, borderWidth: 0.6 });
        K.page.drawText('AN AFFIRMATION FOR YOU', { x: M + 20, y: K.y - 16, size: 7, font: F.m, color: C.ACC });
        ls.forEach((ln, i) => K.page.drawText(ln, { x: M + 20, y: K.y - 34 - i * 19, size: 13, font: F.i, color: C.ACC }));
        K.y -= bh + 16;
      }
      if (K.y - M > 60) { K.page.drawText('YOUR NOTES', { x: M, y: K.y - 8, size: 7, font: F.m, color: C.ACC }); K.y -= 10; K.lines(Math.floor((K.y - M - 6) / 24)); }
      K.noFill = false;
    };
    K.annot = obj => { const ctx = doc.context, A = lib.PDFName.of('Annots'); const ref = ctx.register(ctx.obj(obj)); const arr = K.page.node.lookup(A); if (arr) arr.push(ref); else K.page.node.set(A, ctx.obj([ref])); };
    K.addLink = (url, x, yb, w, h) => K.annot({ Type: 'Annot', Subtype: 'Link', Rect: [x, yb, x + w, yb + h], Border: [0, 0, 0], A: { Type: 'Action', S: 'URI', URI: lib.PDFString.of(url) } });
    K.wrap = (text, font, size, width) => { const words = clean(text).split(/\s+/), lines = []; let cur = ''; words.forEach(w => { const t = cur ? cur + ' ' + w : w; if (cur && font.widthOfTextAtSize(t, size) > width) { lines.push(cur); cur = w; } else cur = t; }); if (cur) lines.push(cur); return lines; };
    K.para = (text, o) => {
      o = o || {}; const font = o.font || F.r, size = o.size || 11.5, lh = o.lh || size * 1.5, color = o.color || C.INK, x = o.x || M, width = o.width || CW;
      const lines = K.wrap(text, font, size, width);
      lines.forEach((ln, i) => {
        if (i === 0) K.ensure(Math.min(lines.length, 2) * lh); else if (lines.length - i === 2) K.ensure(2 * lh); else K.ensure(lh);
        const dx = o.center ? (W - font.widthOfTextAtSize(ln, size)) / 2 : x;
        K.page.drawText(ln, { x: dx, y: K.y - size, size, font, color });
        if (o.link) K.addLink(o.link, dx, K.y - size - 2, font.widthOfTextAtSize(ln, size), size + 4);
        K.y -= lh;
      });
      K.y -= (o.after == null ? 8 : o.after);
    };
    K.label = t => { K.ensure(110); K.y -= 6; K.para(t.toUpperCase(), { font: F.m, size: 7.5, color: C.ACC, after: 6, lh: 11 }); };
    K.title = (t, size) => { K.ensure(90); K.para(t, { font: F.i, size: size || 19, lh: (size || 19) * 1.3, after: 8 }); };
    K.rule = () => { K.ensure(20); K.page.drawLine({ start: { x: M, y: K.y - 4 }, end: { x: W - M, y: K.y - 4 }, thickness: 0.6, color: C.LINE }); K.y -= 20; };
    K.small = t => { K.ensure(48); K.para(t.toUpperCase(), { font: F.m, size: 7, color: C.ACC, after: 2, lh: 10 }); };
    K.part = (num, title, intro) => { K.newPage(); K.y -= 30; K.para('PART ' + num.toUpperCase(), { font: F.m, size: 8, color: C.ACC, after: 8 }); K.para(title, { font: F.i, size: 28, lh: 34, after: 14 }); K.page.drawLine({ start: { x: M, y: K.y }, end: { x: M + 60, y: K.y }, thickness: 0.8, color: C.ACC }); K.y -= 22; if (intro) K.para(intro, { font: F.i, color: C.DIM, after: 14 }); };
    K.lines = n => { for (let k = 0; k < n; k++) { K.y -= 24; K.page.drawLine({ start: { x: M, y: K.y }, end: { x: W - M, y: K.y }, thickness: 0.5, color: C.LINE }); } };
    K.journal = q => { const ql = K.wrap(q, F.i, 11.5, CW).length * 17.25 + 24; let n = Math.min(5, Math.floor((K.y - M - ql - 10) / 24)); if (n < 3) { K.newPage(); n = 5; } K.small('Journal'); K.para(q, { font: F.i }); K.lines(n); K.y -= 16; };
    // a question with its own writing lines (3), kept together
    K.question = q => { const h = K.wrap(q, F.i, 11.5, CW).length * 17.25 + 3 * 24 + 22; K.ensure(h); K.para(q, { font: F.i, after: 0 }); K.lines(3); K.y -= 18; };
    K.notes = () => { if (K.y - M < 95) return; K.fill(); };
    // table: head [..], rows [[..]], widths fractions
    K.table = t => {
      const cols = t.widths.map(f => f * CW), pad = 6, size = 9.5, lh = 12.5;
      const fbs = t.firstBold || [0]; const rowH = cells => Math.max(...cells.map((c, j) => K.wrap(c, fbs.includes(j) ? F.b : F.r, size, cols[j] - 2 * pad).length)) * lh + 2 * pad - 2;
      const drawHead = () => { K.ensure(28 + rowH(t.rows[0])); K.page.drawRectangle({ x: M, y: K.y - 20, width: CW, height: 20, color: C.WASH }); let x = M; t.head.forEach((h, j) => { K.page.drawText(clean(h).toUpperCase(), { x: x + pad, y: K.y - 13.5, size: 6.8, font: F.m, color: C.ACC }); x += cols[j]; }); K.y -= 20; };
      drawHead();
      t.rows.forEach((row, i) => {
        const h = rowH(row);
        if (K.y - h < M) { K.newPage(); drawHead(); }
        let x = M; const fb = t.firstBold || [0]; row.forEach((c, j) => { const bb = fb.includes(j); const ls = K.wrap(c, bb ? F.b : F.r, size, cols[j] - 2 * pad); ls.forEach((ln, k) => K.page.drawText(ln, { x: x + pad, y: K.y - pad - size + 1 - k * lh, size, font: bb ? F.b : F.r, color: bb ? C.ACC : C.INK })); x += cols[j]; });
        K.y -= h; K.page.drawLine({ start: { x: M, y: K.y }, end: { x: W - M, y: K.y }, thickness: 0.4, color: C.LINE });
      });
      K.y -= 16;
    };

    const SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
    const WD = r.charts;
    const posTxt = l => { const s = Math.floor(l / 30), d = l % 30; let dd = Math.floor(d), m = Math.round((d - dd) * 60); if (m === 60) { dd++; m = 0; } return dd + '°' + String(m).padStart(2, '0') + "' " + SIGNS[s]; };
    const houseOf = (c, l) => { for (let i = 0; i < 12; i++) { const a = c[i], b = c[(i + 1) % 12]; if (((l - a) % 360 + 360) % 360 < ((b - a) % 360 + 360) % 360) return i + 1; } return 1; };
    K.natal = (nat) => {
      const ch = WD[nat.key], img = imgs['n_' + nat.key + '.png'], w = 262, h = w * img.height / img.width;
      const keys = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North Node', 'South Node', 'Ascendant', 'Midheaven'];
      const top = K.y; K.page.drawImage(img, { x: M - 6, y: top - h, width: w, height: h });
      const tx = M + w + 4, tw = W - M - tx, c1 = 0.36 * tw, c2 = 0.5 * tw, rh = 16.5; let y = top - 4;
      K.page.drawRectangle({ x: tx, y: y - 16, width: tw, height: 16, color: C.WASH });
      [['PLANET', 0], ['POSITION', c1], ['HOUSE', c1 + c2]].forEach(([t, dx]) => K.page.drawText(t, { x: tx + 5 + dx, y: y - 11, size: 6.5, font: F.m, color: C.ACC })); y -= 16;
      keys.filter(k => k === 'South Node' ? ch.planets['North Node'] != null : ch.planets[k] != null).forEach(k => { const lon = k === 'South Node' ? (ch.planets['North Node'] + 180) % 360 : ch.planets[k], hs = k === 'Ascendant' || k === 'Midheaven' ? '' : String(houseOf(ch.cusps, lon)) + (ch.solar ? '' : '');
        K.page.drawText(k + (ch.retro && ch.retro[k] ? ' R' : ''), { x: tx + 5, y: y - 12, size: 9, font: F.b, color: C.ACC });
        K.page.drawText(posTxt(lon), { x: tx + 5 + c1, y: y - 12, size: 9, font: F.r, color: C.INK });
        K.page.drawText(hs, { x: tx + 5 + c1 + c2, y: y - 12, size: 9, font: F.r, color: C.INK });
        y -= rh; K.page.drawLine({ start: { x: tx, y }, end: { x: tx + tw, y }, thickness: 0.4, color: C.LINE }); });
      K.y = Math.min(top - h, y) - 10;
      K.para('R marks a planet that was retrograde at birth. NN and SN are the North and South Node, and AC and MC are the Ascendant and Midheaven.', { font: F.i, size: 8.5, color: C.DIM, after: 6 });
    };
    K.grid = g => {
      if (K.y - M < 380) { K.newPage(); K.y -= 10; } else K.y -= 4;
      K.para(g.title, { font: F.i, size: 22, lh: 26, after: 4 });
      if (g.sub) K.para(g.sub, { font: F.i, size: 10.5, color: C.DIM, after: 6 });
      const WHO = { a: C.ACC, b: rgb(0.69, 0.28, 0.42), both: rgb(0.66, 0.51, 0.18) };
      if (g.legend) { let x = M; g.legend.forEach(([k, t]) => { K.page.drawCircle({ x: x + 3, y: K.y - 4, size: 3, color: WHO[k] }); K.page.drawText(clean(t), { x: x + 10, y: K.y - 7, size: 8, font: F.m, color: C.DIM }); x += 20 + F.m.widthOfTextAtSize(clean(t), 8) + 14; }); K.y -= 18; }
      const first = new Date(Date.UTC(g.year, g.month - 1, 1)).getUTCDay(), days = new Date(Date.UTC(g.year, g.month, 0)).getUTCDate();
      const weeks = Math.ceil((first + days) / 7), cw = CW / 7, top = K.y, hh = 16, ch = (top - hh - M - 18) / weeks;
      ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach((d, i) => { K.page.drawRectangle({ x: M + i * cw, y: top - hh, width: cw, height: hh, color: C.WASH, borderColor: C.LINE, borderWidth: 0.6 }); K.page.drawText(d.toUpperCase(), { x: M + i * cw + 5, y: top - 11, size: 7, font: F.m, color: C.ACC }); });
      for (let wk = 0; wk < weeks; wk++) for (let i = 0; i < 7; i++) {
        const day = wk * 7 + i - first + 1, x = M + i * cw, y = top - hh - (wk + 1) * ch;
        K.page.drawRectangle({ x, y, width: cw, height: ch, borderColor: C.LINE, borderWidth: 0.6 });
        if (day < 1 || day > days) continue;
        const its = g.items.filter(t => t[0] === day), star = its.some(t => t[3]);
        if (star) K.page.drawRectangle({ x: x + 0.6, y: y + 0.6, width: cw - 1.2, height: ch - 1.2, color: rgb(0.985, 0.965, 0.92) });
        K.page.drawText(String(day), { x: x + 4, y: y + ch - 11, size: 9, font: star ? F.mb : F.m, color: star ? WHO.both : C.INK });
        let ly = y + ch - 21;
        its.forEach(t => { const lines = K.wrap(t[1], F.m, 6.4, cw - 12); K.page.drawCircle({ x: x + 5, y: ly + 2.2, size: 1.6, color: WHO[t[2] || 'a'] }); lines.forEach(ln => { if (ly > y + 3) K.page.drawText(ln, { x: x + 9, y: ly, size: 6.4, font: t[3] ? F.mb : F.m, color: C.INK }); ly -= 7.6; }); ly -= 1.5; });
      }
      K.y = top - hh - weeks * ch - 10;
      K.page.drawText(clean(g.foot || 'Shaded days are the most important of the month. Times and full details are in the Key Dates table.'), { x: M, y: K.y - 8, size: 8.5, font: F.i, color: C.DIM });
    };
    // Cover emblem: crescent Moon inside a ring of twelve points (the twelve houses a month moves through)
    K.coverMark = (cx, cy) => {
      K.page.drawCircle({ x: cx, y: cy, size: 34, borderColor: C.ACC, borderWidth: 0.7 });
      for (let k = 0; k < 12; k++) { const a = Math.PI / 2 + k * 2 * Math.PI / 12; K.page.drawCircle({ x: cx + 44 * Math.cos(a), y: cy + 44 * Math.sin(a), size: k % 3 === 0 ? 2.6 : 1.6, color: C.ACC }); }
      K.page.drawCircle({ x: cx, y: cy, size: 16, color: C.ACC });
      K.page.drawCircle({ x: cx + 7, y: cy + 4, size: 14.5, color: rgb(1, 1, 1) });
    };

    // ---------- Cover
    K.newPage(); K.y = H - 150;
    K.page.drawRectangle({ x: 24, y: 24, width: W - 48, height: H - 48, borderColor: C.ACC, borderWidth: 2.5 });
    K.page.drawRectangle({ x: 32, y: 32, width: W - 64, height: H - 64, borderColor: C.LINE, borderWidth: 0.8 });
    K.coverMark(W / 2, K.y + 50); K.y -= 20;
    K.para('SAGE REALITY 11  ·  ' + (r.coverQ || 'WHAT IS THIS MONTH ASKING OF ME?'), { font: F.m, size: 8, color: C.ACC, center: true, after: 12 });
    K.para(r.title || 'Your Monthly Transit Forecast', { font: F.i, size: 28, center: true, lh: 34, after: r.titleSub ? 2 : 6 }); if (r.titleSub) K.para(r.titleSub, { font: F.m, size: 9, color: C.ACC, center: true, after: 8 });
    K.para(r.month, { font: F.i, size: 17, color: C.ACC, center: true, after: 10 });
    if (r.pair) { K.para('Prepared for ' + r.name + ' and ' + r.other, { size: 12.5, center: true, after: 2 }); K.para(r.birthLabel, { size: 10.5, color: C.DIM, center: true, after: 0 }); K.para(r.birthLabel2, { size: 10.5, color: C.DIM, center: true, after: 6 }); }
    else { K.para('Prepared for ' + r.name, { size: 12.5, center: true, after: 2 }); K.para('Born ' + r.birthLabel, { size: 11.5, color: C.DIM, center: true, after: 6 }); }
    K.para(r.tagline, { font: F.i, size: 11.5, color: C.DIM, center: true, after: 22 });
    K.rule();
    r.letter.forEach(p => K.para(p, { size: 12.5, lh: 19 }));

    // ---------- Contents
    if (withToc) {
      K.newPage(); K.y -= 30;
      K.para('Contents', { font: F.i, size: 28, lh: 34, after: 14 });
      K.page.drawLine({ start: { x: M, y: K.y }, end: { x: M + 60, y: K.y }, thickness: 0.8, color: C.ACC }); K.y -= 22;
      const entry = (label, key, sub) => {
        const size = sub ? 10 : 12, font = sub ? F.r : F.i, x = sub ? M + 16 : M;
        K.ensure(sub ? 16 : 22);
        const lab = clean(label), pgs = String(pages[key] || ''), lw = font.widthOfTextAtSize(lab, size), pw = F.m.widthOfTextAtSize(pgs, 8.5);
        K.page.drawText(lab, { x, y: K.y - size, size, font, color: sub ? C.DIM : C.INK });
        K.page.drawLine({ start: { x: x + lw + 8, y: K.y - size + 2 }, end: { x: W - M - pw - 8, y: K.y - size + 2 }, thickness: 0.4, color: C.LINE, dashArray: [1, 3] });
        K.page.drawText(pgs, { x: W - M - pw, y: K.y - size, size: 8.5, font: F.m, color: C.ACC });
        tocLinks.push({ page: K.page, target: pages[key], rect: [x, K.y - size - 3, W - M, K.y + 2] });
        K.y -= sub ? 15 : 21;
      };
      r.parts.forEach((p, n) => { entry('Part ' + NUMS[n] + '  ·  ' + p.title, 'p' + n); p.sections.forEach((s, j) => entry(s.title, 'p' + n + 's' + j, true)); K.y -= 4; });
      entry('Final Thoughts', 'final');
      entry('How This Reading Is Calculated', 'method');
    }

    // ---------- Body
    r.parts.forEach((p, n) => {
      K.part(NUMS[n], p.title, p.intro); found['p' + n] = K.pageNo;
      (p.opening || []).forEach(t => K.para(t)); if ((p.opening || []).length) K.y -= 6;
      p.sections.forEach((s, j) => {
        if (s.diagram) { const im = imgs[s.diagram.file], dw = s.diagram.w || 360; K.ensure(dw * im.height / im.width + 150); }
        if (s.grid) { K.grid(s.grid); found['p' + n + 's' + j] = K.pageNo; K.y = M; return; }
        if (s.natal) { if (j > 0 || K.y - M < 380) K.newPage(); found['p' + n + 's' + j] = K.pageNo; if (s.eyebrow) K.label(s.eyebrow); K.title(s.title); s.paras.forEach(t => K.para(t)); K.natal(s.natal); return; }
        if (j > 0) { K.ensure(160); K.rule(); }
        if (s.image) { const img = imgs[s.image.file], w = s.image.w || 400; K.ensure(w * img.height / img.width + 60 + s.paras.reduce((a, t) => a + K.wrap(t, F.r, 11.5, CW).length * 17.25 + 8, 0) + 40); }
        K.ensure(s.table && !s.paras.length ? 130 : 170); found['p' + n + 's' + j] = K.pageNo;
        if (s.eyebrow) K.label(s.eyebrow); K.title(s.title);
        if (s.sub) K.para(s.sub, { font: F.i, color: C.DIM, after: 10 });
        if (s.diagram) { const img = imgs[s.diagram.file], w = s.diagram.w || 360, h = w * img.height / img.width; K.ensure(h + 34); K.page.drawImage(img, { x: (W - w) / 2, y: K.y - h, width: w, height: h }); K.y -= h + 4; if (s.diagram.caption) K.para(s.diagram.caption, { font: F.i, size: 9.5, color: C.DIM, center: true, after: 10 }); }
        s.paras.forEach(t => K.para(t, s.italic ? { font: F.i, size: 12.5, lh: 19, color: C.ACC, after: 12 } : {}));
        if (s.table) K.table(s.table);
        if (s.image) { const img = imgs[s.image.file], w = s.image.w || 400, h = w * img.height / img.width; K.ensure(h + 30); K.page.drawImage(img, { x: (W - w) / 2, y: K.y - h, width: w, height: h }); K.y -= h + 6; K.para(s.image.caption || (!r.pair ? 'Inner ring your birth chart   ·   Outer ring ' + r.month + ' transits' : ''), { font: F.m, size: 7, color: C.DIM, center: true, after: 10 }); }
        (s.after || []).forEach(t => K.para(t));
        (s.blocks || []).forEach(b => { K.ensure(90); K.y -= 2; K.para(b.h, { font: F.i, size: 14, lh: 18, color: C.ACC, after: 4 }); b.paras.forEach(t => K.para(t)); });
        (s.bullets || []).forEach(t => K.para('\u2022  ' + t, { x: M + 8, width: CW - 8, after: 4 }));
        if (s.octTable) { K.y -= 2; K.ensure(s.octTable.length * 26 + 34); K.table({ head: ['The lower octave', 'The higher octave'], widths: [0.5, 0.5], rows: s.octTable, firstBold: [] }); }
        if (s.octave) { const oh = K.wrap(s.octave[0], F.i, 11.5, CW).length + K.wrap(s.octave[1], F.i, 11.5, CW).length, chh = s.close ? K.wrap(s.close, F.b, 13, CW).length * 19 + 20 : 0; K.ensure(oh * 17.25 + 60 + chh); K.small('The lower octave'); K.para(s.octave[0], { font: F.i }); K.small('The higher octave'); K.para(s.octave[1], { font: F.i }); }
        if (s.story) { K.ensure(K.wrap(s.story, F.i, 13.5, CW).length * 19 + 14); K.y -= 2; K.para(s.story, { font: F.i, size: 13.5, lh: 19, color: C.ACC, after: 12 }); }
        if (s.close) { K.ensure(K.wrap(s.close, F.b, 13, CW).length * 19 + 20); K.y -= 4; K.para(s.close, { font: F.b, size: 13, lh: 19, color: C.ACC, after: 14 }); }
        if (s.practice) { const ph = K.wrap(s.practice, F.r, 11.5, CW).length * 17.25 + 40; K.ensure(ph); K.small('Your practice'); K.para(s.practice); }
        if (s.questions) { K.ensure(130); K.small('Questions to sit with'); K.y -= 4; s.questions.forEach(q => K.question(q)); }
        (s.reflect || []).forEach(([l, q]) => { const h = K.wrap(q, F.i, 11.5, CW).length * 17.25 + 3 * 24 + 40; K.ensure(h); K.small(l); K.question(q); });
        if (s.prompt) K.journal(s.prompt);
      });
      K.notes();
    });

    // ---------- Final Thoughts
    K.newPage(); K.y -= 4; found.final = K.pageNo;
    K.para('Final Thoughts', { font: F.i, size: 26, lh: 30, after: 6 });
    if (r.finalSub) K.para(r.finalSub, { font: F.i, size: 15, color: C.DIM, after: 10 });
    const fh = sz => r.final.reduce((a, p) => a + (typeof p === 'string' ? K.wrap(p, F.r, sz, CW).length * sz * 1.5 + 8 : K.wrap(p.bold, F.b, 13, CW).length * 19 + 18), 0) + 64;
    const fsz = fh(11.5) <= K.y - M ? 11.5 : fh(11) <= K.y - M ? 11 : 11.5;
    r.final.forEach((p, i) => {
      const last = i === r.final.length - 1;
      if (last && typeof p === 'string') { K.noFill = true; K.ensure(K.wrap(p, F.r, fsz, CW).length * fsz * 1.5 + 70); K.noFill = false; }
      if (typeof p === 'string') K.para(p, { size: fsz }); else { K.ensure(60); K.y -= 4; K.para(p.bold, { font: F.b, size: 13, lh: 19, color: C.ACC, after: 14 }); }
    });
    K.y -= 4; K.noFill = true; K.ensure(48); K.noFill = false;
    K.para('With Love and Light,', { font: F.i, size: 14, color: C.DIM, after: 0 });
    K.para('Tiff', { font: F.i, size: 14, color: C.DIM, after: 18 });
    K.ensure(110); K.rule();
    K.label('Keep Exploring');
    r.more.forEach(l => { K.ensure(44); K.para(l.name, { size: 11, color: C.ACC, link: l.url, after: 1 }); K.para(l.why, { font: F.i, size: 10, color: C.DIM, after: 8 }); });

    K.notes();
    // ---------- Method (last page)
    K.newPage(); K.y -= 30; found.method = K.pageNo;
    K.para('How This Reading Is Calculated', { font: F.i, size: 22, lh: 28, after: 12 });
    r.method.forEach(p => K.para(p, { size: 10.5, color: C.DIM }));
    K.rule();
    r.fine.forEach(f => K.para(f, { font: F.i, size: 9, color: C.DIM, lh: 13 }));

    const all = doc.getPages();
    tocLinks.forEach(l => { if (!l.target || !all[l.target - 1]) return; K.page = l.page; K.annot({ Type: 'Annot', Subtype: 'Link', Rect: l.rect, Border: [0, 0, 0], Dest: [all[l.target - 1].ref, lib.PDFName.of('Fit')] }); });
    return { doc, found, tocPages: 0 };
  }
  // pass 1 without contents; measure how many pages the contents takes, then shift
  const p1 = await render({}, false);
  const pre = await render(Object.fromEntries(Object.keys(p1.found).map(k => [k, p1.found[k] + 1])), true);
  const shift = pre.doc.getPageCount() - p1.doc.getPageCount();
  const pages = {}; Object.keys(p1.found).forEach(k => pages[k] = p1.found[k] + shift);
  const p2 = await render(pages, true);
  addOutline(p2.doc, r, p2.found);
  return p2.doc.save();
}

function addOutline(doc, r, found) {
  const ctx = doc.context, N = n => lib.PDFName.of(n), pages = doc.getPages();
  const dest = pg => ctx.obj([pages[pg - 1].ref, N('XYZ'), null, null, null]);
  const items = [{ title: 'Welcome', page: 1 }, { title: 'Contents', page: 2 }].concat(r.parts.map((p, n) => ({ title: 'Part ' + NUMS[n] + ': ' + clean(p.title), page: found['p' + n],
    kids: p.sections.map((s, j) => ({ title: clean(s.title), page: found['p' + n + 's' + j] })) })));
  items.push({ title: 'Final Thoughts', page: found.final }, { title: 'How This Reading Is Calculated', page: found.method });
  const rootRef = ctx.nextRef();
  function build(list, parentRef) {
    const refs = list.map(() => ctx.nextRef()); let count = 0;
    list.forEach((it, i) => {
      const d = { Title: lib.PDFHexString.fromText(it.title), Parent: parentRef, Dest: dest(it.page) };
      if (i > 0) d.Prev = refs[i - 1]; if (i < list.length - 1) d.Next = refs[i + 1];
      if (it.kids && it.kids.length) { const k = build(it.kids, refs[i]); d.First = k.first; d.Last = k.last; d.Count = -k.count; }
      ctx.assign(refs[i], ctx.obj(d)); count++;
    });
    return { first: refs[0], last: refs[refs.length - 1], count };
  }
  const top = build(items, rootRef);
  ctx.assign(rootRef, ctx.obj({ Type: 'Outlines', First: top.first, Last: top.last, Count: top.count }));
  doc.catalog.set(N('Outlines'), rootRef); doc.catalog.set(N('PageMode'), N('UseOutlines'));
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { make, clean };
  if (require.main === module) {
    const r = require(process.argv[2]);
    r._loadImage = f => require('fs').readFileSync(f);
    make(r).then(b => { require('fs').writeFileSync(process.argv[3], b); console.log('wrote', process.argv[3], b.length); });
  }
} else { window.TrnPDF = { make, clean }; }
