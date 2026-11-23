/* Layout and contrast probe for a Growth10x plan page. render_page.py injects this into a QA copy of the
   page (never into the page itself). It writes its findings as JSON into <pre id="qa-out">, which the
   renderer reads from Chrome's --dump-dom output. */
(function(){
  'use strict';
  function parse(c){
    var m = /rgba?\(([^)]+)\)/.exec(c || ''); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat);
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  }
  function over(top, base){ var a = top.a; return {r: top.r * a + base.r * (1 - a), g: top.g * a + base.g * (1 - a), b: top.b * a + base.b * (1 - a), a: 1}; }
  function lum(c){ function ch(v){ v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); } return 0.2126 * ch(c.r) + 0.7152 * ch(c.g) + 0.0722 * ch(c.b); }
  function ratio(a, b){ var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function where(el){
    var s = el.closest('section[id],header[id],footer,.tb'), id = s ? (s.id || s.className.split(' ')[0]) : 'page';
    var cls = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 3).join('.');
    return id + ' > ' + el.tagName.toLowerCase() + (cls ? '.' + cls : '');
  }
  function snippet(el){ return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70); }
  function ownText(el){ for (var n = el.firstChild; n; n = n.nextSibling) if (n.nodeType === 3 && n.nodeValue.trim()) return true; return false; }
  function skip(el){ return el.closest('#qa-out,script,style,canvas,svg,[aria-hidden="true"]'); }
  function bgOf(el){
    var layers = [], op = 1;
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) {
      var cs = getComputedStyle(e); op *= parseFloat(cs.opacity) || 1;
      var bi = cs.backgroundImage;
      if (bi && bi.indexOf('linear-gradient(') === 0 && cs.backgroundSize.indexOf('0%') !== 0) {
        var g = parse(bi); if (g && g.a > 0) { layers.push(g); if (g.a >= 1) break; }
      }
      var c = parse(cs.backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    var base = parse(getComputedStyle(document.body).backgroundColor) || {r: 23, g: 22, b: 29, a: 1};
    var col = base; for (var i = layers.length - 1; i >= 0; i--) col = over(layers[i], col);
    return {bg: col, op: op};
  }
  function run(){
    var R = {width: innerWidth, height: Math.ceil(Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)),
             theme: document.documentElement.getAttribute('data-theme'), errors: [], warnings: [], info: {}};
    var vw = document.documentElement.clientWidth;
    if (document.documentElement.scrollWidth > vw + 1) R.errors.push({rule: 'page-scrolls-sideways', where: 'page', detail: 'content is ' + document.documentElement.scrollWidth + 'px wide in a ' + vw + 'px window'});
    var scrollers = [];
    var all = [].slice.call(document.body.querySelectorAll('*')), contrastFails = 0, checked = 0;
    all.forEach(function(el){
      if (skip(el)) return;
      var cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
      var r = el.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
      var sx = cs.overflowX;
      if ((sx === 'auto' || sx === 'scroll') && el.scrollWidth > el.clientWidth + 1) { scrollers.push(el); R.warnings.push({rule: 'scrolls-inside', where: where(el), detail: 'scrolls sideways inside its box (' + el.scrollWidth + ' in ' + el.clientWidth + 'px). Fine for wide tables on phones, not on desktop.'}); }
      var inScroller = scrollers.some(function(s){ return s !== el && s.contains(el); });
      if (!inScroller && r.right > vw + 1 && cs.position !== 'fixed') R.errors.push({rule: 'off-page', where: where(el), detail: 'right edge at ' + Math.round(r.right) + 'px, window ' + vw + 'px', text: snippet(el)});
      var txt = ownText(el);
      if (txt && cs.display !== 'inline' && !inScroller) {
        var clipX = el.scrollWidth > el.clientWidth + 2, clipY = el.scrollHeight > el.clientHeight + 3;
        var hidden = /hidden|clip/.test(cs.overflowX + cs.overflowY);
        if (hidden && (clipX || clipY) && cs.textOverflow !== 'ellipsis') R.errors.push({rule: 'clipped-text', where: where(el), detail: 'text cut off by its box', text: snippet(el)});
        else if (!hidden && clipX && cs.whiteSpace !== 'nowrap') R.errors.push({rule: 'text-overflow', where: where(el), detail: 'text wider than its box by ' + (el.scrollWidth - el.clientWidth) + 'px', text: snippet(el)});
        else if (!hidden && clipX) R.warnings.push({rule: 'nowrap-overflow', where: where(el), detail: 'unwrapped text sticks out of its box', text: snippet(el)});
        if (cs.textOverflow === 'ellipsis' && clipX) R.warnings.push({rule: 'truncated', where: where(el), detail: 'text shortened with an ellipsis', text: snippet(el)});
      }
      if (txt) {
        var fg = parse(cs.color); if (!fg) return; checked++;
        var b = bgOf(el), col = over({r: fg.r, g: fg.g, b: fg.b, a: fg.a * b.op}, b.bg), cr = ratio(col, b.bg);
        var size = parseFloat(cs.fontSize), wt = parseInt(cs.fontWeight, 10) || 400, big = size >= 24 || (size >= 18.66 && wt >= 700);
        var need = big ? 3 : 4.5;
        if (cr < need) { contrastFails++; if (contrastFails <= 40) R.errors.push({rule: 'contrast', where: where(el), detail: cr.toFixed(2) + ':1, needs ' + need + ':1 (' + Math.round(size) + 'px ' + wt + ')', text: snippet(el)}); }
      }
    });
    R.info.text_elements_checked = checked; R.info.contrast_failures = contrastFails;
    [].slice.call(document.images).forEach(function(im){ if (!im.complete || !im.naturalWidth) R.errors.push({rule: 'broken-image', where: where(im), detail: im.getAttribute('src').slice(0, 80)}); });
    try { R.info.manrope_loaded = document.fonts.check('16px Manrope'); if (!R.info.manrope_loaded) R.warnings.push({rule: 'font', where: 'page', detail: 'Manrope did not load (no network?). Screenshots show the fallback font.'}); } catch (e) {}
    var secs = [].slice.call(document.querySelectorAll('section.sc'));
    R.info.sections = secs.map(function(s){ return s.id; });
    secs.forEach(function(s){ if (!s.querySelector('.rv')) R.warnings.push({rule: 'no-entrance', where: s.id, detail: 'section has no .rv element, so nothing animates in'}); });
    var pre = document.createElement('pre'); pre.id = 'qa-out'; pre.hidden = true; pre.textContent = JSON.stringify(R);
    document.body.appendChild(pre);
    var qy = +(document.documentElement.getAttribute('data-qy') || 0);
    if (qy) { document.body.style.transform = 'translateY(-' + qy + 'px)'; }
  }
  function go(){ setTimeout(run, 250); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(go); else addEventListener('load', go);
})();
