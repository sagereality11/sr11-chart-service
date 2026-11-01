/* Sage Reality 11 · shared birth-place search and chart service client (sitewide).
   Used by the calculators and readings that used to look up time zones in the browser.
   Birthplaces come from the site's GeoNames search; the birth time is converted to UTC
   by the chart service, which applies Sage Reality 11's historical time zone corrections
   and, for births before 1970, an optional time zone taken from the birth record.
   Nov 2026: for US births from April to October in 1946-1966 (when each town chose its own
   daylight saving time), visitors are asked whether their town's clocks were set forward.
   No ampersand characters anywhere in this file. */
(function (global) {
  'use strict';
  if (global.SR11Chart) return;
  var REST = '/wp-json/sr11bc/v1/';
  var BODY_KEYS = { sun: 'Sun', moon: 'Moon', mercury: 'Mercury', venus: 'Venus', mars: 'Mars', jupiter: 'Jupiter',
    saturn: 'Saturn', uranus: 'Uranus', neptune: 'Neptune', pluto: 'Pluto', chiron: 'Chiron',
    north_node: 'NNode', south_node: 'SNode' };
  var ANGLE_KEYS = { asc: 'ASC', mc: 'MC', ic: 'IC', dsc: 'DSC' };
  var RECORD_ZONES = [
    ['', 'Same as my birthplace (recommended)'],
    ['-300', 'Eastern Standard Time (EST, UTC-5)'],
    ['-240', 'Eastern Daylight or War Time (EDT or EWT, UTC-4)'],
    ['-360', 'Central Standard Time (CST, UTC-6)'],
    ['-300', 'Central Daylight or War Time (CDT or CWT, UTC-5)'],
    ['-420', 'Mountain Standard Time (MST, UTC-7)'],
    ['-360', 'Mountain Daylight or War Time (MDT or MWT, UTC-6)'],
    ['-480', 'Pacific Standard Time (PST, UTC-8)'],
    ['-420', 'Pacific Daylight or War Time (PDT or PWT, UTC-7)'],
    ['-240', 'Atlantic Standard Time (AST, UTC-4)'],
    ['-600', 'Hawaii Standard Time (HST, UTC-10)']
  ];
  var OTHER_OFFSETS = [-720, -660, -600, -570, -540, -480, -420, -360, -300, -240, -210, -180, -120, -60, 0, 60, 120, 180, 210, 240, 270, 300, 330, 345, 360, 390, 420, 480, 525, 540, 570, 600, 630, 660, 720, 765, 780, 840];
  /* US zones whose standard time did not change between 1946 and 1966 (minutes from UTC).
     Indiana, Kentucky, Michigan and North Dakota zones are left out on purpose: their
     standard time moved in those years, so the birth record choice is the safer route. */
  var DST_ZONES = { 'America/New_York': -300, 'America/Chicago': -360, 'America/Denver': -420,
    'America/Boise': -420, 'America/Los_Angeles': -480 };

  function rest(path, opts) {
    opts = opts || {};
    opts.credentials = 'same-origin';
    opts.headers = Object.assign({ 'X-SR11-Request': '1' }, opts.headers || {});
    return fetch(REST + path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return { http: r.status, json: j }; });
    });
  }
  function fail(message) { var e = new Error(message); e.sr11 = true; return e; }
  function offsetLabel(m) {
    var s = m < 0 ? '-' : '+', a = Math.abs(m), h = Math.floor(a / 60), mm = a % 60;
    return 'UTC' + s + h + (mm ? ':' + String(mm).padStart(2, '0') : '');
  }
  function injectCss() {
    if (document.getElementById('sr11-chart-client-css')) return;
    var css = document.createElement('style'); css.id = 'sr11-chart-client-css';
    css.textContent = '.sr11-rectz{margin:.6rem 0 0}.sr11-rectz label{display:block;font-size:.9rem;margin:0 0 .3rem}' +
      '.sr11-rectz select{width:100%;max-width:100%;padding:.55rem .6rem;border-radius:8px;border:1px solid rgba(124,77,170,.35);background:#fff;color:#3a2a4f;font:inherit;font-size:.95rem}' +
      '.sr11-rectz p{font-size:.8rem;margin:.35rem 0 0;opacity:.8;line-height:1.45}' +
      '.sr11-rectz .sr11-dstq{margin:0 0 .8rem}' +
      '.sr11-choice{display:block;margin:.45rem 0 0;padding:.5rem .8rem;border-radius:8px;border:1px solid rgba(124,77,170,.45);background:#fff;color:#3a2a4f;cursor:pointer;font:inherit;font-size:.9rem;text-align:left}';
    document.head.appendChild(css);
  }

  /* Birthplace search on an existing text input and suggestions box.
     onPick(place) receives { id, label, lat, lon, tz }; it is called with null while typing.
     The picked place is also kept on the input (input.sr11Place) for the daylight question. */
  function attachCitySearch(input, sugg, onPick) {
    var timer = null, seq = 0;
    input.addEventListener('input', function () {
      input.sr11Place = null;
      onPick(null);
      var q = input.value.trim(), my = ++seq;
      if (timer) clearTimeout(timer);
      if (q.length < 2) { sugg.hidden = true; sugg.innerHTML = ''; return; }
      timer = setTimeout(function () {
        rest('places?q=' + encodeURIComponent(q)).then(function (r) {
          if (my !== seq) return;
          var rs = (r.json ? r.json.results : null) || [];
          sugg.innerHTML = '';
          if (!rs.length) { sugg.innerHTML = '<div class="city-suggestion-item city-error">No matches. Try a nearby larger city.</div>'; sugg.hidden = false; return; }
          rs.slice(0, 8).forEach(function (p) {
            var it = document.createElement('div'); it.className = 'city-suggestion-item'; it.textContent = p.label;
            it.addEventListener('click', function () {
              input.value = p.label; sugg.hidden = true;
              input.sr11Place = { tz: p.tz, cc: p.country_code };
              onPick({ id: p.id, label: p.label, lat: p.lat, lon: p.lon, tz: p.tz });
              input.dispatchEvent(new Event('change', { bubbles: true }));
            });
            sugg.appendChild(it);
          });
          sugg.hidden = false;
        }).catch(function () {
          sugg.innerHTML = '<div class="city-suggestion-item city-error">Could not reach location search right now.</div>'; sugg.hidden = false;
        });
      }, 350);
    });
  }

  /* Optional "time zone on your birth record" choice, placed under the city field and
     shown only for birth dates before 1970. getDate() returns "YYYY-MM-DD" or "".
     For US births from April to October 1946-1966 it also asks whether the town used
     daylight saving time. A birth record time zone, when chosen, wins over that answer. */
  var recordBoxes = [];
  function attachRecordZone(cityInput, getDate) {
    injectCss();
    var field = cityInput.closest('.bd-field') || cityInput.parentNode;
    var box = document.createElement('div'); box.className = 'bd-field sr11-rectz'; box.hidden = true;
    var id = (cityInput.id || 'city') + '-record-tz';
    var html = '<div class="sr11-dstq" hidden><label for="' + id + '-dst">Did your birth town set its clocks forward for daylight saving time that day?</label>' +
      '<select id="' + id + '-dst"><option value="">Not sure (use our best records)</option>' +
      '<option value="yes">Yes, clocks were set forward an hour</option>' +
      '<option value="no">No, clocks stayed on standard time</option></select>' +
      '<p>From 1946 to 1966 each US town chose for itself whether to use daylight saving time, so two towns in the same state could be an hour apart. If your birth record or family knows, choose it here.</p></div>';
    html += '<label for="' + id + '">Born before 1970? Time zone on your birth record (optional)</label><select id="' + id + '">';
    RECORD_ZONES.forEach(function (z) { html += '<option value="' + z[0] + '">' + z[1] + '</option>'; });
    html += '<optgroup label="Other UTC offsets">';
    OTHER_OFFSETS.forEach(function (m) { html += '<option value="' + m + '">' + offsetLabel(m) + '</option>'; });
    html += '</optgroup></select><p>Older records sometimes used a different time zone than today. If your birth certificate states one, choose it here. Otherwise leave the first option.</p>';
    box.innerHTML = html;
    field.parentNode.insertBefore(box, field.nextSibling);
    var sel = box.querySelector('#' + id);
    var dstWrap = box.querySelector('.sr11-dstq'), dstSel = dstWrap.querySelector('select');
    var rec = { input: cityInput, box: box, select: sel, dstWrap: dstWrap, dstSel: dstSel, std: null,
      lookedFor: null, timer: null };
    /* Calculators with their own city picker do not set input.sr11Place, so look the
       chosen town up once its name settles (the first search result is used). */
    function lookUpTown() {
      var v = cityInput.value.trim();
      var pl = cityInput.sr11Place || null;
      if (pl ? (pl.auto ? pl.label !== v : false) : false) { cityInput.sr11Place = null; pl = null; }
      if (pl ? true : (v.length < 3 ? true : rec.lookedFor === v)) return;
      if (rec.timer) clearTimeout(rec.timer);
      rec.timer = setTimeout(function () {
        rec.lookedFor = v;
        rest('places?q=' + encodeURIComponent(v.split(',')[0])).then(function (r) {
          var rs = (r.json ? r.json.results : null) || [];
          var hit = rs.filter(function (p) { return p.label === v; })[0] || rs[0];
          if (hit ? cityInput.value.trim() === v : false) {
            cityInput.sr11Place = { tz: hit.tz, cc: hit.country_code, auto: true, label: v };
            refresh();
          }
        }).catch(function () {});
      }, 600);
    }
    function refresh() {
      var d = getDate ? getDate() : '';
      var ok = /^\d{4}-\d{2}/.test(d || '');
      var y = ok ? parseInt(d.slice(0, 4), 10) : null, mo = ok ? parseInt(d.slice(5, 7), 10) : null;
      box.hidden = !(y !== null ? y < 1970 : false);
      if (!box.hidden) lookUpTown();
      var pl = cityInput.sr11Place || null;
      var std = pl ? (pl.cc === 'US' ? DST_ZONES[pl.tz] : undefined) : undefined;
      var inEra = y !== null ? (y >= 1946 ? (y <= 1966 ? (mo >= 4 ? mo <= 10 : false) : false) : false) : false;
      var askDst = std !== undefined ? inEra : false;
      dstWrap.hidden = !askDst;
      rec.std = askDst ? std : null;
    }
    rec.refresh = refresh;
    document.addEventListener('input', refresh, true);
    document.addEventListener('change', refresh, true);
    setTimeout(refresh, 0);
    recordBoxes.push(rec);
    return function () { refresh(); return readOffset(rec); };
  }
  /* Minutes from UTC chosen by the visitor, or null to let the chart service decide. */
  function readOffset(b) {
    if (b.box.hidden) return null;
    if (b.select.value !== '') return parseInt(b.select.value, 10);
    if (b.std === null) return null;
    if (b.dstSel.value === 'yes') return b.std + 60;
    if (b.dstSel.value === 'no') return b.std;
    return null;
  }
  function recordOffset(cityInput) {
    for (var i = 0; i < recordBoxes.length; i++) {
      if (recordBoxes[i].input === cityInput) {
        var b = recordBoxes[i]; b.refresh();
        return readOffset(b);
      }
    }
    return null;
  }
  /* For calculators that build their own request body: adds the visitor's birth record
     time zone or daylight answer to body.location (place mode only). Returns body. */
  function withRecordOffset(body, cityInput) {
    var m = recordOffset(cityInput);
    var loc = body ? body.location : null;
    if (m !== null ? (loc ? loc.mode === 'place' : false) : false) loc.record_offset_minutes = m;
    return body;
  }

  /* When a birth time happened twice (clocks set back), ask which one. */
  function askFold(anchor, res) {
    injectCss();
    return new Promise(function (resolve) {
      var box = document.createElement('div'); box.className = 'sr11-rectz';
      box.innerHTML = '<p>' + (res.message || 'That birth time happened twice because the clocks were set back. Which one was it?') + '</p>';
      (res.options || []).forEach(function (o) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'sr11-choice';
        b.textContent = o.label;
        b.addEventListener('click', function () { box.remove(); resolve(o.fold); });
        box.appendChild(b);
      });
      var field = anchor ? (anchor.closest('.bd-field') || anchor.parentNode) : document.body;
      field.parentNode.insertBefore(box, field.nextSibling);
      box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  /* Calls the chart service. o = { date: "YYYY-MM-DD", time: "HH:MM" or null (local noon is used),
     place: picked place or null (no city: noon UTC at 0,0, as the calculators did before),
     recordOffset: minutes or null, anchor: the city input (for the fold question),
     points, asteroids: optional extras }. Resolves to the service JSON. */
  function getChart(o) {
    var p = o.date.split('-').map(Number), t = o.time ? o.time.split(':').map(Number) : [12, 0];
    var body = { year: p[0], month: p[1], day: p[2], hour: t[0], minute: t[1], time_known: true, house_system: 'P',
      points: o.points || [], node: 'true', aspects: [], asteroids: o.asteroids || [] };
    if (o.place) {
      body.location = { mode: 'place', place_id: o.place.id };
      if (o.recordOffset !== null ? o.recordOffset !== undefined : false) body.location.record_offset_minutes = o.recordOffset;
    } else {
      body.location = { mode: 'manual', lat: 0, lon: 0, utc_offset_minutes: 0 };
    }
    function call(b, note) {
      return rest('chart', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) }).then(function (r) {
        var j = r.json || {};
        if (j.status === 'ok') { if (note) (j.warnings = j.warnings || []).push(note); return j; }
        if (j.status === 'ambiguous') return askFold(o.anchor, j).then(function (fold) { return call(Object.assign({}, b, { fold: fold }), note); });
        if (j.status === 'needs_confirmation') return call(Object.assign({}, b, { accept_lmt: true }), 'Your birth date comes from before standardized time zones in your birth city, so local mean time was used.');
        if (j.status === 'nonexistent') throw fail('That birth time was skipped when the clocks went forward in your birth city. Please check the time on your birth record.');
        if (/house/i.test(String(j.code || '') + String(j.message || ''))) {
          b.house_system = 'W';
          return call(b, 'Placidus houses cannot be calculated this close to the poles, so whole sign houses were used.');
        }
        throw fail(j.message || 'Something went wrong calculating your chart. Please try again in a moment.');
      });
    }
    return call(body, null);
  }

  /* The chart in the shape the older calculators use:
     { points: { Sun ... Pluto, Chiron, NNode, SNode, ASC, MC, IC, DSC }, cusps: { 1: longitude, ... 12: longitude },
       birthUTCDate: Date, service: <full service JSON> } */
  function toLegacy(j) {
    var points = {};
    (j.bodies || []).forEach(function (b) { if (BODY_KEYS[b.id]) points[BODY_KEYS[b.id]] = b.lon; });
    var ang = (j.houses ? j.houses.angles : null) || {};
    Object.keys(ANGLE_KEYS).forEach(function (k) { if (ang[k]) points[ANGLE_KEYS[k]] = ang[k].lon; });
    var cusps = {};   /* keyed by house number 1 to 12, like the older calculators */
    ((j.houses ? j.houses.cusps : null) || []).forEach(function (c) { cusps[c.house] = c.lon; });
    return { points: points, cusps: cusps, birthUTCDate: new Date(j.time.utc_iso), service: j };
  }
  function legacyChart(o) { return getChart(o).then(toLegacy); }

  global.SR11Chart = { rest: rest, attachCitySearch: attachCitySearch, attachRecordZone: attachRecordZone,
    recordOffset: recordOffset, withRecordOffset: withRecordOffset, getChart: getChart, toLegacy: toLegacy, legacyChart: legacyChart };
})(window);
