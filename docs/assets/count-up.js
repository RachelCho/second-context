/* Second Context 경력 수치 카운트업.
   - HTML에는 처음부터 최종 값이 들어 있다. 이 스크립트가 없거나 실패해도 40+ · 12+ · 27이 그대로 보인다
   - 숫자 영역이 화면에 충분히 들어오면(60%) 세 숫자를 동시에 0 → 최종 값으로 약 900ms 동안 올린다 (끝으로 갈수록 느려짐)
   - 한 번의 페이지 방문에서 처음 한 번만. 다시 스크롤해도 반복하지 않는다
   - 언어를 바꿔 들어온 페이지에서는 lang.js가 'sc:counted' 이벤트를 보내 다시 재생하지 않는다
   - 움직임 줄이기 설정, IntersectionObserver 미지원이면 최종 값을 그대로 둔다
   - 화면에 보이는 숫자는 aria-hidden이고, 스크린리더는 옆의 sr-only 최종 값만 읽는다 (aria-live 없음) */
(function () {
  var DURATION = 900;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window) || !window.requestAnimationFrame) return;

  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

  Array.prototype.forEach.call(document.querySelectorAll('[data-countup]'), function (list) {
    var nums = Array.prototype.slice.call(list.querySelectorAll('.stat-num[data-count]'));
    if (!nums.length) return;
    var frame = null;
    var safety = null; // 탭이 가려져 프레임이 멈춰도 최종 값으로 끝내기 위한 예비 타이머

    // 최종 값 자릿수만큼 자리를 잡아 두어 카운트 중에 폭이 흔들리지 않게 한다
    nums.forEach(function (el) {
      el.style.minWidth = String(el.getAttribute('data-count')).length + 'ch';
    });

    function finish() {
      if (frame) { cancelAnimationFrame(frame); frame = null; }
      if (safety) { clearTimeout(safety); safety = null; }
      nums.forEach(function (el) { el.textContent = el.getAttribute('data-count'); });
      list.setAttribute('data-counted', '');
    }

    var observer = new IntersectionObserver(function (entries) {
      if (!entries.some(function (e) { return e.isIntersecting; })) return;
      observer.disconnect();
      list.setAttribute('data-counted', '');
      var start = null;
      function step(now) {
        if (start === null) start = now;
        var t = Math.min(1, (now - start) / DURATION);
        var k = easeOut(t);
        nums.forEach(function (el) { el.textContent = String(Math.round(+el.getAttribute('data-count') * k)); });
        if (t < 1) frame = requestAnimationFrame(step);
        else finish();
      }
      frame = requestAnimationFrame(step);
      safety = setTimeout(finish, DURATION + 300);
    }, { threshold: 0.6 });

    // 화면에 들어오기 전에는 0에서 기다린다 (스크립트가 동작할 때만)
    nums.forEach(function (el) { el.textContent = '0'; });
    observer.observe(list);

    list.addEventListener('sc:counted', function () { observer.disconnect(); finish(); });
  });
})();
