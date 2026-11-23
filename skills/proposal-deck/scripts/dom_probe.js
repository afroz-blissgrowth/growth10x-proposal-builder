/* Growth10x deck DOM probe. Injected by qa_render.py after the deck script, run in headless Chrome with --dump-dom.
   window.QA_MODE = 'layout' (default): tests interactions, then lays out every slide at its final build and every
   mockup, and reports overflow, clipping, off-stage, footer clearance, text collisions, timeline pin alignment,
   contrast and fonts. window.QA_MODE = 'anim': walks the deck with the keyboard and counts running animations
   about 300ms after each slide or build appears. Results go into a JSON script element with the id qa-probe-out. */
(function () {
  'use strict';
  var MODE = window.QA_MODE || 'layout';
  var stage = document.getElementById('stage');
  var slides = [].slice.call(document.querySelectorAll('#stage > .slide'));
  var mzs = [].slice.call(document.querySelectorAll('#stage > .mz'));
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function out(obj) {
    var s = document.createElement('script'); s.type = 'application/json'; s.id = 'qa-probe-out';
    s.textContent = JSON.stringify(obj); document.body.appendChild(s);
  }
  function scale() { return stage.getBoundingClientRect().width / 1920; }
  function rel(el) {
    var sr = stage.getBoundingClientRect(), r = el.getBoundingClientRect(), k = scale();
    return { x: (r.left - sr.left) / k, y: (r.top - sr.top) / k, w: r.width / k, h: r.height / k, r: (r.right - sr.left) / k, b: (r.bottom - sr.top) / k };
  }
  function path(el) {
    var p = [], n = el;
    while (n && n !== stage && p.length < 4) {
      var s = n.tagName.toLowerCase();
      if (n.id) { s += '#' + n.id; p.unshift(s); break; }
      var c = (n.getAttribute('class') || '').trim().split(/\s+/).filter(function (x) { return x && ['in', 'vis', 'on', 'glass'].indexOf(x) < 0; }).slice(0, 2);
      if (c.length) s += '.' + c.join('.');
      p.unshift(s); n = n.parentElement;
    }
    return p.join(' > ');
  }
  function ownText(el) {
    var t = '';
    for (var i = 0; i < el.childNodes.length; i++) if (el.childNodes[i].nodeType === 3) t += el.childNodes[i].textContent;
    return t.replace(/\s+/g, ' ').trim();
  }
  function effOpacity(el) { var o = 1, n = el; while (n && n !== document.body) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return o; }
  function visible(el) {
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || effOpacity(el) < 0.05) return false;
    var r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0;
  }
  var PUNCT = /^[\s\u00B7\u2022|\/\u2192\u2190\u00D7+&:.,()\-]*$/;
  function meaningful(el) { var t = ownText(el); return t.length > 0 && !PUNCT.test(t); }
  /* the box of the text itself (not the element box, which can be full width) */
  function textRect(el) {
    var sr = stage.getBoundingClientRect(), k = scale(), x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, any = false;
    for (var i = 0; i < el.childNodes.length; i++) {
      var n = el.childNodes[i]; if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      var rg = document.createRange(); rg.selectNodeContents(n);
      [].slice.call(rg.getClientRects()).forEach(function (q) { if (q.width < 1) return; any = true; x0 = Math.min(x0, q.left); y0 = Math.min(y0, q.top); x1 = Math.max(x1, q.right); y1 = Math.max(y1, q.bottom); });
    }
    if (!any) return rel(el);
    var o = { x: (x0 - sr.left) / k, y: (y0 - sr.top) / k, r: (x1 - sr.left) / k, b: (y1 - sr.top) / k };
    /* a block with a tight line-height (big numbers at 1.0) has glyph boxes taller than its line box: clamp to the box */
    var eb = rel(el); if (getComputedStyle(el).display !== 'inline' && eb.h > 0) { o.y = Math.max(o.y, eb.y); o.b = Math.min(o.b, eb.b); if (o.b < o.y) o.b = o.y; }
    o.w = o.r - o.x; o.h = o.b - o.y; return o;
  }
  function decorative(el) {
    return el.closest('svg, canvas, [aria-hidden="true"]') !== null && !el.closest('svg text');
  }
  /* ---------- colour ---------- */
  function parseC(s) {
    var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  }
  function over(top, bot) { var a = top.a; return { r: top.r * a + bot.r * (1 - a), g: top.g * a + bot.g * (1 - a), b: top.b * a + bot.b * (1 - a), a: 1 }; }
  function lum(c) { function f(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); } return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  var rootCS = getComputedStyle(document.documentElement);
  function tok(n) { return rootCS.getPropertyValue(n).trim(); }
  function rgbTok(n) { var p = tok(n).split(',').map(parseFloat); return { r: p[0], g: p[1], b: p[2], a: 1 }; }
  var GROUND = rgbTok('--bg-rgb');
  function bgOf(el) {
    var layers = [], n = el;
    while (n && n !== document.documentElement) {
      var cs = getComputedStyle(n);
      if (n.classList && n.classList.contains('hl')) { layers.push(rgbTok('--acc-rgb')); break; }
      var c = parseC(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 0.99) break; }
      n = n.parentElement;
    }
    var base = GROUND;
    for (var i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return base;
  }
  /* ---------- per-view checks ---------- */
  function checkView(root, label, isMockup) {
    var issues = [];
    function add(kind, el, msg, sev) { issues.push({ kind: kind, sev: sev || 'error', where: path(el), msg: msg }); }
    var els = $$('*', root).filter(function (el) { return visible(el) && !decorative(el); });
    var texts = els.filter(meaningful);
    var FOOT = 930, FOOT_MAX = 980, reportedOff = [];
    els.forEach(function (el) {
      var cs = getComputedStyle(el), r = rel(el), tag = el.tagName.toLowerCase();
      if (tag === 'canvas' || tag === 'svg') return;
      // off stage
      if ((r.x < -1 || r.y < -1 || r.r > 1921 || r.b > 1081) && !el.closest('.mz-scroll') && !el.classList.contains('fb-ph')
          && !reportedOff.some(function (p) { return p.contains(el); })) {
        reportedOff.push(el);
        add('off-stage', el, 'outside the 1920x1080 stage: x ' + Math.round(r.x) + ' y ' + Math.round(r.y) + ' right ' + Math.round(r.r) + ' bottom ' + Math.round(r.b));
      }
      // overflow and clipping
      var clipX = /(hidden|clip|auto|scroll)/.test(cs.overflowX), clipY = /(hidden|clip|auto|scroll)/.test(cs.overflowY);
      if (el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2 && (clipX || ownText(el))) {
        if (!(el.classList.contains('mz') || el.classList.contains('mz-scroll')))
          add(clipX ? 'clipped' : 'overflow', el, 'content ' + (el.scrollWidth - el.clientWidth) + 'px wider than its box');
      }
      if (el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 2 && clipY && !el.classList.contains('mz-scroll') && !el.classList.contains('rk') && el.textContent.trim()) {
        add('clipped', el, 'content ' + (el.scrollHeight - el.clientHeight) + 'px taller than its box (text cut off)');
      }
      if (cs.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1) add('clipped', el, 'text truncated with an ellipsis');
      // footer clearance (slides only)
      if (!isMockup && r.b > FOOT + 2 && el.closest('.slide') === root && cs.position !== 'absolute' && !el.closest('.src, .marks, .hint, .nav')) {
        if (meaningful(el) || el.classList.contains('glass'))
          add('footer', el, 'bottom at y ' + Math.round(r.b) + ' (aim for ' + FOOT + ', never past ' + FOOT_MAX + ')', r.b > FOOT_MAX ? 'error' : 'warn');
      }
    });
    // balance: a slide whose content stops far above the footer looks unfinished
    if (!isMockup && !/^(cover|thanks)(-|$)/.test(root.id)) {
      var low = 0; [].slice.call(root.children).forEach(function (c) { if (!visible(c) || /^(CANVAS|svg)$/i.test(c.tagName) || c.classList.contains('src')) return; low = Math.max(low, rel(c).b); });
      if (low && low < 760) issues.push({ kind: 'balance', sev: 'warn', where: root.id, msg: 'content ends at y ' + Math.round(low) + ', leaving ' + Math.round(930 - low) + 'px empty above the footer: spread or enlarge the content' });
    }
    // text inside its panel
    texts.forEach(function (el) {
      var r = textRect(el), p = el.parentElement;
      while (p && p !== root) {
        var cs = getComputedStyle(p), pb = rel(p);
        var framed = (parseFloat(cs.borderTopWidth) > 0 && parseFloat(cs.borderBottomWidth) > 0 || (parseC(cs.backgroundColor) || { a: 0 }).a > 0.05) && pb.h >= 40 && pb.w >= 80;
        if (framed && !p.classList.contains('hl') && cs.display !== 'inline') {
          var pr = rel(p);
          if (r.x < pr.x - 2 || r.r > pr.r + 2 || r.y < pr.y - 2 || r.b > pr.b + 2) add('outside-panel', el, 'text spills out of ' + path(p) + ' by ' + Math.round(Math.max(pr.x - r.x, r.r - pr.r, pr.y - r.y, r.b - pr.b)) + 'px');
          break;
        }
        p = p.parentElement;
      }
    });
    // text collisions: leaf text boxes that overlap and are not nested
    var leaves = texts.filter(function (el) { return getComputedStyle(el).display !== 'inline' || el.children.length === 0; });
    var boxes = leaves.filter(function (el) { return !el.closest('.mz-hd') || !root.classList.contains('mz-scroll'); }).map(function (el) { return { el: el, r: textRect(el) }; });
    for (var i = 0; i < boxes.length; i++) for (var j = i + 1; j < boxes.length; j++) {
      var a = boxes[i], b = boxes[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      var ox = Math.min(a.r.r, b.r.r) - Math.max(a.r.x, b.r.x), oy = Math.min(a.r.b, b.r.b) - Math.max(a.r.y, b.r.y);
      if (ox > 4 && oy > Math.max(8, 0.35 * Math.min(a.r.h, b.r.h))) add('collision', a.el, 'overlaps ' + path(b.el) + ' (' + Math.round(ox) + 'x' + Math.round(oy) + 'px)');
    }
    // contrast
    texts.forEach(function (el) {
      var cs = getComputedStyle(el); var fg = parseC(cs.color); if (!fg) return;
      var op = 1, n = el; while (n && n !== root) { op *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
      fg.a *= op;
      var bg = bgOf(el), c = ratio(over(fg, bg), bg);
      var size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
      var large = size >= 30 || (size >= 24 && bold);
      var need = large ? 3 : 4.5, floor = 3;
      if (c < floor - 0.05) add('contrast', el, 'contrast ' + c.toFixed(2) + ' (needs ' + need + ', hard floor ' + floor + ')');
      else if (c < need - 0.05) add('contrast', el, 'contrast ' + c.toFixed(2) + ' below ' + need + ' for ' + Math.round(size) + 'px text', 'warn');
    });
    // timeline pins on the bar (.tl) and milestone nodes on the track (.nt)
    $$('.tl', root).forEach(function (tl) {
      var bar = tl.querySelector('.tl-bar'); if (!bar) return;
      var br = rel(bar), cy = br.y + br.h / 2;
      $$('.tl-p', tl).forEach(function (p) {
        var ps = getComputedStyle(p, '::before'), pr = rel(p), k = 1;
        var h = parseFloat(ps.height), top = ps.top !== 'auto' ? parseFloat(ps.top) : null, bottom = ps.bottom !== 'auto' ? parseFloat(ps.bottom) : null;
        var dotTop = top !== null ? pr.y + top : pr.b - bottom - h;
        var d = dotTop + h / 2 - cy;
        if (Math.abs(d) > 2) add('pin-align', p, 'timeline dot is ' + Math.round(d) + 'px off the bar centre');
      });
    });
    $$('.nt', root).forEach(function (nt) {
      var tr = nt.querySelector('.nt-tr'); if (!tr) return;
      var t = rel(tr), cy = t.y + t.h / 2;
      $$('.nt-nd', nt).forEach(function (n) { var r = rel(n), d = r.y + r.h / 2 - cy; if (Math.abs(d) > 2) add('pin-align', n, 'milestone node is ' + Math.round(d) + 'px off the track centre'); });
    });
    // highlight height
    $$('.hl', root).forEach(function (h) {
      var bs = getComputedStyle(h).backgroundSize;
      if (bs.indexOf('86%') < 0) add('highlight', h, 'highlight background-size is ' + bs + ', expected 100% 86%', 'warn');
    });
    var metrics = null;
    if (!isMockup) metrics = slideGates(root, texts, issues, add);
    return { id: label, issues: issues, texts: texts.length, metrics: metrics };
  }

  /* ---------- slide gates: fill, empty band, heading hierarchy, count-up on number heroes ----------
     Content slides must fill the content box (x 128 to 1792, y 96 to 930): at least FILL_MIN percent of an 8px grid
     covered by text lines, panels, images and SVG, and no more than BAND_MAX px empty above the footer.
     Exempt from fill and band: cover, thanks, and any slide with data-kind="cover|thanks|agenda|hero|closing". */
  /* Calibrated on the approved ContextPath deck (25 content slides: fill mean 73%, min 58%; empty band mean 28px).
     Per slide: fill under FILL_MIN or band over BAND_MAX is an error, under FILL_WARN or over BAND_WARN a warning.
     The deck averages (fill 70% or more, band 30px or less, words 140 or more) are checked in deck_check.py. */
  var FILL_MIN = +(window.G10X_FILL_MIN || 58), FILL_WARN = +(window.G10X_FILL_WARN || 66),
      BAND_MAX = +(window.G10X_BAND_MAX || 70), BAND_WARN = +(window.G10X_BAND_WARN || 40),
      HIER_MIN = +(window.G10X_HIER_MIN || 1.2), HIER_ROW = +(window.G10X_HIER_ROW || 1.08), HIER_W = +(window.G10X_HIER_W || 200);
  function slideKind(s) {
    var k = s.getAttribute('data-kind'); if (k) return k;
    var b = s.id.replace(/-d$/, ''); return (b === 'cover' || b === 'thanks') ? b : 'content';
  }
  function isLabel(el, cs) {
    var size = parseFloat(cs.fontSize), ls = parseFloat(cs.letterSpacing) || 0;
    return cs.textTransform === 'uppercase' || ls > 0.08 * size;
  }
  function isNumeric(t) { return /^[^A-Za-z]*\d[^A-Za-z]*$/.test(t) || /^[\s\d.,%+£$€~]*\d[\s\d.,%+]*(k|m|M|bn|x)?$/.test(t); }
  function slideGates(root, texts, issues, add) {
    var kind = slideKind(root), m = { kind: kind };
    var X0 = 128, X1 = 1792, Y0 = 96, Y1 = 930, C = 8, gw = Math.ceil((X1 - X0) / C), gh = Math.ceil((Y1 - Y0) / C), grid = new Uint8Array(gw * gh), maxB = 0;
    function mark(r) {
      if (r.w < 2 || r.h < 2 || r.y > 1080 || r.x > 1920 || r.b < 0 || r.r < 0) return;
      if (r.w > 1800 && r.h > 1000) return;
      if (r.b <= 1000) maxB = Math.max(maxB, r.b);
      var cx0 = Math.max(0, Math.floor((r.x - X0) / C)), cx1 = Math.min(gw, Math.ceil((r.r - X0) / C)), cy0 = Math.max(0, Math.floor((r.y - Y0) / C)), cy1 = Math.min(gh, Math.ceil((r.b - Y0) / C));
      for (var j = cy0; j < cy1; j++) for (var i = cx0; i < cx1; i++) grid[j * gw + i] = 1;
    }
    var sr = stage.getBoundingClientRect(), k = scale();
    $$('*', root).forEach(function (el) {
      var tag = el.tagName.toLowerCase();
      if (tag === 'canvas' || tag === 'script' || tag === 'style') return;
      if (el.closest('svg') && tag !== 'svg') return;
      if (el.closest('.src, .marks, .hint')) return;
      if (!visible(el)) return;
      var cs = getComputedStyle(el), bgc = parseC(cs.backgroundColor);
      var boxy = (bgc && bgc.a > 0.01) || cs.backgroundImage !== 'none' || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0 || el.classList.contains('glass');
      if (el.classList.contains('hl')) boxy = false;
      if (tag === 'svg' || tag === 'img' || boxy) { mark(rel(el)); return; }
      var own = false; for (var c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3 && c.textContent.trim()) { own = true; break; }
      if (own) {
        var rg = document.createRange(); rg.selectNodeContents(el);
        [].slice.call(rg.getClientRects()).forEach(function (q) { mark({ x: (q.left - sr.left) / k, y: (q.top - sr.top) / k, w: q.width / k, h: q.height / k, r: (q.right - sr.left) / k, b: (q.bottom - sr.top) / k }); });
      }
    });
    var filled = 0; for (var t = 0; t < grid.length; t++) filled += grid[t];
    m.fill = Math.round(1000 * filled / grid.length) / 10; m.bottom = Math.round(maxB); m.emptyBand = Math.round(930 - maxB);
    var exempt = /^(cover|thanks|agenda|hero|closing)$/.test(kind);
    if (!exempt) {
      if (m.emptyBand > BAND_WARN) issues.push({ kind: 'empty-band', sev: m.emptyBand > BAND_MAX ? 'error' : 'warn', where: root.id, msg: 'content ends at y ' + m.bottom + ', leaving ' + m.emptyBand + 'px empty above the footer (aim for ' + BAND_WARN + ' or less, error over ' + BAND_MAX + '): add substance (proof, a mechanism, a build) or enlarge the visual' });
      if (m.fill < FILL_WARN) issues.push({ kind: 'fill', sev: m.fill < FILL_MIN ? 'error' : 'warn', where: root.id, msg: 'fill ' + m.fill + '% of the content box (aim for ' + FILL_WARN + '% or more, error under ' + FILL_MIN + '%): the slide is thin, add the missing elements from the content standard' });
    }
    /* heading vs detail hierarchy, per card (innermost framed box holding a heading and detail text) */
    var cards = $$('*', root).filter(function (el) {
      if (!visible(el) || el.closest('svg')) return false;
      var cs = getComputedStyle(el), bgc = parseC(cs.backgroundColor);
      var framed = el.classList.contains('glass') || (bgc && bgc.a > 0.03) || (parseFloat(cs.borderTopWidth) > 0 && parseFloat(cs.borderLeftWidth) > 0);
      var r = rel(el); return framed && r.w >= 160 && r.h >= 80 && !el.classList.contains('hl');
    });
    m.hier = [];
    cards.forEach(function (card) {
      var inner = cards.filter(function (c) { return c !== card && card.contains(c); });
      var own = texts.filter(function (el) { return card.contains(el) && !inner.some(function (c) { return c.contains(el); }); });
      var heads = [], body = [];
      own.forEach(function (el) {
        var cs = getComputedStyle(el), t = ownText(el), size = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight, 10);
        if (el.closest('svg, table') || isLabel(el, cs) || isNumeric(t)) return;
        /* not headings: labels inside caps tags, chips and pills (own fill or border), run-in bold inside a sentence */
        var lab = false; for (var q = el.parentElement; q && q !== card; q = q.parentElement) if (isLabel(q, getComputedStyle(q))) { lab = true; break; }
        if (lab) return;
        var words = t.split(/\s+/).length;
        var ebg = parseC(cs.backgroundColor), chip = (ebg && ebg.a > 0.03) || parseFloat(cs.borderTopWidth) > 0 || (el.parentElement && /\b(pills|chips|b-chips)\b/.test(el.parentElement.className || ''));
        var runIn = cs.display === 'inline' && el.parentElement && ownText(el.parentElement).length > 0;
        if (w >= 600 && (chip || runIn)) return;
        if (w >= 600 && !el.closest('p, li')) heads.push({ el: el, size: size, w: w });
        else if (w < 600 && words >= 4) body.push({ el: el, size: size, w: w });
      });
      if (!heads.length || !body.length) return;
      var h = heads.reduce(function (a, b) { return b.size > a.size ? b : a; });
      var d = body.reduce(function (a, b) { return b.size > a.size ? b : a; });
      var ratio = Math.round(100 * h.size / d.size) / 100, dw = h.w - d.w;
      /* card headings: 1.2x the detail and at least 200 heavier; row titles under 26px (lists, tables, lanes): 1.08x and 200 heavier */
      var need = h.size < 26 ? HIER_ROW : HIER_MIN;
      m.hier.push(ratio);
      if (ratio < need || dw < HIER_W) add('hierarchy', h.el, 'heading ' + Math.round(h.size) + 'px/' + h.w + ' vs detail ' + Math.round(d.size) + 'px/' + d.w + ' in the same card: ratio ' + ratio + ', weight +' + dw + '; needs ' + need + 'x and +' + HIER_W + ' weight (raise the heading or lower the detail text)', exempt ? 'warn' : 'error');
    });
    /* hollow panels: a framed panel whose content stops far above its bottom edge (stretched to pass fill) */
    m.hollow = 0;
    cards.forEach(function (card) {
      var cr = rel(card); if (cr.h < 200) return;
      var low = 0, spans = [];
      $$('*', card).forEach(function (el) {
        if (!visible(el)) return;
        var tag = el.tagName.toLowerCase();
        if (el.closest('svg') && tag !== 'svg') return;
        var own = meaningful(el), cs = getComputedStyle(el), bgc = parseC(cs.backgroundColor);
        if (own || tag === 'svg' || tag === 'img' || tag === 'canvas' || (bgc && bgc.a > 0.05) || parseFloat(cs.borderTopWidth) > 0) {
          var rr = own ? textRect(el) : rel(el);
          low = Math.max(low, rr.b);
          if (rr.h < cr.h * 0.9) spans.push([rr.y, rr.b]);
        }
      });
      /* a gap in the middle (text at the top, a button pinned to the bottom) is as hollow as a gap at the bottom */
      spans.sort(function (a, b) { return a[0] - b[0]; });
      var reach = cr.y, midGap = 0;
      spans.forEach(function (s) { if (s[0] > reach) midGap = Math.max(midGap, s[0] - reach); reach = Math.max(reach, s[1]); });
      var bottomGap = cr.b - low, mg = midGap - 24, gap = Math.max(bottomGap, mg);
      var hard = bottomGap >= Math.max(150, 0.5 * cr.h) || mg >= Math.max(150, 0.38 * cr.h);
      var soft = bottomGap > Math.max(110, 0.4 * cr.h) || mg > Math.max(110, 0.3 * cr.h);
      if (low && (soft || hard)) {
        m.hollow++;
        /* error at half the panel empty (the approved roadmap's last quarter column sits at 48%: a warning) */
        add('hollow', card, 'panel ' + Math.round(cr.h) + 'px tall with ' + Math.round(gap) + 'px of it empty (' + (mg > bottomGap ? 'a gap between its content and a pinned button or line' : 'below its content') + '): fill it with substance (an output, a proof line, a number) or let it shrink', (exempt || !hard) ? 'warn' : 'error');
      }
    });
    /* entrance motion: elements with a CSS animation once the slide is on (names survive the frozen QA style) */
    var animated = $$('*', root).filter(function (el) { var n = getComputedStyle(el).animationName; return n && n !== 'none'; });
    m.animated = animated.length;
    m.entrances = animated.filter(function (el) { return /rise|fade|grow|pop|draw|slide|wipe/i.test(getComputedStyle(el).animationName); }).length;
    if (!m.entrances) issues.push({ kind: 'motion', sev: 'error', where: root.id, msg: 'no entrance animation: give the header and every panel class "in" with a staggered --d (or a draw or grow recipe)' });
    else if (m.entrances < 3 && !exempt) issues.push({ kind: 'motion', sev: 'warn', where: root.id, msg: 'only ' + m.entrances + ' elements enter: stagger the panels too, not just the header' });
    /* a hero number (56px or larger) needs a count-up */
    var big = texts.filter(function (el) { var cs = getComputedStyle(el); return parseFloat(cs.fontSize) >= 56 && isNumeric(ownText(el)) && !el.closest('h1, h2'); });
    m.heroNumbers = big.length; m.countUps = $$('[data-count]', root).length;
    if (big.length && !m.countUps && !exempt) add('countup', big[0], 'hero number "' + ownText(big[0]) + '" has no count-up: keep the final figure in the HTML and add data-count (data-pre and data-suf for currency and units)');
    return m;
  }

  function layout() {
    var res = { mode: 'layout', theme: document.documentElement.getAttribute('data-theme'), fonts: {}, interactions: [], views: [] };
    try {
      res.fonts = { manrope: document.fonts.check('700 64px Manrope'), bricolage: document.fonts.check('800 40px "Bricolage Grotesque"'), fraunces: document.fonts.check('italic 400 40px Fraunces') };
    } catch (e) {}
    var G = window.G10X;
    // interactions first, with the deck script live
    if (G) {
      $$('[data-open]').forEach(function (b) {
        var id = b.getAttribute('data-open'), m = document.getElementById(id), ok;
        b.click(); ok = !!(m && !m.hidden);
        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
        var closed = !!(m && m.hidden);
        res.interactions.push({ kind: 'data-open', target: id, from: path(b), opens: ok, closesOnEsc: closed });
      });
      $$('[data-go]').forEach(function (b) {
        var src = b.closest('.slide'), si = slides.indexOf(src);
        G.go(si, 99, true);
        var g = b.getAttribute('data-go'), ti = /^\d+$/.test(g) ? +g - 1 : slides.findIndex(function (x) { return x.id === g; });
        b.click();
        var landed = ti >= 0 && slides[ti].classList.contains('on');
        var back = document.getElementById('back'), shown = back && !back.hidden;
        if (shown) back.click();
        var returned = src.classList.contains('on');
        res.interactions.push({ kind: 'data-go', target: g, from: src.id, lands: landed, backPill: shown, backReturns: returned });
      });
      var wi = $$('.wi-c')[0]; if (wi) { wi.click(); res.interactions.push({ kind: 'flip', ok: wi.classList.contains('open') }); wi.click(); }
      G.go(0, 0, true);
    }
    // layout per slide at its final build
    slides.forEach(function (s) {
      slides.forEach(function (x) { x.classList.remove('on'); });
      s.classList.add('on', 'instant');
      var n = +(s.getAttribute('data-steps') || 0);
      s.setAttribute('data-step', n);
      $$('[data-b]', s).forEach(function (b) { b.classList.add('vis'); });
      var th = s.getAttribute('data-theme'); if (th) document.documentElement.setAttribute('data-theme', th);   // review builds
      stage.classList.toggle('cov', /^(cover|thanks)(-|$)/.test(s.id));
      void s.offsetWidth;
      res.views.push(checkView(s, s.id, false));
    });
    slides.forEach(function (x) { x.classList.remove('on'); });
    mzs.forEach(function (m) {
      m.hidden = false; m.classList.add('show'); void m.offsetWidth;
      res.views.push(checkView(m, m.id, true));
      m.hidden = true; m.classList.remove('show');
    });
    out(res);
  }

  function anim() {
    var res = { mode: 'anim', steps: [] }, G = window.G10X;
    if (!G) { out({ mode: 'anim', error: 'no window.G10X hook' }); return; }
    var plan = [];
    slides.forEach(function (s, i) { var n = +(s.getAttribute('data-steps') || 0); for (var k = 0; k <= n; k++) plan.push([i, k]); });
    var idx = 0;
    function stepOnce() {
      if (idx >= plan.length) { out(res); return; }
      var p = plan[idx++], s = slides[p[0]];
      G.go(p[0], p[1], false);
      setTimeout(function () {
        var list = document.getAnimations ? document.getAnimations() : [];
        var mine = list.filter(function (a) { var t = a.effect && a.effect.target; return t && s.contains(t) && a.playState !== 'idle'; });  /* running or finished-but-applied: virtual time can finish short entrances before the sample */
        var names = {}; mine.forEach(function (a) { names[a.animationName || a.transitionProperty || 'anim'] = 1; });
        var trans = list.filter(function (a) { var t = a.effect && a.effect.target; return t && s.contains(t) && a.transitionProperty; }).length;
        res.steps.push({ slide: s.id, step: p[1], running: mine.length, transitions: trans, names: Object.keys(names).slice(0, 12) });
        stepOnce();
      }, 320);
    }
    stepOnce();
  }

  function start() { if (MODE === 'anim') anim(); else layout(); }
  if (document.readyState === 'complete') setTimeout(start, 50); else addEventListener('load', function () { setTimeout(start, 50); });
})();
