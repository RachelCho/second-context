/* Second Context 언어 전환: 선택한 언어 기억, 전환할 때 보던 위치·펼친 사례·사례 인터랙션 단계와 탭·작성 중인 문의 유지.
   - 첫 방문은 한국어. 브라우저 언어나 접속 국가로 자동 이동하지 않는다.
   - 언어 링크를 누르면 그 언어를 기억하고, 다음에 한국어(기본) 주소로 들어오면 영어 페이지로 이어 준다.
   - 저장은 이 브라우저에만 남는다(localStorage·sessionStorage). 막혀 있으면 기억 없이 그대로 동작한다. */
(function () {
  var KEY = 'sc-lang';
  var STATE = 'sc-lang-switch';
  var html = document.documentElement;
  var cur = html.lang === 'en' ? 'en' : 'ko';

  function get(store, k) { try { return window[store].getItem(k); } catch (e) { return null; } }
  function set(store, k, v) { try { window[store].setItem(k, v); } catch (e) {} }
  function del(store, k) { try { window[store].removeItem(k); } catch (e) {} }
  // 홈은 폴더 주소(/, /en/)로도 열리므로 빈 이름은 index.html로 본다 (운영 도메인 second-context.com)
  function pageName(path) { return path.split('/').pop() || 'index.html'; }

  // 1) 다음 방문: 한국어 기본 주소로 왔는데 영어를 골라 둔 경우에만 영어 페이지로 바꾼다
  // (영어 페이지는 같은 폴더의 en/ 아래 같은 파일 이름. 상대 경로라 로컬 미리보기에서도 같은 서버에 머문다)
  if (cur === 'ko' && get('localStorage', KEY) === 'en') {
    location.replace(location.pathname.replace(/[^\/]*$/, function (n) { return 'en/' + n; }) + location.hash);
    return;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var header = document.querySelector('header');
    var headerBottom = function () { return header ? header.getBoundingClientRect().bottom : 0; };

    // 2) 전환 직전 상태 저장: 보던 영역, 펼친 사례, 작성 중인 문의
    function saveState(target) {
      var spots = Array.prototype.slice.call(document.querySelectorAll('main section[id], main li[id], main form[id], main .step[id], main .contact-way[id]'));
      var top = headerBottom() + 1, anchor = null, ratio = 0;
      spots.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top <= top && r.bottom > top) { anchor = el.id; ratio = r.height ? (top - r.top) / r.height : 0; }
      });
      var fields = {};
      Array.prototype.forEach.call(document.querySelectorAll('#inquiry .field input, #inquiry .field textarea'), function (el) {
        if (el.value) fields[el.id] = el.value;
      });
      var open = Array.prototype.map.call(document.querySelectorAll('details[id][open]'), function (d) { return d.id; });
      var demos = {};
      var counted = Array.prototype.map.call(document.querySelectorAll('[data-countup][data-counted][id]'), function (l) { return l.id; });
      Array.prototype.forEach.call(document.querySelectorAll('[data-demo][id]'), function (d) {
        demos[d.id] = { step: d.getAttribute('data-step'), sel: d.getAttribute('data-sel'), open: d.classList.contains('is-open') };
      });
      var tabs = {};
      Array.prototype.forEach.call(document.querySelectorAll('[data-tabs][id]'), function (b) {
        var t = b.querySelector('[role="tab"][aria-selected="true"]');
        if (t) tabs[b.id] = t.id;
      });
      set('sessionStorage', STATE, JSON.stringify({ page: pageName(location.pathname), target: target, anchor: anchor, ratio: ratio, atTop: window.scrollY < 4, open: open, demos: demos, tabs: tabs, counted: counted, fields: fields }));
    }

    Array.prototype.forEach.call(document.querySelectorAll('nav.lang a[hreflang]'), function (a) {
      a.addEventListener('click', function () {
        set('localStorage', KEY, a.getAttribute('hreflang'));
        if (a.getAttribute('aria-current') !== 'true') saveState(a.getAttribute('hreflang'));
      });
    });

    // 3) 전환 직후 복원: 같은 페이지의 다른 언어로 왔을 때만
    var raw = get('sessionStorage', STATE);
    if (!raw) return;
    del('sessionStorage', STATE);
    var st;
    try { st = JSON.parse(raw); } catch (e) { return; }
    if (!st || st.target !== cur || st.page !== pageName(location.pathname)) return;

    (st.open || []).forEach(function (id) { var d = document.getElementById(id); if (d && d.tagName === 'DETAILS') d.open = true; });
    // 이미 재생한 경력 수치 카운트업은 다시 재생하지 않는다 (count-up.js가 sc:counted를 받아 최종 값 표시)
    (st.counted || []).forEach(function (id) {
      var l = document.getElementById(id);
      if (l) l.dispatchEvent(new CustomEvent('sc:counted'));
    });
    // 사례 인터랙션의 단계·선택한 항목·펼친 기록 (case-demo.js가 sc:step 이벤트를 받아 바꾼다)
    Object.keys(st.demos || {}).forEach(function (id) {
      var d = document.getElementById(id);
      if (d) d.dispatchEvent(new CustomEvent('sc:step', { detail: st.demos[id] }));
    });
    // 사례 데모 탭 (case-demo.js가 sc:tab 이벤트를 받아 바꾼다)
    Object.keys(st.tabs || {}).forEach(function (id) {
      var b = document.getElementById(id);
      if (b) b.dispatchEvent(new CustomEvent('sc:tab', { detail: st.tabs[id] }));
    });
    Object.keys(st.fields || {}).forEach(function (id) {
      var el = document.getElementById(id);
      if (el && !el.value) el.value = st.fields[id];
    });
    if (location.hash || st.atTop || !st.anchor) return;
    var el = document.getElementById(st.anchor);
    if (!el) return;
    var prev = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    var r = el.getBoundingClientRect();
    window.scrollTo(0, window.scrollY + r.top + r.height * st.ratio - headerBottom() - 1);
    html.style.scrollBehavior = prev;
  });
})();
