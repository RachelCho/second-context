/* Second Context 공통 동작 (2026-11-10 다크 리디자인)
   1) 사이트 검색: 헤더 검색 버튼 → 검은 검색 오버레이. 실제 페이지·사례만 찾는다(아래 INDEX). Esc·닫기 버튼으로 닫고 검색 버튼으로 초점을 돌려준다
   2) 푸터 "Let’s" 회전 단어: edenspiekermann.com 푸터와 같은 전환(오른쪽 20px에서 들어오며 나타남, 0.3초 ease-out).
      단어가 바뀌는 간격은 원본에서 확인되지 않아 data-interval(기본 2400ms)로 조정한다. 일시정지/재생 버튼, 움직임 줄이기 설정에서는 멈춘 상태
   3) 뉴스레터: 이메일 형식 검사. form의 data-endpoint가 비어 있으면 구독 서비스가 연결되지 않았다고 알리고 등록된 척하지 않는다.
      주소를 넣으면 JSON으로 보내고 서버 2xx 뒤에만 완료를 알린다
   4) Hero 영상: 무음 반복 재생(900px 이하는 작은 파일, 포스터는 영상 첫 프레임). 파일 오류면 포스터 그대로. 움직임 줄이기 설정이면 재생하지 않는다 */
(function () {
  var html = document.documentElement;
  var lang = html.lang === 'en' ? 'en' : 'ko';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var T = {
    ko: {
      hint: '사례, 서비스, 페이지 이름으로 찾아보세요.',
      found: function (n, q) { return '‘' + q + '’ 검색 결과 ' + n + '개'; },
      empty: function (q) { return '‘' + q + '’에 맞는 결과가 없습니다. 다른 단어로 찾거나 문의 페이지로 알려 주세요.'; },
      pause: '일시정지', play: '재생',
      nlInvalid: '이메일 주소 형식을 확인해 주세요. 예: name@company.com',
      nlEmpty: '이메일 주소를 입력해 주세요.',
      nlOff: '아직 뉴스레터 구독 서비스가 연결되지 않아 등록되지 않았습니다. 소식을 받고 싶으시면 문의 페이지로 알려 주세요.',
      nlSending: '등록하는 중…',
      nlOk: '구독 신청이 접수되었습니다.',
      nlFail: '등록하지 못했습니다. 잠시 후 다시 시도해 주세요.'
    },
    en: {
      hint: 'Search by case study, service, or page name.',
      found: function (n, q) { return n + (n === 1 ? ' result' : ' results') + ' for “' + q + '”'; },
      empty: function (q) { return 'No results for “' + q + '”. Try another word, or tell us on the contact page.'; },
      pause: 'Pause', play: 'Play',
      nlInvalid: 'Please check the email format. Example: name@company.com',
      nlEmpty: 'Please enter your email address.',
      nlOff: 'The newsletter service isn’t connected yet, so you haven’t been subscribed. To hear from us, please get in touch via the contact page.',
      nlSending: 'Subscribing…',
      nlOk: 'Thank you. Your subscription has been received.',
      nlFail: 'We couldn’t subscribe you. Please try again in a moment.'
    }
  }[lang];

  // 검색 대상: 실제로 있는 페이지와 사례만. 주소는 같은 언어 폴더 기준 상대 경로
  var INDEX = {
    ko: [
      { t: '홈', u: './', d: '새로운 시장의 맥락을, 제품의 다음 단계로. 사용자와 업무 환경의 차이를 이해하고 제품 경험과 실행 우선순위를 함께 설계합니다.', k: 'home 메인' },
      { t: '선택 이유 (Why Us)', u: './#why-us', d: '제품과 사람, 비즈니스를 함께 이해합니다. 차별점, 창업자 소개, 경험한 제품과 맡은 역할.', k: 'why us 차별점 창업자 founder 경력 수치 about' },
      { t: '서비스 (Services)', u: './#services', d: '제품 전략, UX 리서치, 프로덕트 디자인, AI 기반 프로토타이핑.', k: 'services 서비스 전략 리서치 디자인 ai 프로토타입' },
      { t: '01 Healthcare — Clinician Scheduling', u: 'second-context-work.html#case-healthcare', d: '미국 홈헬스케어 SaaS의 일정 관리 UX. 복잡한 자격 조건·일정 규칙·예외를 이해하고 바로 행동할 수 있게 설계했습니다.', k: '헬스케어 일정 임상의 달력 AI 추천 디자인 시스템 사례 프로젝트 work' },
      { t: '02 Enterprise — Incident Management', u: 'second-context-work.html#case-monitoring', d: '글로벌 제약사의 운영 모니터링·인시던트 관리 UX. 심각도·영향 범위·조사 우선순위를 연결했습니다.', k: '엔터프라이즈 모니터링 인시던트 대시보드 우선순위 AI 요약 사례 프로젝트 work' },
      { t: '03 Localization — Korean Product Localization', u: 'second-context-work.html#case-localization', d: '글로벌 테크 기업의 한국어 제품 현지화. 언어와 사용 맥락에 맞춰 제품 경험을 조정했습니다.', k: '현지화 한국어 번역 날짜 이름 타이포그래피 사례 프로젝트 work' },
      { t: '진행 방식 (Approach)', u: './#approach', d: '맥락 이해 → 문제 정의 → 디자인 및 검증 → 실행 지원.', k: 'approach 진행 방식 프로세스 단계' },
      { t: '진행 방식 자세히 보기', u: 'second-context-approach.html', d: '진단부터 설계, 개발 협업까지 여섯 단계로 함께 일하는 방식.', k: 'approach 프로세스 우선순위 매트릭스' },
      { t: 'About Second Context', u: 'second-context-about.html', d: '헬스케어 제품, 엔터프라이즈 소프트웨어, 복잡한 업무 흐름을 설계해 온 경력과 멘토링 활동.', k: '소개 창업자 founder 경력 멘토링 about rachel' },
      { t: '문의 (Contact)', u: './#contact', d: '프로젝트 문의 폼, 30분 상담 예약, 이메일 연락.', k: 'contact 문의 폼 상담 예약 이메일 calendly' }
    ],
    en: [
      { t: 'Home', u: './', d: 'New market context, your product’s next step. We understand how your users and their work environments differ, then design the product experience and execution priorities with your team.', k: 'home main' },
      { t: 'Why Us', u: './#why-us', d: 'We understand products, people, and business together. What sets us apart, the founder, and products and roles.', k: 'why us difference founder career figures about' },
      { t: 'Services', u: './#services', d: 'Product strategy, UX research, product design, and AI-assisted prototyping.', k: 'services strategy research design ai prototype prototyping' },
      { t: '01 Healthcare — Clinician Scheduling', u: 'second-context-work.html#case-healthcare', d: 'Scheduling UX for a U.S. home healthcare SaaS. Complex eligibility, scheduling rules, and exceptions turned into clear next actions.', k: 'healthcare scheduling clinician calendar ai recommendation design system case study work project' },
      { t: '02 Enterprise — Incident Management', u: 'second-context-work.html#case-monitoring', d: 'Operations monitoring and incident management UX for a global pharmaceutical company. Severity, impact, and investigation priority connected.', k: 'enterprise monitoring incident dashboard triage priority ai summary case study work project' },
      { t: '03 Localization — Korean Product Localization', u: 'second-context-work.html#case-localization', d: 'Korean product localization for a global tech company. The product experience adapted to language and context of use.', k: 'localization korean translation date name typography case study work project' },
      { t: 'Approach', u: './#approach', d: 'Understand context → Define the problem → Design and validate → Support delivery.', k: 'approach process steps' },
      { t: 'More about our approach', u: 'second-context-approach.html', d: 'Six steps from diagnosis to design and development collaboration.', k: 'approach process priorities matrix' },
      { t: 'About Second Context', u: 'second-context-about.html', d: 'Experience designing healthcare products, enterprise software, and complex workflows, plus mentoring.', k: 'about founder career mentoring rachel' },
      { t: 'Contact', u: './#contact', d: 'Project inquiry form, 30-minute consultation booking, and email.', k: 'contact inquiry form call booking email calendly' }
    ]
  }[lang];

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  document.addEventListener('DOMContentLoaded', function () {
    /* ---------- 0) 헤더: 고정 헤더 높이만큼 앵커 위치 보정 · 모바일 메뉴 패널 · 현재 섹션 표시 · 연도 ---------- */
    var header = document.querySelector('.site-header');
    var setOffset = function () {
      if (header) html.style.scrollPaddingTop = (header.offsetHeight + 16) + 'px';
    };
    setOffset();
    window.addEventListener('resize', setOffset);
    // 처음부터 #섹션 주소로 들어오면 보정한 위치로 다시 맞춘다
    if (location.hash && document.getElementById(location.hash.slice(1))) {
      window.addEventListener('load', function () { document.getElementById(location.hash.slice(1)).scrollIntoView(); });
    }

    var menuBtn = document.querySelector('.menu-toggle');
    var nav = document.getElementById('main-nav');
    if (menuBtn && nav) {
      var menuText = menuBtn.querySelector('.menu-toggle-text');
      var labels = ['Menu', 'Close']; // 메뉴는 두 언어 모두 영어
      var setMenu = function (open, restore) {
        header.classList.toggle('is-open', open);
        menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        menuText.textContent = labels[open ? 1 : 0];
        setOffset();
        if (!open && restore) menuBtn.focus();
      };
      menuBtn.addEventListener('click', function () { setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'); });
      nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && header.classList.contains('is-open')) setMenu(false, true);
      });
      window.matchMedia(document.documentElement.lang === 'en' ? '(min-width: 1240px)' : '(min-width: 1120px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
    }

    // 홈에서는 화면에 보이는 섹션의 메뉴를 현재 위치로 표시한다(하위 페이지는 HTML에 고정)
    var navLinks = Array.prototype.slice.call(document.querySelectorAll('.main-nav a[data-nav]'));
    var tracked = navLinks.map(function (a) { return document.getElementById(a.getAttribute('data-nav')); }).filter(Boolean);
    if (tracked.length && 'IntersectionObserver' in window && navLinks[0].getAttribute('href').charAt(0) === '#') {
      var mark = function (id) {
        navLinks.forEach(function (a) {
          if (a.getAttribute('data-nav') === id) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      };
      var visible = {};
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
        var cur = null;
        tracked.forEach(function (sec) { if (visible[sec.id]) cur = cur || sec.id; });
        mark(cur);
      }, { rootMargin: '-35% 0px -60% 0px' });
      tracked.forEach(function (sec) { io.observe(sec); });
    }

    Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (y) { y.textContent = new Date().getFullYear(); });

    // 홈 Approach 4단계(2026-11-11): 화면에 들어오면 01→04 번호·연결선을 한 번 순서대로 강조한다.
    // HTML·CSS 기본은 완성된 상태라 JS가 없거나 움직임 줄이기면 그대로 보인다. 시작 상태(ready)는 1024px 이상에서만 CSS가 적용
    var flow = document.querySelector('#approach .flow-steps');
    if (flow && !reduce && 'IntersectionObserver' in window) {
      flow.setAttribute('data-flow', 'ready');
      var flowIo = new IntersectionObserver(function (entries) {
        var en = entries[0];
        if (!en.isIntersecting) {
          // 이미 지나친 위치(예: #contact로 바로 열기)면 재생 없이 완성 상태로 둔다
          if (en.boundingClientRect.bottom < 0) { flow.removeAttribute('data-flow'); flowIo.disconnect(); }
          return;
        }
        flow.setAttribute('data-flow', 'play');
        flowIo.disconnect();
      }, { rootMargin: '0px 0px -20% 0px' });
      flowIo.observe(flow);
    }

    /* ---------- 1) 검색 ---------- */
    var openBtn = document.querySelector('.search-open');
    var dlg = document.getElementById('search');
    if (openBtn && dlg) {
      var input = dlg.querySelector('#search-input');
      var list = dlg.querySelector('.search-results');
      var status = dlg.querySelector('.search-status');
      var closeBtn = dlg.querySelector('.search-close');

      var render = function () {
        var q = input.value.trim();
        list.textContent = '';
        if (!q) { status.textContent = T.hint; return; }
        var terms = q.toLowerCase().split(/\s+/);
        var hits = INDEX.filter(function (p) {
          var hay = (p.t + ' ' + p.d + ' ' + p.k).toLowerCase();
          return terms.every(function (w) { return hay.indexOf(w) !== -1; });
        });
        status.textContent = hits.length ? T.found(hits.length, q) : T.empty(q);
        hits.forEach(function (p) {
          var li = el('li'), a = el('a', 'search-hit');
          a.href = p.u;
          a.appendChild(el('span', 'search-hit-title', p.t));
          a.appendChild(el('span', 'search-hit-desc', p.d));
          a.addEventListener('click', function () { close(false); });
          li.appendChild(a); list.appendChild(li);
        });
      };
      var focusables = function () {
        return Array.prototype.filter.call(dlg.querySelectorAll('a[href], button, input'), function (x) { return x.offsetParent !== null; });
      };
      var onKey = function (e) {
        if (e.key === 'Escape') { e.preventDefault(); close(true); return; }
        if (e.key !== 'Tab') return;
        var f = focusables(); if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      };
      var open = function () {
        dlg.hidden = false;
        html.classList.add('search-on');
        openBtn.setAttribute('aria-expanded', 'true');
        document.addEventListener('keydown', onKey);
        render();
        input.focus();
      };
      var close = function (restore) {
        dlg.hidden = true;
        html.classList.remove('search-on');
        openBtn.setAttribute('aria-expanded', 'false');
        document.removeEventListener('keydown', onKey);
        if (restore) openBtn.focus();
      };
      openBtn.addEventListener('click', open);
      closeBtn.addEventListener('click', function () { close(true); });
      input.addEventListener('input', render);
      dlg.querySelector('form').addEventListener('submit', function (e) {
        e.preventDefault();
        var first = list.querySelector('a');
        if (first) first.focus();
      });
    }

    /* ---------- 2) 푸터 회전 단어 ---------- */
    var rot = document.querySelector('[data-rotator]');
    if (rot) {
      var words = (rot.getAttribute('data-words') || '').split('|');
      var word = rot.querySelector('.lets-word');
      var toggle = document.querySelector('.lets-toggle');
      var interval = parseInt(rot.getAttribute('data-interval'), 10) || 2400;
      var i = 0, timer = null;
      var tick = function () {
        i = (i + 1) % words.length;
        word.textContent = words[i];
        word.classList.remove('is-in'); void word.offsetWidth; word.classList.add('is-in');
      };
      var setPlaying = function (on) {
        if (timer) { clearInterval(timer); timer = null; }
        if (on) timer = setInterval(tick, interval);
        if (toggle) {
          toggle.setAttribute('aria-pressed', on ? 'false' : 'true');
          toggle.querySelector('.lets-toggle-text').textContent = on ? T.pause : T.play;
        }
      };
      if (words.length > 1 && !reduce) {
        setPlaying(true);
        if (toggle) { toggle.hidden = false; toggle.addEventListener('click', function () { setPlaying(!timer); }); }
      }
    }

    /* ---------- 3) 뉴스레터 ---------- */
    var nl = document.querySelector('.newsletter');
    if (nl) {
      var nlInput = nl.querySelector('input[type="email"]');
      var nlStatus = nl.querySelector('.newsletter-status');
      var nlBtn = nl.querySelector('button[type="submit"]');
      var busy = false;
      var say = function (msg, state) { nlStatus.textContent = msg; nlStatus.setAttribute('data-state', state); };
      /* 2026-11-11: 구독 서비스가 연결되지 않았으면(data-endpoint 비어 있음) 입력·버튼을 비활성으로 두어
         신청할 수 있는 것처럼 보이지 않게 한다. 연결하면 data-endpoint에 주소만 넣으면 다시 켜진다 */
      if (!nl.getAttribute('data-endpoint')) {
        nl.setAttribute('data-state', 'off');
        nlInput.disabled = true;
        nlBtn.disabled = true;
      }
      nl.addEventListener('submit', function (e) {
        e.preventDefault();
        if (busy) return;
        var v = nlInput.value.trim();
        var bad = !v ? T.nlEmpty : (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v) ? T.nlInvalid : '');
        nlInput.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad) { say(bad, 'error'); nlInput.focus(); return; }
        var endpoint = nl.getAttribute('data-endpoint');
        if (!endpoint) { say(T.nlOff, 'off'); return; }
        busy = true; nlBtn.setAttribute('aria-disabled', 'true'); say(T.nlSending, 'sending');
        fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ email: v, language: lang }) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); say(T.nlOk, 'ok'); nl.reset(); })
          .catch(function () { say(T.nlFail, 'error'); })
          .then(function () { busy = false; nlBtn.removeAttribute('aria-disabled'); });
      });
    }

    /* ---------- 4) Hero 영상 ---------- */
    var slot = document.querySelector('[data-hero-video]');
    if (slot && !reduce) {
      var small = slot.getAttribute('data-hero-video-sm');
      var src = (small && window.matchMedia('(max-width: 900px)').matches) ? small : slot.getAttribute('data-hero-video');
      var img = slot.querySelector('img');
      var v = document.createElement('video');
      v.className = 'hero-video';
      v.muted = true; v.loop = true; v.playsInline = true; v.autoplay = true;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
      v.preload = 'auto';
      v.poster = img ? (img.currentSrc || img.src) : '';
      var btn = slot.querySelector('.hero-video-toggle');
      /* 파일이 없거나 재생할 수 없으면 영상을 지우고 포스터 사진만 남긴다 */
      v.addEventListener('error', function () { v.remove(); if (btn) btn.hidden = true; });
      v.addEventListener('playing', function () { if (btn) btn.hidden = false; }, { once: true });
      v.src = src;
      slot.insertBefore(v, btn);
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
      if (btn) {
        btn.addEventListener('click', function () {
          if (v.paused) { v.play(); btn.setAttribute('aria-pressed', 'false'); btn.querySelector('span').textContent = T.pause; }
          else { v.pause(); btn.setAttribute('aria-pressed', 'true'); btn.querySelector('span').textContent = T.play; }
        });
      }
    }
  });
})();
