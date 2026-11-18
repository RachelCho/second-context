/* 서비스·가격 상세 슬라이더(2026-11-18). 네 상품 패널을 가로 스크롤(scroll-snap)로 넘기고,
   번호 버튼·이전/다음·진행 막대로 현재 위치를 보여 준다. 스크롤 위치에 따라 가운데 패널을 강조(.is-active).
   JS 없음: 버튼 없이 가로 스크롤만 된다. 움직임 줄이기: 부드러운 스크롤·확대 전환 없이 바로 이동.
   #consult·#review·#sprint·#project 주소(다른 페이지 링크, 요약 카드)는 해당 패널로 연다 */
(function () {
  var track = document.querySelector('[data-slider]');
  var nav = document.querySelector('[data-slider-nav]');
  if (!track || !nav) return;
  var panels = Array.prototype.slice.call(track.querySelectorAll('.pr-panel'));
  var tabs = Array.prototype.slice.call(nav.querySelectorAll('[data-go]'));
  var prev = nav.querySelector('[data-prev]');
  var next = nav.querySelector('[data-next]');
  var bar = nav.querySelector('.pr-progress span');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = -1;

  document.documentElement.classList.add('js-slider');
  nav.hidden = false;

  function offsetOf(i) { return panels[i].offsetLeft - panels[0].offsetLeft; }

  function setActive(i) {
    if (i === current) return;
    current = i;
    panels.forEach(function (p, k) { p.classList.toggle('is-active', k === i); });
    tabs.forEach(function (t, k) {
      if (k === i) t.setAttribute('aria-current', 'true');
      else t.removeAttribute('aria-current');
    });
    prev.disabled = i === 0;
    next.disabled = i === panels.length - 1;
  }

  // 스크롤 위치에서 가장 가까운 패널(끝까지 넘기면 마지막 패널)
  function sync() {
    var max = track.scrollWidth - track.clientWidth;
    var x = track.scrollLeft;
    if (bar) bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, x / max) : 1) + ')';
    if (max > 0 && x >= max - 2) { setActive(panels.length - 1); return; }
    var best = 0;
    panels.forEach(function (p, k) {
      if (Math.abs(offsetOf(k) - x) < Math.abs(offsetOf(best) - x)) best = k;
    });
    setActive(best);
  }

  function go(i, instant) {
    i = Math.max(0, Math.min(panels.length - 1, i));
    track.scrollTo({ left: offsetOf(i), behavior: reduce || instant ? 'auto' : 'smooth' });
    setActive(i);
  }

  var ticking = false;
  track.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { ticking = false; sync(); });
  }, { passive: true });
  window.addEventListener('resize', function () { if (current >= 0) go(current, true); });

  tabs.forEach(function (t, k) { t.addEventListener('click', function () { go(k); }); });
  prev.addEventListener('click', function () { go(current - 1); });
  next.addEventListener('click', function () { go(current + 1); });

  // 키보드로 다른 패널 안의 링크에 들어가면 그 패널로 맞춘다
  track.addEventListener('focusin', function (e) {
    var p = e.target.closest && e.target.closest('.pr-panel');
    var k = panels.indexOf(p);
    if (k >= 0 && k !== current) go(k, true);
  });

  // 주소의 #상품 id로 열기: 슬라이더 영역으로 내려가고 해당 패널을 연다
  function openHash(smooth) {
    var id = decodeURIComponent((location.hash || '').slice(1));
    var k = panels.map(function (p) { return p.id; }).indexOf(id);
    if (k < 0) return false;
    var section = track.closest('section');
    section.scrollIntoView({ behavior: smooth && !reduce ? 'smooth' : 'auto', block: 'start' });
    go(k, !smooth);
    return true;
  }
  Array.prototype.forEach.call(document.querySelectorAll('a[href^="#"]'), function (a) {
    var id = a.getAttribute('href').slice(1);
    if (!panels.some(function (p) { return p.id === id; })) return;
    a.addEventListener('click', function (e) {
      e.preventDefault();
      if (history.replaceState) history.replaceState(null, '', '#' + id);
      openHash(true);
    });
  });
  window.addEventListener('hashchange', function () { openHash(true); });

  if (!openHash(false)) setActive(0);
  sync();
})();
