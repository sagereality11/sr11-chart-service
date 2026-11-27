/* Monthly Transit Forecast + Shared Soul Journey: site app (Sage Reality 11).
   Buyer portal (#tm-app, inside #sr-tm-app) and free calculator (#tm-free).
   The chart service writes the reading (Swiss Ephemeris); this file draws the wheels, the web view and the PDF. */
(function (W) {
  'use strict';
  var C = W.TMConfig || {};
  var PDF_LIB_URL = 'https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js';
  var REL = [['romantic', 'Romantic partners'], ['spouse', 'Spouses'], ['mother_son', 'Mother and son'], ['mother_daughter', 'Mother and daughter'],
    ['father_son', 'Father and son'], ['father_daughter', 'Father and daughter'], ['parent_child', 'Parent and child'], ['siblings', 'Siblings'],
    ['grandparent', 'Grandparent and grandchild'], ['friends', 'Friends'], ['business', 'Business partners']];
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function load(src, ok) { return new Promise(function (res, rej) { if (ok()) return res(); var s = document.createElement('script'); s.src = src; s.onload = function () { res(); }; s.onerror = rej; document.head.appendChild(s); }); }
  function chartSvc() { return new Promise(function (res) { (function w(n) { if (W.SR11Chart) return res(W.SR11Chart); if (n > 200) return res(null); setTimeout(function () { w(n + 1); }, 50); })(0); }); }
  function save(bytes, name) { var b = new Blob([bytes], { type: 'application/pdf' }), u = URL.createObjectURL(b), a = document.createElement('a'); a.href = u; a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { a.remove(); }, 4000); return u; }

  /* ---------- form pieces */
  function personHtml(pre, title, isOther) {
    return '<fieldset class="tm-person" id="' + pre + '-box"><legend>' + esc(title) + '</legend><div class="tm-grid">'
      + '<div class="tm-field"><label for="' + pre + '-name">First name</label><input type="text" id="' + pre + '-name" maxlength="40" autocomplete="' + (isOther ? 'off' : 'given-name') + '"></div>'
      + '<div class="tm-field"><label for="' + pre + '-pron">Pronouns</label><select id="' + pre + '-pron"><option value="she">she / her</option><option value="he">he / him</option><option value="they">they / them</option></select></div>'
      + '<div class="tm-field"><label for="' + pre + '-date">Birth date</label><input type="date" id="' + pre + '-date" min="1900-01-01" max="2059-12-31"></div>'
      + '<div class="tm-field"><label for="' + pre + '-time">Birth time (local)</label><input type="time" id="' + pre + '-time"></div>'
      + '<label class="tm-check" for="' + pre + '-notime"><input type="checkbox" id="' + pre + '-notime"> Birth time unknown</label>'
      + '<div class="tm-field tm-wide bd-field"><label for="' + pre + '-city">Birth city</label><input type="text" id="' + pre + '-city" placeholder="Start typing, then choose from the list" autocomplete="off"><div class="city-suggestions" id="' + pre + '-city-suggestions" hidden></div></div>'
      + '</div><p class="tm-note">Please check the time zone shown for the birth city. Many programs get older time zones wrong, so if a birth certificate shows a different zone, choose it in the box that appears under the city.</p></fieldset>';
  }
  function setupPerson(pre) {
    var st = { place: null };
    chartSvc().then(function (svc) {
      if (!svc) return;
      svc.attachCitySearch($(pre + '-city'), $(pre + '-city-suggestions'), function (p) { st.place = p || null; });
      if (svc.attachRecordZone) svc.attachRecordZone($(pre + '-city'), function () { return $(pre + '-date').value; });
    });
    var nt = $(pre + '-notime'), tm = $(pre + '-time');
    nt.addEventListener('change', function () { tm.disabled = nt.checked; if (nt.checked) tm.value = ''; });
    document.addEventListener('click', function (e) { var b = $(pre + '-city-suggestions'); if (b ? (e.target !== $(pre + '-city') ? !b.contains(e.target) : false) : false) b.hidden = true; });
    return st;
  }
  function personBody(pre, st, who) {
    var name = $(pre + '-name').value.trim(), date = $(pre + '-date').value, time = $(pre + '-time').value, nt = $(pre + '-notime').checked;
    if (!name) return 'Please add a first name for ' + who + '.';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return 'Please enter the full birth date for ' + who + '.';
    if (!nt ? !/^\d{2}:\d{2}/.test(time) : false) return 'Please enter the birth time for ' + who + ', or tick "Birth time unknown".';
    if (!st.place) return 'Please start typing the birth city for ' + who + ' and choose it from the list.';
    var d = date.split('-'), b = { name: name, pronoun: $(pre + '-pron').value, year: +d[0], month: +d[1], day: +d[2], location: { mode: 'place', place_id: st.place.id } };
    if (nt) b.time_known = false; else { var t = time.split(':'); b.hour = +t[0]; b.minute = +t[1]; }
    return W.SR11Chart ? W.SR11Chart.withRecordOffset(b, $(pre + '-city')) : b;
  }

  /* ---------- wheels and diagrams */
  function natalLines(c) {
    var ks = Object.keys(c.planets).filter(function (k) { return ['North Node', 'Ascendant', 'Midheaven'].indexOf(k) < 0; }), o = [], A = [[60, 4, '#3f6aa8'], [90, 6, '#b5523f'], [120, 6, '#3f6aa8'], [180, 6, '#b5523f']];
    for (var i = 0; i < ks.length; i++) for (var j = i + 1; j < ks.length; j++) { var d = Math.abs(c.planets[ks[i]] - c.planets[ks[j]]) % 360; if (d > 180) d = 360 - d; A.forEach(function (x) { if (Math.abs(d - x[0]) <= x[1]) o.push({ a: c.planets[ks[i]], b: c.planets[ks[j]], color: x[2] }); }); }
    return o;
  }
  function natalSvg(r, key) { var c = r.charts[key]; return W.TriWheel.svg({ inner: c, size: 640, lines: natalLines(c) }); }
  function imageSvg(r, im) { var inner = r.charts[im.inner], mid = im.middle ? r.charts[im.middle] : null, outer = r.charts[im.outer]; return W.TriWheel.svg({ inner: inner, middle: mid, outer: outer, size: 640, lines: W.TriWheel.aspectLines(outer, inner, 1.0) }); }
  function svgToPng(svg, width) {
    return new Promise(function (res, rej) {
      var img = new Image(), url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
      img.onload = function () {
        var h = Math.round(width * (img.naturalHeight || img.height) / (img.naturalWidth || img.width)), cv = document.createElement('canvas');
        cv.width = width; cv.height = h; var x = cv.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, width, h); x.drawImage(img, 0, 0, width, h);
        URL.revokeObjectURL(url);
        cv.toBlob(function (b) { b.arrayBuffer().then(function (ab) { res(new Uint8Array(ab)); }); }, 'image/png');
      };
      img.onerror = function () { URL.revokeObjectURL(url); rej(new Error('image')); };
      img.src = url;
    });
  }
  function makePdf(r) {
    var files = {}, jobs = [], n = 0;
    r.parts.forEach(function (p) { p.sections.forEach(function (s) {
      if (s.natal) { var f = 'n_' + s.natal.key + '.png'; if (!files[f]) { files[f] = 1; jobs.push(svgToPng(natalSvg(r, s.natal.key), 1100).then(function (b) { files[f] = b; })); } }
      if (s.image) { var f2 = 'w' + (n++) + '.png'; s.image.file = f2; jobs.push(svgToPng(imageSvg(r, s.image), 1100).then(function (b) { files[f2] = b; })); }
      if (s.diagram) { var f3 = 'd' + (n++) + '.png'; s.diagram.file = f3; jobs.push(svgToPng(W.ConfigDiagram.svg(s.diagram.data), 1200).then(function (b) { files[f3] = b; })); }
    }); });
    return Promise.all(jobs).then(function () { r._loadImage = function (f) { return files[f]; }; return W.TrnPDF.make(r, W.PDFLib); });
  }

  /* ---------- web view with a section menu */
  function webView(r) {
    var nav = '<nav class="tm-nav"><p class="tm-nav-h">In this reading</p><ol>', body = '';
    r.parts.forEach(function (p, i) {
      nav += '<li><a href="#tm-p' + i + '">' + esc(p.title) + '</a></li>';
      body += '<section class="tm-part" id="tm-p' + i + '"><p class="tm-eye">Part ' + (i + 1) + '</p><h2>' + esc(p.title) + '</h2>' + (p.intro ? '<p class="tm-intro">' + esc(p.intro) + '</p>' : '');
      (p.opening || []).forEach(function (t) { body += '<p>' + esc(t) + '</p>'; });
      p.sections.forEach(function (s) {
        body += '<div class="tm-sec">' + (s.eyebrow ? '<p class="tm-eye">' + esc(s.eyebrow) + '</p>' : '') + '<h3>' + esc(s.title) + '</h3>' + (s.sub ? '<p class="tm-sub">' + esc(s.sub) + '</p>' : '');
        if (s.diagram) body += '<figure class="tm-fig">' + W.ConfigDiagram.svg(s.diagram.data) + (s.diagram.caption ? '<figcaption>' + esc(s.diagram.caption) + '</figcaption>' : '') + '</figure>';
        (s.paras || []).forEach(function (t) { body += '<p' + (s.italic ? ' class="tm-int"' : '') + '>' + esc(t) + '</p>'; });
        if (s.natal) body += '<figure class="tm-fig tm-wheel">' + natalSvg(r, s.natal.key) + '</figure>';
        if (s.image) body += '<figure class="tm-fig tm-wheel">' + imageSvg(r, s.image) + '<figcaption>' + esc(s.image.caption || '') + '</figcaption></figure>';
        if (s.table) { body += '<div class="tm-tw"><table><thead><tr>' + s.table.head.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' + s.table.rows.map(function (row) { return '<tr>' + row.map(function (c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>'; }
        if (s.grid) { body += '<ul class="tm-list">' + s.grid.items.map(function (it) { return '<li><b>' + it[0] + '</b> ' + esc(it[1]) + '</li>'; }).join('') + '</ul>'; }
        (s.after || []).forEach(function (t) { body += '<p>' + esc(t) + '</p>'; });
        (s.blocks || []).forEach(function (b) { body += '<h4>' + esc(b.h) + '</h4>' + b.paras.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join(''); });
        if (s.bullets) body += '<ul class="tm-list">' + s.bullets.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul>';
        if (s.octTable) body += '<div class="tm-tw"><table><thead><tr><th>The lower octave</th><th>The higher octave</th></tr></thead><tbody>' + s.octTable.map(function (x) { return '<tr><td>' + esc(x[0]) + '</td><td>' + esc(x[1]) + '</td></tr>'; }).join('') + '</tbody></table></div>';
        if (s.octave) body += '<div class="tm-oct"><p><b>The lower octave</b> ' + esc(s.octave[0]) + '</p><p><b>The higher octave</b> ' + esc(s.octave[1]) + '</p></div>';
        if (s.story) body += '<p class="tm-story">' + esc(s.story) + '</p>';
        if (s.close) body += '<p class="tm-close">' + esc(s.close) + '</p>';
        if (s.practice) body += '<p class="tm-k">Your practice</p><p>' + esc(s.practice) + '</p>';
        if (s.questions) body += '<p class="tm-k">Questions to sit with</p><ul class="tm-q">' + s.questions.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul>';
        (s.reflect || []).forEach(function (x) { body += '<p class="tm-k">' + esc(x[0]) + '</p><p class="tm-int">' + esc(x[1]) + '</p>'; });
        if (s.prompt) body += '<p class="tm-k">Journal</p><p class="tm-int">' + esc(s.prompt) + '</p>';
        body += '</div>';
      });
      body += '</section>';
    });
    nav += '<li><a href="#tm-final">Final Thoughts</a></li></ol></nav>';
    body += '<section class="tm-part" id="tm-final"><h2>Final Thoughts</h2><p class="tm-sub">' + esc(r.finalSub || '') + '</p>' + r.final.map(function (t) { return typeof t === 'string' ? '<p>' + esc(t) + '</p>' : '<p class="tm-close">' + esc(t.bold) + '</p>'; }).join('') + '<p class="tm-sign">With Love and Light,<br>Tiff</p></section>';
    var head = '<header class="tm-head"><p class="tm-eye">' + esc(r.title || 'Your Monthly Transit Forecast') + ' · ' + esc(r.month) + '</p>' + r.letter.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('') + '</header>';
    return '<div class="tm-view">' + nav + '<div class="tm-body">' + head + body + '</div></div>';
  }

  /* ---------- buyer portal */
  function initPortal() {
    var app = $('tm-app'); if (!app) return;
    var mode = C.mode || 'solo';
    var months = (C.months || []).map(function (m) { return '<option value="' + esc(m[0]) + '">' + esc(m[1]) + '</option>'; }).join('');
    var h = '';
    if (mode === 'both') h += '<div class="tm-tabs" role="tablist"><button type="button" class="tm-tab on" data-m="solo">Just me</button><button type="button" class="tm-tab" data-m="pair">Two of us</button></div>';
    var PA = C.pre || 'tm-a';
    h += personHtml(PA, 'You', false);
    h += '<div id="tm-pairbits"' + (mode === 'pair' ? '' : ' hidden') + '><div class="tm-field tm-wide"><label for="tm-rel">How are the two of you connected?</label><select id="tm-rel">' + REL.map(function (x) { return '<option value="' + x[0] + '">' + x[1] + '</option>'; }).join('') + '</select></div>' + personHtml('tm-b', 'The other person', true) + '</div>';
    h += '<div class="tm-grid"><div class="tm-field"><label for="tm-month">Your forecast month</label><select id="tm-month">' + months + '</select></div>'
      + '<div class="tm-field"><label for="tm-node">Lunar Node</label><select id="tm-node"><option value="true">True Node (recommended)</option><option value="mean">Mean Node</option></select></div></div>';
    if (C.locked) h += '<p class="tm-note">This order is for your ' + esc(C.locked) + ' forecast. You can create it again here anytime, for example to correct birth details.</p>';
    h += '<button type="button" class="tm-btn" id="tm-go">Create My Forecast</button><p class="tm-status" id="tm-status" role="status"></p>';
    app.innerHTML = h;
    var sa = setupPerson(PA), sb = setupPerson('tm-b'), cur = mode === 'pair' ? 'pair' : 'solo', last = null;
    app.querySelectorAll('.tm-tab').forEach(function (b) { b.addEventListener('click', function () { cur = b.getAttribute('data-m'); app.querySelectorAll('.tm-tab').forEach(function (x) { x.classList.toggle('on', x === b); }); $('tm-pairbits').hidden = cur !== 'pair'; }); });
    var status = $('tm-status'), btn = $('tm-go');
    function msg(t, html) { if (html) status.innerHTML = t; else status.textContent = t; }
    function send(extra) {
      var a = personBody(PA, sa, 'you'); if (typeof a === 'string') return msg(a);
      var body = a; body.order = C.order; body.key = C.key; body.forecast = $('tm-month').value; body.node = $('tm-node').value;
      try { body.forecast_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { body.forecast_tz = ''; }
      if (cur === 'pair') { var b = personBody('tm-b', sb, 'the other person'); if (typeof b === 'string') return msg(b); body.partner = b; body.relationship = $('tm-rel').value; }
      Object.keys(extra || {}).forEach(function (k) { body[k] = extra[k]; if (body.partner ? (k === 'accept_lmt') : false) body.partner[k] = extra[k]; });
      btn.disabled = true; msg('Reading ' + (cur === 'pair' ? 'both charts' : 'your chart') + ' against this month’s sky. This takes about half a minute...');
      fetch(C.endpoint, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-SR11-Request': '1', 'X-WP-Nonce': C.nonce }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); })
        .then(function (x) {
          var j = x.j || {};
          if (x.s === 200 ? !!j.reading : false) {
            var out = $('tm-out'); out.innerHTML = webView(j.reading); out.hidden = false;
            msg('Your forecast is ready and shows below. Creating your PDF now...');
            return load(PDF_LIB_URL, function () { return !!W.PDFLib; }).then(function () { return makePdf(j.reading); }).then(function (bytes) {
              if (last) URL.revokeObjectURL(last); var u = last = save(bytes, j.filename || 'Monthly-Transit-Forecast.pdf');
              msg('Your forecast is downloading now and is also below. If the download did not start, <a href="' + u + '" download="' + esc(j.filename) + '">tap here to open it</a>. A copy is on its way to your email too.', true);
            });
          }
          if (j.status === 'ambiguous') {
            msg('A birth time happened twice on that date because the clocks went back. Which one was it? <button type="button" class="tm-btn tm-mini" id="tm-f0">The first one</button> <button type="button" class="tm-btn tm-mini" id="tm-f1">The second one</button>', true);
            $('tm-f0').onclick = function () { send({ fold: 0 }); }; $('tm-f1').onclick = function () { send({ fold: 1 }); }; return;
          }
          if (j.status === 'needs_confirmation') return send({ accept_lmt: true });
          msg(j.message || 'Something went wrong creating your forecast. Please try again in a minute.');
        })
        .catch(function (e) { if (W.console) console.error(e); msg('We could not finish your forecast. Please check your connection and try again.'); })
        .then(function () { btn.disabled = false; });
    }
    btn.addEventListener('click', function () { send({}); });
  }

  /* ---------- free calculator */
  function initFree() {
    var app = $('tm-free'); if (!app) return;
    var h = '<div class="tm-tabs" role="tablist"><button type="button" class="tm-tab on" data-m="solo">Just me</button><button type="button" class="tm-tab" data-m="pair">Two of us</button></div>'
      + personHtml('tf-a', 'You', false)
      + '<div id="tf-pairbits" hidden><div class="tm-field tm-wide"><label for="tf-rel">How are the two of you connected?</label><select id="tf-rel">' + REL.map(function (x) { return '<option value="' + x[0] + '">' + x[1] + '</option>'; }).join('') + '</select></div>' + personHtml('tf-b', 'The other person', true) + '</div>'
      + '<div class="tm-grid"><div class="tm-field"><label for="tf-node">Lunar Node</label><select id="tf-node"><option value="true">True Node (recommended)</option><option value="mean">Mean Node</option></select></div></div>'
      + '<button type="button" class="tm-btn" id="tf-go">Show My Month</button><p class="tm-status" id="tf-status" role="status"></p><div id="tf-out" hidden></div>';
    app.innerHTML = h;
    var sa = setupPerson('tf-a'), sb = setupPerson('tf-b'), cur = 'solo';
    app.querySelectorAll('.tm-tab').forEach(function (b) { b.addEventListener('click', function () { cur = b.getAttribute('data-m'); app.querySelectorAll('.tm-tab').forEach(function (x) { x.classList.toggle('on', x === b); }); $('tf-pairbits').hidden = cur !== 'pair'; }); });
    var st = $('tf-status'), btn = $('tf-go');
    btn.addEventListener('click', function () {
      var a = personBody('tf-a', sa, 'you'); if (typeof a === 'string') { st.textContent = a; return; }
      a.node = $('tf-node').value; try { a.forecast_tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { /* none */ }
      if (cur === 'pair') { var b = personBody('tf-b', sb, 'the other person'); if (typeof b === 'string') { st.textContent = b; return; } a.partner = b; a.relationship = $('tf-rel').value; }
      btn.disabled = true; st.textContent = 'Looking at this month’s sky...';
      fetch(C.preview, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-SR11-Request': '1', 'X-WP-Nonce': C.nonce }, body: JSON.stringify(a) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j ? true : j.status !== 'ok') { st.textContent = (j ? j.message : '') || 'Something went wrong. Please try again in a minute.'; return; }
          var r = j.snapshot, o = '<div class="tm-snap"><p class="tm-eye">' + esc(r.month) + (r.pair ? ' · ' + esc(r.names) : '') + '</p><h3>' + esc(r.theme) + '</h3>';
          o += '<figure class="tm-fig tm-wheel">' + W.TriWheel.svg({ inner: r.charts.a, middle: r.charts.b || null, outer: r.charts.t, size: 640, lines: W.TriWheel.aspectLines(r.charts.t, r.charts.a, 1.0) }) + '<figcaption>' + esc(r.caption) + '</figcaption></figure>';
          o += '<p>' + esc(r.lead) + '</p><p class="tm-k">The biggest currents this month</p><ul class="tm-list">' + r.currents.map(function (c) { return '<li><b>' + esc(c[0]) + '</b>' + (c[1] ? ' · ' + esc(c[1]) : '') + '</li>'; }).join('') + '</ul>';
          o += '<p class="tm-k">What the full forecast adds</p><p>' + esc(r.more) + '</p></div>';
          o += '<div class="tm-offers"><div class="tm-offer"><h4>Your Monthly Transit Forecast</h4><p>Your whole month in a story: the season you are in, the big currents, your nodes, personal planets, New and Full Moon, a calendar and your charts.</p><a class="tm-btn" href="' + esc(C.soloUrl) + '">Get My Forecast' + (C.soloPrice ? ' · ' + esc(C.soloPrice) : '') + '</a></div>'
            + '<div class="tm-offer"><h4>Your Shared Soul Journey</h4><p>The month for two charts at once, written from your relationship’s lens, with the soul agreements between you and where this month touches you both.</p><a class="tm-btn" href="' + esc(C.pairUrl) + '">Get Our Forecast' + (C.pairPrice ? ' · ' + esc(C.pairPrice) : '') + '</a></div></div>';
          $('tf-out').innerHTML = o; $('tf-out').hidden = false; st.textContent = '';
        })
        .catch(function () { st.textContent = 'We could not reach the calculator. Please check your connection and try again.'; })
        .then(function () { btn.disabled = false; });
    });
  }
  function init() { initPortal(); initFree(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})(window);
