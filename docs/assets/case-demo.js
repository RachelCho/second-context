/* Second Context 사례 인터랙션: 단계 버튼, 모션 재생·정지·다시 보기.
   - 사례마다 상태를 따로 가진다 (한 사례의 단계·선택이 다른 사례에 영향을 주지 않음)
   - 재생은 사용자가 눌렀을 때만 시작하고, 마지막 단계에서 한 번 멈춘다. 한 데모를 재생하면 다른 데모의 재생은 멈춘다
   - 화면 요소: data-show="2 3"(그 단계에서만 보임), data-hl="1"(그 단계에서 강조), data-pick="2"(그 단계에서 선택됨),
     data-on="2 3"(그 단계에서 is-on), data-pos="3 1 1"(단계별 목록 순서 — 순서를 바꿀 때만 한 번 움직인다)
   - 선택 목록: data-select="a" 버튼을 누르면 마지막 단계로 가서 data-detail="a" 내용을 보여 준다
   - 펼침: data-expand 버튼이 aria-controls 영역을 펼친다 (단계를 바꾸면 접힘)
   - 탭(data-tabs): 데모 여러 개 중 하나만 보인다. 탭을 바꾸면 재생 중인 데모는 멈춘다
   - 언어 전환 뒤 단계·선택·펼침을 되살릴 때는 lang.js가 'sc:step', 고른 탭은 'sc:tab' 이벤트를 보낸다 */
(function () {
  var STEP_MS = 2600;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  var halts = [];

  function has(attr, n) { return (' ' + (attr || '') + ' ').indexOf(' ' + n + ' ') !== -1; }
  function all(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }

  all(document, '[data-demo]').forEach(function (demo) {
    var steps = all(demo, '.demo-step');
    var total = steps.length;
    var play = demo.querySelector('[data-play]');
    var stop = demo.querySelector('[data-stop]');
    var replay = demo.querySelector('[data-replay]');
    var expand = demo.querySelector('[data-expand]');
    var timer = null;

    // 목록 순서를 단계에 맞춘다. DOM 순서를 바꿔 화면과 읽는 순서를 같게 두고, 움직임은 바뀔 때 한 번만
    function arrange(n) {
      var items = all(demo, '[data-pos]');
      if (!items.length) return;
      var list = items[0].parentNode;
      var pos = function (el) { return +(el.getAttribute('data-pos').split(' ')[n - 1] || 0); };
      var sorted = items.slice().sort(function (a, b) { return pos(a) - pos(b); });
      if (sorted.every(function (el, i) { return list.children[i] === el; })) return;
      var before = items.map(function (el) { return el.getBoundingClientRect().top; });
      var focused = document.activeElement;
      sorted.forEach(function (el) { list.appendChild(el); });
      if (focused && list.contains(focused)) focused.focus({ preventScroll: true });
      if (reduce && reduce.matches) return;
      items.forEach(function (el, i) {
        var dy = before[i] - el.getBoundingClientRect().top;
        if (!dy || !el.animate) return;
        el.animate([{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }], { duration: 450, easing: 'cubic-bezier(.2,.7,.2,1)' });
      });
    }

    function setOpen(open) {
      if (!expand) return;
      var region = document.getElementById(expand.getAttribute('aria-controls'));
      expand.setAttribute('aria-expanded', String(open));
      if (region) region.hidden = !open;
      demo.classList.toggle('is-open', open);
    }

    function setStep(n) {
      n = Math.max(1, Math.min(total, n));
      if (n !== current()) setOpen(false);
      demo.setAttribute('data-step', String(n));
      steps.forEach(function (b) {
        if (+b.getAttribute('data-go') === n) b.setAttribute('aria-current', 'step');
        else b.removeAttribute('aria-current');
      });
      all(demo, '[data-show]').forEach(function (el) { el.hidden = !has(el.getAttribute('data-show'), n); });
      all(demo, '[data-hl]').forEach(function (el) { el.classList.toggle('is-hl', has(el.getAttribute('data-hl'), n)); });
      all(demo, '[data-pick]').forEach(function (el) { el.classList.toggle('is-pick', has(el.getAttribute('data-pick'), n)); });
      all(demo, '[data-rec]').forEach(function (el) { el.classList.toggle('is-rec', has(el.getAttribute('data-rec'), n)); });
      all(demo, '[data-on]').forEach(function (el) { el.classList.toggle('is-on', has(el.getAttribute('data-on'), n)); });
      all(demo, '[data-note]').forEach(function (el) { el.hidden = +el.getAttribute('data-note') !== n; });
      arrange(n);
      showSelection();
    }

    // 선택한 항목과 상세 내용은 마지막 단계에서만 보인다
    function showSelection() {
      var sel = demo.getAttribute('data-sel');
      var on = current() === total;
      all(demo, '[data-select]').forEach(function (b) {
        var me = on && b.getAttribute('data-select') === sel;
        b.classList.toggle('is-sel', me);
        if (me) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
      });
      all(demo, '[data-detail]').forEach(function (el) { el.hidden = !(on && el.getAttribute('data-detail') === sel); });
    }

    function current() { return +demo.getAttribute('data-step') || 1; }

    function halt() {
      if (timer) { clearTimeout(timer); timer = null; }
      demo.classList.remove('is-playing');
      play.disabled = false;
      stop.disabled = true;
    }
    halts.push(halt);

    function tick() {
      if (current() >= total) { halt(); return; }
      setStep(current() + 1);
      timer = setTimeout(tick, STEP_MS);
    }

    function start(from) {
      halts.forEach(function (h) { h(); });
      if (from) setStep(from);
      else if (current() >= total) setStep(1);
      demo.classList.add('is-playing');
      play.disabled = true;
      stop.disabled = false;
      stop.focus();
      timer = setTimeout(tick, STEP_MS);
    }

    steps.forEach(function (b) {
      b.addEventListener('click', function () { halt(); setStep(+b.getAttribute('data-go')); });
    });
    // 목록 항목을 직접 누르면 시연을 멈추고 그 항목의 상세 내용을 연다
    all(demo, '[data-select]').forEach(function (b) {
      b.addEventListener('click', function () {
        halt();
        demo.setAttribute('data-sel', b.getAttribute('data-select'));
        if (current() !== total) setStep(total); else showSelection();
      });
    });
    if (expand) expand.addEventListener('click', function () {
      halt();
      setOpen(expand.getAttribute('aria-expanded') !== 'true');
    });
    // 단계 버튼은 좌우 화살표로도 이동한다
    demo.querySelector('.demo-steps').addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var i = steps.indexOf(document.activeElement);
      if (i === -1) return;
      e.preventDefault();
      var next = steps[(i + (e.key === 'ArrowRight' ? 1 : total - 1)) % total];
      next.focus();
      next.click();
    });
    play.addEventListener('click', function () { start(); });
    stop.addEventListener('click', function () { halt(); play.focus(); });
    replay.addEventListener('click', function () { start(1); });
    demo.addEventListener('sc:step', function (e) {
      var d = e.detail;
      halt();
      if (d && typeof d === 'object') {
        if (d.sel) demo.setAttribute('data-sel', d.sel);
        setStep(+d.step || 1);
        if (d.open) setOpen(true);
      } else setStep(+d || 1);
    });

    setStep(current());
  });

  // 데모 탭: 좌우 화살표·Home·End로 이동하며 바로 전환한다
  all(document, '[data-tabs]').forEach(function (box) {
    var tabs = all(box, '[role="tab"]');
    function select(tab, focus) {
      halts.forEach(function (h) { h(); });
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var j = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
        if (j === undefined) return;
        e.preventDefault();
        select(tabs[(j + tabs.length) % tabs.length], true);
      });
    });
    box.addEventListener('sc:tab', function (e) {
      var t = document.getElementById(e.detail);
      if (t && tabs.indexOf(t) !== -1) select(t);
    });
  });
})();
