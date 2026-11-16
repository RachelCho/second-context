"""Second Context 한국어 페이지에 언어 전환·hreflang을 넣고, 번역 표로 en/ 영어 페이지를 만든다.
사용: python3 tools/build_en_pages.py docs   (배포 폴더 docs/ 기준, 여러 번 실행해도 결과가 같다)
운영 도메인(2026-11-09 분리): 한국어 홈 index.html → https://second-context.com/, 영어 홈 en/index.html → /en/
원본: my-portfolio의 Second Context 페이지(tools/sync_from_portfolio.py가 docs/로 복사한 뒤 이 스크립트를 실행)"""
import os, re, sys

R = sys.argv[1]
BASE = "https://second-context.com/"
PAGES = ["index.html", "second-context-approach.html", "second-context-contact.html", "second-context-about.html", "second-context-work.html"]
# 사례 상세(2026-11-16): 홈 What we do 카드마다 독립 사례 페이지. 번역은 아래 CASE_PAGES(사례 페이지 공통, 있는 문구만 적용)
CASES = ["second-context-case-healthcare.html", "second-context-case-monitoring.html", "second-context-case-identity.html", "second-context-case-localization.html", "second-context-case-ogs.html"]
PAGES += CASES


def href(page, prefix=""):
    """홈은 폴더 주소(./, en/, ../)로 연결해 /index.html이 주소창에 보이지 않게 한다"""
    return (prefix or "./") if page == "index.html" else prefix + page


def url(page, lang="ko"):
    return BASE + ("en/" if lang == "en" else "") + ("" if page == "index.html" else page)


def head_links(page):
    ko, en = url(page), url(page, "en")
    return (f'<link rel="alternate" hreflang="ko" href="{ko}">\n'
            f'<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{ko}">\n')


# Open Graph 이미지(tools/make_og_images.py로 만든 assets/og/<이름>-<언어>.png). 이전 창업자 소개 주소는 홈 이미지를 쓴다
OG_IMAGE = {PAGES[0]: "home", PAGES[1]: "approach", PAGES[2]: "contact", PAGES[3]: "home", PAGES[4]: "work"}
OG_IMAGE.update({c: "work" for c in CASES})
OG_IMAGE["second-context-case-ogs.html"] = "ogs"  # 공개 사례: 바둑판 OG 이미지
OG_RE = re.compile(r'(<meta (?:property="og:|name="twitter:)[^>]*>\n)+')
DESC_RE = re.compile(r'<meta name="description" content="[^"]*">\n')


def og_tags(page, lang, s):
    """페이지의 title·description으로 Open Graph·Twitter 카드 태그를 만든다. 이미지 설명은 이미지 속 h1 문구"""
    title = re.search(r'<title>(.*?)</title>', s).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
    img_page = PAGES[0] if OG_IMAGE[page] == "home" else page
    src = s if img_page == page else open(os.path.join(R, ("en/" if lang == "en" else "") + img_page), encoding="utf-8").read()
    h1 = re.sub(r'<[^>]+>', '', re.search(r'(?s)<h1[^>]*>(.*?)</h1>', src).group(1)).strip()
    # 이미지: 검정 바탕 + 흰 두 사각 프레임 심볼(tools/make_brand_icons.py, 2026-11-10)
    alt = 'Second Context 로고: 검정 바탕의 흰 두 사각 프레임' if lang == "ko" else 'Second Context logo: two white open frames on black'
    page_url = url(page, lang)
    img = f'{BASE}assets/og/{OG_IMAGE[page]}-{lang}.png'
    locale, other = ("ko_KR", "en_US") if lang == "ko" else ("en_US", "ko_KR")
    return (f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="Second Context">\n'
            f'<meta property="og:locale" content="{locale}">\n'
            f'<meta property="og:locale:alternate" content="{other}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{page_url}">\n'
            f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{alt}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n')


def add_og(page, lang, s):
    d = DESC_RE.search(s).group(0)
    assert s.count(d) == 1
    return s.replace(d, d + og_tags(page, lang, s))


def lang_nav(page, cur):
    if cur == "ko":
        return ('    <nav class="lang" aria-label="언어 선택">\n'
                f'      <a href="{href(page)}" lang="ko" hreflang="ko" aria-current="true">한국어</a>\n'
                '      <span aria-hidden="true">/</span>\n'
                f'      <a href="{href(page, "en/")}" lang="en" hreflang="en"><span aria-hidden="true">EN</span><span class="sr-only">English</span></a>\n'
                '    </nav>\n')
    return ('    <nav class="lang" aria-label="Language">\n'
            f'      <a href="{href(page, "../")}" lang="ko" hreflang="ko">한국어</a>\n'
            '      <span aria-hidden="true">/</span>\n'
            f'      <a href="{href(page)}" lang="en" hreflang="en" aria-current="true"><span aria-hidden="true">EN</span><span class="sr-only">English</span></a>\n'
            '    </nav>\n')


def footer_lang(page, cur):
    """푸터 맨 아래의 언어 링크: 헤더와 같은 대상(현재 페이지의 다른 언어판)"""
    return lang_nav(page, cur).replace('<nav class="lang"', '<nav class="lang lang-footer"', 1).replace('\n    ', '\n      ').replace('    <nav', '      <nav', 1)


def prep_korean(page):
    """한국어 원본에 canonical·hreflang·언어 전환만 추가한다. 본문은 건드리지 않는다."""
    p = os.path.join(R, page)
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'<link rel="canonical"[^>]*>\n(<link rel="alternate"[^>]*>\n)*', "", s)
    s = add_og(page, "ko", OG_RE.sub("", s))
    s = s.replace('<script src="assets/lang.js"></script>\n', '')
    s = re.sub(r'    <nav class="lang".*?    </nav>\n', "", s, flags=re.S)
    s = re.sub(r'      <nav class="lang lang-footer".*?      </nav>\n', "", s, flags=re.S)
    anchor = '<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + f'<link rel="canonical" href="{url(page)}">\n' + head_links(page)
                  + '<script src="assets/lang.js"></script>\n')
    # 언어 링크는 주요 메뉴와 검색 버튼 사이 (2026-11-10 헤더: 로고 · 메뉴 · 언어 · 검색)
    end = '    <button type="button" class="search-open"'
    assert s.count(end) == 1
    s = s.replace(end, lang_nav(page, "ko") + end)
    # 푸터에도 같은 언어 링크 (저작권 앞)
    fend = '      <p class="footer-copy">'
    assert s.count(fend) == 1
    s = s.replace(fend, footer_lang(page, "ko") + fend)
    open(p, "w", encoding="utf-8").write(s)
    return s


COMMON = [
    # 2026-11-10 2차: 검색·뉴스레터 라벨, Follow (메뉴 이름은 sc_chrome.py에서 영어로 고정)
    ('<form class="search-form" role="search" aria-label="사이트 검색">', '<form class="search-form" role="search" aria-label="Site search">'),
    ('<label class="sr-only" for="search-input">사이트 검색어</label>', '<label class="sr-only" for="search-input">Search the site</label>'),
    ('<label class="newsletter-label" for="nl-email">뉴스레터 구독 이메일</label>', '<label class="newsletter-label" for="nl-email">Email for the newsletter</label>'),
    ('<span class="sr-only">뉴스레터 구독 신청</span>', '<span class="sr-only">Subscribe to the newsletter</span>'),
    ('<span class="sr-only"> — Second Context 회사 페이지</span>', '<span class="sr-only"> — Second Context company page</span>'),
    ('<span class="fl-off-note">준비 중</span>', '<span class="fl-off-note">Coming soon</span>'),
    ('<html lang="ko">', '<html lang="en">'),
    ('본문 바로가기', 'Skip to main content'),
    ('aria-label="Second Context 홈"', 'aria-label="Second Context home"'),
    ('aria-label="주요 메뉴"', 'aria-label="Main menu"'),
    ('(새 탭에서 열림)', '(opens in a new tab)'),
    # 2026-11-11: 한국어 페이지의 상담 버튼은 모두 "30분 상담 예약", 영어는 "Book a 30-minute consultation"으로 통일
    ('30분 상담 예약하기', 'Book a 30-minute consultation'),
    ('30분 상담 예약', 'Book a 30-minute consultation'),
    ('프로젝트 문의하기', 'Send a project inquiry'),
    ('30분 상담으로 시작합니다.', 'Start with a 30-minute call.'),
    # 2026-10-29 사진·비주얼 재구성
    ('<span class="ex-label">예시 산출물</span>', '<span class="ex-label">Example deliverable</span>'),
    # 2026-11-10 다크 리디자인: 공통 헤더·검색·푸터 (tools/sc_chrome.py)
    ('<span class="sr-only">사이트 검색</span>', '<span class="sr-only">Search the site</span>'),
    ('<p class="search-title" id="search-title">사이트 검색</p>', '<p class="search-title" id="search-title">Search the site</p>'),
    ('<span>닫기</span>', '<span>Close</span>'),
    ('<label class="sr-only" for="search-input">검색어</label>', '<label class="sr-only" for="search-input">Search terms</label>'),
    ('placeholder="사례, 서비스, 페이지 검색"', 'placeholder="Search case studies, services, pages"'),
    ('<span class="sr-only">검색</span>', '<span class="sr-only">Search</span>'),
    ('<span class="lets-toggle-text">일시정지</span><span class="sr-only"> 움직이는 문구</span>', '<span class="lets-toggle-text">Pause</span><span class="sr-only"> moving text</span>'),
    ('<label class="fl-title" for="nl-email">뉴스레터</label>', '<label class="fl-title" for="nl-email">Newsletter</label>'),
    ('구독 서비스 연결 준비 중입니다. 지금은 신청해도 등록되지 않습니다.', 'The subscription service isn’t connected yet. Signing up now won’t register you.'),
    ('<span class="sr-only">구독 신청</span>', '<span class="sr-only">Subscribe</span>'),
    ('예시 콘셉트', 'Illustrative concept'),
    ('맥락으로 완성하는, 독립 프로덕트 디자인.', 'Independent product design, shaped by context.'),
    ('aria-label="경력 요약"', 'aria-label="Career summary"'),
    ('<span class="stat-label">완료한 프로젝트</span>', '<span class="stat-label">Projects completed</span>'),
    ('<span class="stat-label">함께 일한 글로벌·다국적 기업</span>', '<span class="stat-label">Global &amp; multinational companies worked with</span>'),
    ('<span class="stat-label">여행한 국가</span>', '<span class="stat-label">Countries visited</span>'),
    ('alt="Rachel Cho 프로필 사진"', 'alt="Portrait of Rachel Cho"'),
    ('밝은 실내에서 의자에 앉아 미소 짓는 Rachel Cho', 'Rachel Cho smiling, seated in a bright room'),
]

HOME = [
    ('<title>Second Context — 시장을 넘나드는 제품 디자인</title>', '<title>Second Context — Product design across markets.</title>'),
    ('미국 시장을 준비하는 한국 B2B SaaS 팀을 위한 제품 UX 진단과 디자인.',
     'Product UX reviews and design for Korean B2B SaaS teams preparing for the U.S. market.'),
    # 2026-11-10 다크 리디자인 홈
    ('<h1>새로운 시장의 맥락을, 제품의 다음 단계로.</h1>', '<h1>New market context, your product’s next step.</h1>'),
    ('<span class="lead-line">사용자와 업무 환경의 차이를 이해하고,</span> <span class="lead-line">제품 경험과 실행 우선순위를 함께 설계합니다.</span>',
     'We understand how your users and their work environments differ, then design the product experience and execution priorities with your team.'),
    ('>사례 살펴보기</a>', '>Explore our work</a>'),
    ('alt="제품 화면이 띄워진 대형 화면 앞에서 손짓으로 설명하며 팀과 논의를 이끄는 Rachel Cho"',
     'alt="Rachel Cho gesturing in front of a large screen showing product slides as she leads a team discussion"'),
    ('<span>일시정지</span><span class="sr-only"> 배경 영상</span>', '<span>Pause</span><span class="sr-only"> background video</span>'),
    # 사례 대표 제품 이미지(2026-11-10)
    ('Second Context는 Rachel Cho가 이끄는 독립 프로덕트 디자인 스튜디오입니다. 미국 홈헬스케어 SaaS의 파운딩 디자이너로 AI 일정 플랫폼을 설계했고, 글로벌 제약사의 운영 모니터링·인시던트 관리 경험과 글로벌 기업의 제품 현지화를 맡았습니다. 복잡한 규칙과 업무 흐름을, 사용자가 바로 판단하고 행동할 수 있는 제품 경험으로 바꿉니다.',
     'Second Context is an independent product design studio led by Rachel Cho. As founding designer at a U.S. home healthcare SaaS, she designed an AI scheduling platform, and she has designed operations monitoring and incident management for a global pharmaceutical company and product localization for global companies. She turns complex rules and workflows into product experiences people can understand and act on right away.'),
    # 2026-11-10 2차: 선택 이유 · 서비스 · 진행 방식 · 문의 섹션 (이전 홈의 검증된 문구를 다시 쓴다)
    ('제품과 사람, 비즈니스를 함께 이해합니다.', 'We understand products, people, and business—together.'),
    ('번역만으로는 제품이 현지에서 쓰이지 않습니다. 같은 제품도 시장과 사용자가 달라지면 일하는 방식, 제품을 이해하는 방식, 신뢰를 판단하는 기준이 함께 달라지고, 한국 시장에 맞춰 제품을 만들어 온 팀은 이 차이를 내부에서 발견하기 어렵습니다.', 'Translation alone won’t get your product used in a new market. When the market and users change, how people work, how they make sense of a product, and how they judge trust all shift too—and teams that built for the Korean market often find these differences hard to see from the inside.'),
    ('좋은 판단이 팀의 실행으로 이어지도록.', 'So good decisions turn into team action.'),
    ('디자인은 화면을 만드는 데서 끝나지 않습니다. 설계 의도와 우선순위를 팀이 이해할 수 있는 말로 설명하고, 다음에 무엇을 할지 함께 정합니다.', 'Design doesn’t end with screens. We explain design intent and priorities in language the whole team can use, and decide together what happens next.'),
    ('<p>사용자 영향·사업 중요도·구현 난이도로 우선순위의 이유를 설명합니다.</p>', '<p>Explain the reasons behind priorities using user impact, business importance, and implementation effort.</p>'),
    ('<p>디자인 의도와 요구사항, 예외 상황을 개발 전에 정리합니다.</p>', '<p>Document design intent, requirements, and edge cases before development.</p>'),
    ('<p>합의한 방향을 팀이 실행할 수 있는 다음 작업으로 나눕니다.</p>', '<p>Break the agreed direction into next tasks the team can act on.</p>'),
    # 2026-11-11: 사례 01 오른쪽 카드(한국어는 한국어 문구, 영어는 기존 영어 문구 유지)
    ('네 단계는 협업의 큰 흐름입니다. 진행 방식 페이지에서는 이를 여섯 단계의 실행 과정과 단계별 산출물로 나눠 설명합니다.',
     'These four steps outline how we work together. The Approach page breaks them into six working steps, each with its own deliverable.'),
    ('노트북을 사이에 두고 웃으며 제품 이야기를 나누는 세 사람', 'Three people smiling as they talk about a product over a laptop'),
    ('화이트보드에 그린 화면 흐름을 가리키며 팀에게 설명하는 사람', 'A person pointing to a screen flow drawn on a whiteboard while explaining it to the team'),
    ('유리벽에 손으로 그린 화면 흐름을 설명하는 사람과 이를 지켜보는 동료 세 명', 'A person explaining a hand-drawn screen flow on a glass wall as three colleagues look on'),
    ('맥락에서 시작해, 실행까지 함께합니다.', 'From context to delivery, together.'),
    ('<span class="lead-line">제품과 팀의 현재 단계에 맞춰</span> <span class="lead-line">네 단계로 진행합니다.</span>', '<span class="lead-line">Matched to where your product and team are today,</span> <span class="lead-line">we work in four steps.</span>'),
    ('<h3>맥락 이해</h3>', '<h3>Understand context</h3>'),
    ('제품과 목표 시장, 사용자와 업무 환경을 살펴 현재 상황을 함께 파악합니다.', 'We look at your product, target market, users, and work environment to understand where things stand.'),
    ('<h3>문제 정의</h3>', '<h3>Define the problem</h3>'),
    ('사용자 영향·사업 중요도·구현 난이도로 먼저 풀 문제와 우선순위를 정합니다.', 'We decide which problems to solve first, and in what order, using user impact, business importance, and implementation effort.'),
    ('<h3>디자인 및 검증</h3>', '<h3>Design and validate</h3>'),
    ('사용자 흐름과 화면을 설계하고, 프로토타입으로 사용자와 팀에게 확인합니다.', 'We design user flows and screens, then check them with users and your team through prototypes.'),
    ('<h3>실행 지원</h3>', '<h3>Support delivery</h3>'),
    ('디자인 의도와 요구사항, 예외 상황을 정리해 개발 과정의 해석 차이를 줄입니다.', 'We document design intent, requirements, and edge cases to reduce differences in interpretation during development.'),
    ('>진행 방식 자세히 보기</a>', '>More about our approach</a>'),
    ('제품과 목표 시장, 현재 고민하고 계신 과제를 알려 주세요. <span class="keep">협업할 범위를 함께 살펴보겠습니다.</span>',
     'Tell us about your product, your target market, and the challenges you’re working through. We’ll explore the right scope of collaboration together.'),
]

# 사례 문구: 홈 Work 요약과 사례 페이지(second-context-work.html)가 함께 쓰는 번역. 페이지에 있는 것만 적용한다
CASE_TEXT = [
    ('복잡한 업무와 새로운 사용 맥락을, 명확한 제품 경험으로.', 'Turning complex work and new contexts of use into clear product experiences.'),
    ('Second Context를 시작하기 전, Rachel Cho가 이전 경력에서 수행한 세 프로젝트입니다. 고객사 이름은 밝히지 않습니다.',
     'Three projects Rachel Cho delivered in previous roles, before starting Second Context. Client names are not disclosed.'),
    # 01 홈헬스케어
    ('미국 홈헬스케어 SaaS의 일정 관리 UX', 'Scheduling UX for a U.S. home healthcare SaaS'),
    ('미국 홈헬스케어 SaaS의 <span class="tl">일정 관리 UX</span>', 'Scheduling UX <span class="tl">for a U.S. home healthcare SaaS</span>'),
    ('복잡한 자격 조건·일정 규칙·예외를 사용자가 이해하고 바로 행동할 수 있게 설계했습니다.',
     'Designed complex eligibility conditions, scheduling rules, and exceptions so users could understand them and act right away.'),
    ('내부 규칙과 코드를 그대로 보여주는 대신, 예약 가능한 날짜를 보여주는 달력과 명확한 상태 표시로 다음 행동을 판단할 수 있게 했습니다.',
     'Instead of exposing internal rules and codes, a calendar of bookable dates and clear status indicators let users decide their next step.'),
    ('5.8 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 8.2', '5.8 <span aria-hidden="true">→</span><span class="sr-only"> to </span> 8.2'),
    ('파일럿에서 측정한 일정 계획 자신감', 'Confidence in planning schedules, measured in the pilot'),
    ('180초 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 60초', '180 sec <span aria-hidden="true">→</span><span class="sr-only"> to </span> 60 sec'),
    ('여러 개선이 함께 적용된 후의 작업 시간', 'Task time after several improvements were applied together'),
    ('<p class="metric-value">3,000명 이상</p>', '<p class="metric-value">3,000+</p>'),
    ('AI 일정 추천 경험을 사용하는 임상의', 'Clinicians using the AI scheduling recommendation experience'),
    ('미국 홈헬스케어 운영팀이 임상의 방문 일정을 조정하는 AI 일정 관리 플랫폼입니다. 일정 담당자는 환자 자격·방문 빈도·인력 가용성을 함께 고려해야 했고, 이 과정에서 반복 문의와 혼란이 발생했습니다.',
     'An AI scheduling platform that U.S. home healthcare operations teams use to coordinate clinician visits. Schedulers had to weigh patient eligibility, visit frequency, and staff availability together, which led to repeated questions and confusion.'),
    ('파운딩 디자이너(Senior Product Designer)로 참여했습니다.', 'Joined as the founding designer (Senior Product Designer).'),
    ('CEO와 함께 핵심 AI 일정 플랫폼의 제품 디자인 비전과 전략을 정의하고, 비즈니스 목표를 0→1 단계의 엔드투엔드 디자인 방향으로 옮겼습니다.',
     'Defined the product design vision and strategy for the core AI scheduling platform with the CEO, translating business goals into end-to-end design direction from 0 to 1.'),
    ('CTO, 프런트엔드 엔지니어 6명과 함께 회사의 첫 Figma 디자인 시스템을 만들었습니다.',
     'Built the company’s first Figma design system with the CTO and 6 front-end engineers.'),
    ('디자인·제품·엔지니어링이 함께 쓰는 회사의 첫 엔드투엔드 디자인 프로세스를 만들었습니다.',
     'Established the company’s first end-to-end design process shared by design, product, and engineering.'),
    ('자격·방문 빈도·인력 가용성 규칙이 겹쳐 반복 문의와 혼란이 생겼기 때문에, 규칙을 설명하는 대신 예약 가능한 날짜와 상태를 먼저 보여주도록 했습니다.',
     'Because overlapping eligibility, visit-frequency, and availability rules caused repeated questions and confusion, the design shows bookable dates and status first instead of explaining the rules.'),
    ('내부 코드는 사용자가 이해할 수 있는 문구로 바꿨습니다.', 'Replaced internal codes with wording users could understand.'),
    ('의사결정 속도와 확신을 함께 높이기 위해, AI가 만든 일정 추천을 어떻게 보여주고 검증하고 조정할지 정의했습니다.',
     'To improve both decision speed and confidence, defined how AI-generated schedule recommendations are surfaced, validated, and adjusted.'),
    ('예약 가능한 날짜를 보여주는 달력과 일정 상태 표시', 'A calendar of bookable dates and schedule status indicators'),
    ('내부 코드를 대신하는 화면 문구', 'UI wording that replaces internal codes'),
    ('AI 일정 추천을 확인·검증·조정하는 흐름', 'A flow for reviewing, validating, and adjusting AI schedule recommendations'),
    ('파일럿에서 일정 계획 자신감 <strong class="metric-num">5.8 → 8.2</strong>', 'Schedule-planning confidence <strong class="metric-num">5.8 → 8.2</strong> in the pilot'),
    ('여러 개선이 함께 적용된 후 작업 시간 <strong class="metric-num">180초 → 60초</strong>', 'Task time <strong class="metric-num">180 sec → 60 sec</strong> after several improvements were applied together'),
    ('AI 보조 일정 워크플로에서 수동 검증 <strong class="metric-num">35% 감소</strong>', 'Manual validation <strong class="metric-num">reduced by 35%</strong> in the AI-assisted scheduling workflow'),
    ('임상의 <strong class="metric-num">3,000명 이상</strong>이 사용하는 일정 추천 경험', 'Scheduling recommendation experience used by <strong class="metric-num">3,000+</strong> clinicians'),
    ('디자인 시스템을 개발자 <strong class="metric-num">23명 전원</strong>이 조직 표준으로 채택', 'Design system adopted by <strong class="metric-num">all 23 developers</strong> as the org-wide standard'),
    ('디자인 시스템 도입 후 릴리스 주기 <strong class="metric-num">50% 이상 단축</strong>', 'Release cycles <strong class="metric-num">accelerated by 50%+</strong> after the design system was adopted'),
    # 02 운영 모니터링
    ('글로벌 제약사의 운영 모니터링·인시던트 관리 UX', 'Operations monitoring and incident management UX for a global pharmaceutical company'),
    ('글로벌 제약사의 <span class="tl">운영 모니터링·</span><span class="tl">인시던트 관리 UX</span>', 'Operations monitoring and incident management UX <span class="tl">for a global pharmaceutical company</span>'),
    ('많은 정보 속에서 심각도·영향 범위·조사 우선순위를 연결했습니다.',
     'Connected severity, scope of impact, and investigation priority across a large volume of information.'),
    ('8개 대시보드에 흩어진 정보를 심각도와 후속 영향 중심으로 다시 구조화해, 무엇부터 조사할지 먼저 판단할 수 있게 했습니다.',
     'Restructured information scattered across 8 dashboards around severity and downstream impact, so teams could first decide what to investigate.'),
    ('30분 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 3분', '30 min <span aria-hidden="true">→</span><span class="sr-only"> to </span> 3 min'),
    ('<p class="metric-value">80% 단축</p>', '<p class="metric-value">80% faster</p>'),
    ('의사결정 지원 흐름과 신호 표시를 다시 설계한 뒤의 인시던트 분류(triage) 시간',
     'Incident triage time after redesigning decision-support workflows and signal display'),
    ('<p class="metric-value">40% 단축</p>', '<p class="metric-value">40% faster</p>'),
    ('개발자 내부 도구의 티켓 처리 시간 <strong class="metric-num">40% 단축</strong>', 'Developer internal-tool ticket processing time <strong class="metric-num">reduced by 40%</strong>'),
    ('개발자 내부 도구의 티켓 처리 시간', 'Ticket processing time in developers’ internal tools'),
    ('백신 운영을 지원하는 엔터프라이즈 모니터링 플랫폼으로, 제약사 엔지니어링팀이 사용했습니다. 운영 담당자는 인시던트를 조사하기 위해 8개 대시보드를 오가며 심각도와 영향을 파악해야 했습니다.',
     'An enterprise monitoring platform supporting vaccine operations, used by the company’s engineering teams. To investigate an incident, operators had to move between 8 dashboards to work out severity and impact.'),
    ('UX 디자인 에이전시를 통해 계약 Senior Product Designer로 참여했습니다.', 'Joined as a contract Senior Product Designer through a UX design agency.'),
    ('글로벌 IT 기업의 AI/ML 팀과 협업해 생성형 AI 기반 인시던트 관리 시스템을 설계하고, 모델 출력을 엔터프라이즈 사용자가 행동할 수 있는 신호로 바꿨습니다.',
     'Designed a generative-AI incident management system with a global IT company’s AI/ML teams, translating model outputs into actionable signals for enterprise users.'),
    ('이해관계자 인터뷰 15회를 진행해 위험 예측·알림·신뢰도 같은 AI 인사이트를 어떻게 보여주고 우선순위를 정할지 정의했습니다.',
     'Conducted 15 stakeholder interviews to define how AI insights such as risk predictions, alerts, and confidence levels are surfaced and prioritized.'),
    ('담당자가 8개 대시보드를 오가며 심각도와 영향을 직접 맞춰 봐야 했기 때문에, 정보 구조를 심각도와 후속 영향 중심으로 다시 설계했습니다.',
     'Because operators had to piece together severity and impact across 8 dashboards themselves, the information architecture was redesigned around severity and downstream impact.'),
    ('위험 예측·알림·신뢰도를 같은 무게로 나열하지 않고, 조사 우선순위에 따라 보여주는 기준을 정했습니다.',
     'Rather than listing risk predictions, alerts, and confidence levels with equal weight, set criteria for showing them by investigation priority.'),
    ('엔지니어링팀과 성능을 고려한 목록 탐색 방식을 조율했습니다.', 'Aligned with engineering on a list-browsing approach that accounts for performance.'),
    ('심각도와 후속 영향을 중심으로 한 인시던트 조사 흐름', 'An incident investigation flow centered on severity and downstream impact'),
    ('AI 인사이트를 우선순위에 따라 보여주는 의사결정 지원 화면', 'Decision-support screens that surface AI insights by priority'),
    ('성능을 고려한 인시던트 목록 탐색', 'Performance-aware incident list browsing'),
    ('프로젝트에서 보고된 인시던트 조사 시간 <strong class="metric-num">30분 → 3분</strong>', 'Incident investigation time <strong class="metric-num">30 min → 3 min</strong>, as reported in the project'),
    ('프로젝트에서 보고된 인시던트 조사 시간', 'Incident investigation time reported in the project'),
    ('의사결정 지원 흐름 재설계와 신호 명확화 후 인시던트 분류(triage) 시간 <strong class="metric-num">80% 단축</strong>',
     'Incident triage time <strong class="metric-num">reduced by 80%</strong> after redesigning decision-support workflows and clarifying signals'),
    ('이해관계자 인터뷰 <strong class="metric-num">15회</strong>', '<strong class="metric-num">15</strong> stakeholder interviews'),
    ('이해관계자 인터뷰 15회', '15 stakeholder interviews'),
    # 03 한국어 현지화
    ('글로벌 테크 기업의 한국어 제품 현지화', 'Korean product localization for a global tech company'),
    ('글로벌 테크 기업의 <span class="tl">한국어 제품 현지화</span>', 'Korean product localization <span class="tl">for a global tech company</span>'),
    ('언어와 사용 맥락에 맞춰 제품 경험을 조정했습니다.', 'Adapted the product experience to the language and its context of use.'),
    ('번역된 문구에서 멈추지 않고, 이름·날짜·시간 표기와 타이포그래피·간격까지 한국어 사용 맥락에 맞춰 조정했습니다.',
     'Went beyond translated copy, adapting name, date, and time formats as well as typography and spacing to the Korean context of use.'),
    ('<p class="metric-value">6주</p>', '<p class="metric-value">6 weeks</p>'),
    ('2019년, 제작 에이전시와 고객사의 한국·미국 팀이 함께한 현지화 기간',
     'Localization period in 2019, with a production agency and the client’s Korea and U.S. teams'),
    ('5K 디스플레이 데스크톱 제품 관련 콘텐츠를 한국 시장에 맞추는 프로젝트였습니다. 글로벌 브랜드의 표현과 한국어의 자연스러운 문구·레이아웃을 함께 유지해야 했습니다.',
     'A project adapting content for a 5K-display desktop product to the Korean market, keeping the global brand’s expression while making Korean copy and layout read naturally.'),
    ('2019년 6주 동안 영국의 글로벌 제작 에이전시, 고객사의 한국 팀·미국 팀과 협업하며 UX 문구와 디자인 자산을 현지화하고 팀 간 소통을 지원했습니다.',
     'Over 6 weeks in 2019, worked with a global production agency in the U.K. and the client’s Korea and U.S. teams to localize UX copy and design assets and support communication between teams.'),
    ('글로벌 브랜드의 표현과 한국어의 자연스러움을 함께 지켜야 했기 때문에, 문구만 옮기지 않고 이름·날짜·시간 표기 방식까지 한국어 관례에 맞췄습니다.',
     'Because both the global brand’s expression and natural Korean had to be preserved, name, date, and time formats were matched to Korean conventions, not just the copy.'),
    ('같은 이유로 타이포그래피와 간격을 한국어 문장에 맞춰 조정했습니다.', 'For the same reason, typography and spacing were adjusted for Korean text.'),
    ('영국·한국·미국 팀의 관점이 어긋나지 않도록 팀 간 소통을 지원했습니다.', 'Supported communication so the U.K., Korea, and U.S. teams stayed aligned.'),
    ('한국어 UX 문구', 'Korean UX copy'),
    ('이름·날짜·시간 표기', 'Name, date, and time formats'),
    ('한국어 타이포그래피와 간격을 반영한 현지화 레이아웃', 'Localized layouts reflecting Korean typography and spacing'),
    ('한국 시장에 맞춘 UX 문구와 디자인 자산', 'UX copy and design assets tailored to the Korean market'),
    ('<li>현지화 레이아웃</li>', '<li>Localized layouts</li>'),
    # 공통 라벨
    ('<strong>핵심 설계 판단</strong>', '<strong>Key design decision</strong>'),
    ('<summary>사례 자세히 보기</summary>', '<summary>Read the full case</summary>'),
    ('<dt>프로젝트 맥락과 문제</dt>', '<dt>Project context and problem</dt>'),
    ('<dt>Rachel의 역할과 책임</dt>', '<dt>Rachel’s role and responsibilities</dt>'),
    ('<dt>핵심 설계 판단과 이유</dt>', '<dt>Key design decisions and why</dt>'),
    ('<dt>바뀐 화면과 업무 흐름</dt>', '<dt>Screens and workflows changed</dt>'),
    ('<dt>결과</dt>', '<dt>Results</dt>'),
    ('<dt>산출물</dt>', '<dt>Deliverables</dt>'),
    ('<span class="metric-kind">사용자 평가</span>', '<span class="metric-kind">User rating</span>'),
    ('<span class="metric-kind">업무 성과</span>', '<span class="metric-kind">Work outcome</span>'),
    ('<span class="metric-kind">도입 범위</span>', '<span class="metric-kind">Adoption scope</span>'),
    ('<span class="metric-kind">리서치 범위</span>', '<span class="metric-kind">Research scope</span>'),
    ('<span class="metric-kind">프로젝트 기간</span>', '<span class="metric-kind">Project length</span>'),
    ('수치는 각 프로젝트에서 측정·보고된 값이며, 측정 방식은 프로젝트마다 다릅니다.',
     'Figures are as measured and reported in each project; measurement methods differ by project.'),
    # 사례 페이지 전용
    ('<title>사례 — Second Context</title>', '<title>Selected work — Second Context</title>'),
    ('Rachel Cho가 이전 경력에서 수행한 세 프로젝트의 문제, 역할, 핵심 설계 판단과 확인된 결과.',
     'The problem, role, key design decisions, and confirmed results of three projects Rachel Cho delivered in previous roles.'),
    ('<h1>세 프로젝트로 보는 설계 판단</h1>', '<h1>Design decisions, in three projects</h1>'),
    ('Second Context를 시작하기 전, Rachel Cho가 이전 경력에서 수행한 프로젝트입니다. 고객사 이름은 밝히지 않으며, 화면은 설계 판단을 설명하기 위해 다시 구성했습니다.',
     'Projects Rachel Cho delivered in previous roles, before starting Second Context. Client names are not disclosed, and the screens are recreated to illustrate the design decisions.'),
    ('aria-label="사례 바로가기"', 'aria-label="Jump to a case"'),
    ('<dt>과제</dt>', '<dt>Challenge</dt>'),
    ('<dt>개요 · 내 역할</dt>', '<dt>Overview</dt>'),
    ('<dt>접근 · 핵심 설계 판단</dt>', '<dt>Approach</dt>'),
    ('<dt>해결 · 바뀐 화면과 흐름</dt>', '<dt>Solution</dt>'),
    ('<dt>결과 · 확인된 산출물</dt>', '<dt>Outcomes (deliverables)</dt>'),
    ('<dt>결과 · 확인된 수치</dt>', '<dt>Outcomes</dt>'),
    ('<p class="work-link"><a href="second-context-work.html#case-healthcare">사례 자세히 보기</a></p>', '<p class="work-link"><a href="second-context-work.html#case-healthcare">Read the full case</a></p>'),
    ('<p class="work-link"><a href="second-context-work.html#case-monitoring">사례 자세히 보기</a></p>', '<p class="work-link"><a href="second-context-work.html#case-monitoring">Read the full case</a></p>'),
    ('<p class="work-link"><a href="second-context-work.html#case-localization">사례 자세히 보기</a></p>', '<p class="work-link"><a href="second-context-work.html#case-localization">Read the full case</a></p>'),
    # 데모 공통
    ('aria-label="인터랙션 단계"', 'aria-label="Interaction steps"'),
    ('>모션 재생</button>', '>Play motion</button>'),
    ('>정지</button>', '>Stop</button>'),
    ('>다시 보기</button>', '>Replay</button>'),
    ('설계 설명을 위한 재구성 · 실제 프로젝트 화면이 아닌 예시 문구', 'Recreated for illustration · Sample copy, not actual project screens'),
    ('설계 설명을 위한 재구성 · 예시 데이터', 'Recreated for illustration · Sample data'),
    # 데모 1: 홈헬스케어
    ('</span>날짜 선택</button>', '</span>Pick a date</button>'),
    ('</span>제한 이유 확인</button>', '</span>See why it’s blocked</button>'),
    ('</span>다음 행동</button>', '</span>Next step</button>'),
    ('aria-label="재구성한 방문 일정 화면"', 'aria-label="Recreated visit scheduling screen"'),
    ('<span class="ui-title">방문 일정</span><span class="ui-sub">예시 환자 A</span>', '<span class="ui-title">Visit schedule</span><span class="ui-sub">Sample patient A</span>'),
    ('aria-label="상태 범례"', 'aria-label="Status legend"'),
    ('</span>예약 가능</li>', '</span>Available</li>'),
    ('</span>제한</li>', '</span>Blocked</li>'),
    ('</span>선택</li>', '</span>Selected</li>'),
    ('aria-label="예시 달력 2주"', 'aria-label="Sample two-week calendar"'),
    ('<span role="columnheader">월</span><span role="columnheader">화</span><span role="columnheader">수</span><span role="columnheader">목</span><span role="columnheader">금</span><span role="columnheader">토</span><span role="columnheader">일</span>',
     '<span role="columnheader">Mon</span><span role="columnheader">Tue</span><span role="columnheader">Wed</span><span role="columnheader">Thu</span><span role="columnheader">Fri</span><span role="columnheader">Sat</span><span role="columnheader">Sun</span>'),
    ('</span>10일은 예약할 수 없습니다</p>', '</span>The 10th can’t be booked</p>'),
    ('이번 주 방문 횟수(2회)를 이미 모두 사용했습니다.', 'This week’s visit limit (2 visits) has already been used.'),
    ('→ 사용자가 이해할 수 있는 문장으로 표시', '→ shown as a sentence users can understand'),
    ('추천 일정: 12일(금) 오전', 'Recommended: Fri the 12th, morning'),
    ('방문 빈도와 담당 임상의 가능 시간을 함께 확인한 날짜입니다.', 'This date fits both the visit frequency and the assigned clinician’s availability.'),
    ('<span class="ui-btn ui-btn-fill">추천 확인</span><span class="ui-btn">다른 날짜 선택</span>', '<span class="ui-btn ui-btn-fill">Confirm</span><span class="ui-btn">Choose another date</span>'),
    ('<strong>1. 날짜 선택</strong> 규칙을 먼저 설명하지 않고, 예약 가능한 날짜와 상태를 달력에서 바로 보여 줍니다.',
     '<strong>1. Pick a date</strong> Instead of explaining the rules first, the calendar shows which dates are available and their status.'),
    ('<strong>2. 제한 이유 확인</strong> 제한된 날짜를 고르면 내부 코드 대신 이유를 문장으로 알려 줍니다.',
     '<strong>2. See why it’s blocked</strong> Choosing a blocked date explains the reason in plain language instead of an internal code.'),
    ('<strong>3. 다음 행동</strong> AI 추천 일정을 보여 주되, 사용자가 확인하거나 다른 날짜로 조정한 뒤 확정합니다.',
     '<strong>3. Next step</strong> The AI-recommended date is shown, and the user confirms it or adjusts to another date before booking.'),
    # 데모 3: 한국어 현지화 (비교 화면 자체는 i18n:keep으로 번역하지 않음)
    ('</span>원문 화면</button>', '</span>Original screen</button>'),
    ('</span>한국어 화면</button>', '</span>Korean screen</button>'),
    ('</span>변경 지점</button>', '</span>What changed</button>'),
    ('aria-label="재구성한 원문·한국어 비교 화면"', 'aria-label="Recreated original and Korean comparison screen"'),
    ('<strong>1. 원문 화면</strong> 영어 원문의 이름·날짜·시간 표기와 문장 길이를 기준으로 삼습니다.',
     '<strong>1. Original screen</strong> The English original’s name, date, and time formats and sentence length are the starting point.'),
    ('<strong>2. 한국어 화면</strong> 같은 정보를 한국어 사용자가 익숙한 순서와 표기로 옮깁니다.',
     '<strong>2. Korean screen</strong> The same information is carried over in the order and formats Korean users expect.'),
    ('<p><strong>3. 변경 지점</strong></p>', '<p><strong>3. What changed</strong></p>'),
    ('<li>이름: 성-이름 순서와 ‘님’ 호칭</li>', '<li>Names: family name first, with the honorific <span lang="ko">님</span></li>'),
    ('<li>날짜: 연-월-일 순서, 요일은 괄호로</li>', '<li>Dates: year-month-day order, with the weekday in parentheses</li>'),
    ('<li>시간: 오전·오후를 숫자 앞에</li>', '<li>Times: <span lang="ko">오전/오후</span> (a.m./p.m.) before the numbers</li>'),
    ('<li>문구·줄바꿈: 단어 단위 줄바꿈과 한글에 맞춘 글자 간격</li>', '<li>Copy and line breaks: breaking lines at word boundaries, with spacing suited to Korean text</li>'),
    # 2026-10-29 사진·비주얼 재구성
    ('재구성한 일정 화면 미리보기: 예약 가능한 날짜, 제한된 날짜, 추천 날짜를 구분한 달력', 'Recreated scheduling screen preview: a calendar distinguishing available, blocked, and recommended dates'),
    ('재구성한 인시던트 목록 미리보기: 우선 대응할 P1 항목이 맨 위에 강조된 화면', 'Recreated incident list preview: the P1 item that needs action first is highlighted at the top'),
    ('재구성한 현지화 비교 미리보기: 같은 화면의 영어 원문과 한국어 화면', 'Recreated localization comparison preview: the same screen in the English original and in Korean'),
    ('<p class="thumb-note">설계 설명을 위한 재구성</p>', '<p class="thumb-note">Recreated for illustration</p>'),
]

WORK = [
    # 사례 02 데모 탭
    ('role="tablist" aria-label="데모 선택"', 'role="tablist" aria-label="Choose a demo"'),
    ('aria-controls="panel-triage">우선 대응 판단</button>', 'aria-controls="panel-triage">Priority triage</button>'),
    ('tabindex="-1">AI 예측 요약</button>', 'tabindex="-1">AI forecast summary</button>'),
    # 사례 02 데모 A: 우선 대응 목록
    ('<h3 class="demo-title">먼저 대응할 문제를, 먼저 보이게.</h3>', '<h3 class="demo-title">Put what needs action first, first.</h3>'),
    ('기술 신호와 업무 영향을 함께 보고, 가장 먼저 대응해야 할 인시던트를 목록 맨 위에 둡니다.',
     'Technical signals and business impact are read together, so the incident that needs action first sits at the top of the list.'),
    ('</span>여러 알림</button>', '</span>Many alerts</button>'),
    ('</span>우선 대응을 위로</button>', '</span>Priority to the top</button>'),
    ('</span>클릭 후 조사</button>', '</span>Click to investigate</button>'),
    ('aria-label="재구성한 인시던트 우선순위 화면"', 'aria-label="Recreated incident priority screen"'),
    ('<span class="ui-title">인시던트</span>', '<span class="ui-title">Incidents</span>'),
    ('data-show="1">들어온 순서</span>', 'data-show="1">In order received</span>'),
    ('hidden>우선 대응 순서</span>', 'hidden>In order of priority</span>'),
    ('판단 기준: 기술 신호(이상 점수) + 업무 영향(막힌 팀·담당자 배정)', 'Criteria: technical signal (anomaly score) + business impact (blocked teams, owner assigned)'),
    ('aria-label="예시 인시던트 목록"', 'aria-label="Sample incident list"'),
    ('<span class="tri-name">예시 인시던트 D · 서버 메모리 사용률 상승</span>', '<span class="tri-name">Sample incident D · Rising server memory usage</span>'),
    ('<span class="tri-name">예시 인시던트 B · 백업 작업 실패 재시도</span>', '<span class="tri-name">Sample incident B · Backup job failing and retrying</span>'),
    ('<span class="tri-name">예시 인시던트 A · 배송 추적 데이터 동기화 지연</span>', '<span class="tri-name">Sample incident A · Delivery tracking data sync delay</span>'),
    ('<span class="tri-name">예시 인시던트 C · 접속 권한 요청 증가</span>', '<span class="tri-name">Sample incident C · More access requests</span>'),
    ('이상 점수 0.66 · 막힌 팀 0/5</span>', 'Anomaly score 0.66 · Teams blocked 0/5</span>'),
    ('이상 점수 0.38 · 막힌 팀 1/5</span>', 'Anomaly score 0.38 · Teams blocked 1/5</span>'),
    ('이상 점수 0.42 · 막힌 팀 3/5 · 담당자 없음</span>', 'Anomaly score 0.42 · Teams blocked 3/5 · No owner</span>'),
    ('이상 점수 0.21 · 막힌 팀 0/5</span>', 'Anomaly score 0.21 · Teams blocked 0/5</span>'),
    ('이상 점수는 낮지만, 5개 팀 중 3개 팀의 업무가 막혔고 담당자가 없습니다.', 'The anomaly score is low, but 3 of 5 teams are blocked and no one owns it.'),
    ('</span> 예시 인시던트 A · 즉시 에스컬레이션</p>', '</span> Sample incident A · Escalate now</p>'),
    ('</span> 예시 인시던트 D · 모니터링</p>', '</span> Sample incident D · Monitor</p>'),
    ('</span> 예시 인시던트 B · 추적·기록 필요</p>', '</span> Sample incident B · Track and log</p>'),
    ('</span> 예시 인시던트 C · 기록만</p>', '</span> Sample incident C · Log only</p>'),
    ('<dt>영향받는 팀</dt>', '<dt>Affected teams</dt>'),
    ('<dt>관련 신호</dt>', '<dt>Related signals</dt>'),
    ('<dt>담당자</dt>', '<dt>Owner</dt>'),
    ('<dt>기록</dt>', '<dt>Records</dt>'),
    ('<dd>예시 팀 1 · 예시 팀 2 · 예시 팀 3 (5개 팀 중 3개)</dd>', '<dd>Sample team 1 · Sample team 2 · Sample team 3 (3 of 5 teams)</dd>'),
    ('<dd>이상 점수 0.42 · 이번 주 3회 반복</dd>', '<dd>Anomaly score 0.42 · Recurred 3× this week</dd>'),
    ('<dd>아직 없음 — 담당 팀 지정이 필요합니다</dd>', '<dd>None yet — a responsible team needs to be assigned</dd>'),
    ('<dd>관련 티켓 2건 · 이전 인시던트 1건</dd>', '<dd>2 related tickets · 1 earlier incident</dd>'),
    ('<dd>업무가 막힌 팀 없음</dd>', '<dd>No teams blocked</dd>'),
    ('<dd>이상 점수 0.66 · 메모리 사용률 상승</dd>', '<dd>Anomaly score 0.66 · Memory usage rising</dd>'),
    ('<dd>예시 담당자 1 (SRE)</dd>', '<dd>Sample owner 1 (SRE)</dd>'),
    ('<dd>이전 인시던트 1건</dd>', '<dd>1 earlier incident</dd>'),
    ('<dd>예시 팀 4 (5개 팀 중 1개)</dd>', '<dd>Sample team 4 (1 of 5 teams)</dd>'),
    ('<dd>이상 점수 0.38 · 백업 재시도 2회</dd>', '<dd>Anomaly score 0.38 · 2 backup retries</dd>'),
    ('<dd>예시 담당자 2 (GCC)</dd>', '<dd>Sample owner 2 (GCC)</dd>'),
    ('<dd>관련 티켓 1건</dd>', '<dd>1 related ticket</dd>'),
    ('<dd>이상 점수 0.21 · 요청 수 증가</dd>', '<dd>Anomaly score 0.21 · Request volume rising</dd>'),
    ('<dd>예시 담당자 3 (GCC)</dd>', '<dd>Sample owner 3 (GCC)</dd>'),
    ('<dd>관련 기록 없음</dd>', '<dd>No related records</dd>'),
    ('<strong>1. 여러 알림</strong> 들어온 순서대로 같은 무게로 나열하면, 무엇을 먼저 확인할지 담당자가 직접 판단해야 합니다.',
     '<strong>1. Many alerts</strong> When alerts are listed in the order received, all with equal weight, responders have to work out for themselves what to check first.'),
    ('<strong>2. 우선 대응을 위로</strong> 이상 점수가 낮아도 여러 팀의 업무가 막히고 담당자가 없으면 P1로 올립니다. 이 이동은 원리를 보여 주는 시연이며, 실제 화면은 처음부터 이 순서로 열립니다.',
     '<strong>2. Priority to the top</strong> Even with a low anomaly score, an incident becomes P1 when several teams are blocked and no one owns it. This movement only demonstrates the principle; the real screen opens in this order from the start.'),
    ('<strong>3. 클릭 후 조사</strong> 항목을 고르면 영향받는 팀·관련 신호·담당자·기록을 한곳에서 확인합니다. 다른 항목을 눌러 비교할 수 있습니다.',
     '<strong>3. Click to investigate</strong> Selecting an item shows affected teams, related signals, owner, and records in one place. Select another item to compare.'),
    # 사례 02 데모 B: 과거 기록 기반 AI 예측 요약
    ('<h3 class="demo-title">과거의 기록에서, 다음에 주의할 신호를.</h3>', '<h3 class="demo-title">From past records, the signals to watch next.</h3>'),
    ('AI가 프로젝트에서 연결한 과거 기록의 반복 패턴을 찾고, 앞으로 생길 수 있는 위험을 목록 위 요약에서 먼저 알려 줍니다.',
     'AI finds recurring patterns in the past records connected for the project, and the summary above the list flags risks that may come next.'),
    ('</span>관련 기록 수집</button>', '</span>Gather related records</button>'),
    ('</span>패턴 분석</button>', '</span>Find the pattern</button>'),
    ('</span>예측 요약</button>', '</span>Forecast summary</button>'),
    ('aria-label="재구성한 AI 예측 요약 화면"', 'aria-label="Recreated AI forecast summary screen"'),
    ('<span class="ui-title">예시 서비스 X · 운영 기록</span><span class="ui-sub">분석 범위: 프로젝트에서 연결한 관련 기록</span>',
     '<span class="ui-title">Sample service X · Operations records</span><span class="ui-sub">Scope: related records connected for the project</span>'),
    ('id="fc-summary-title">AI 요약</p>', 'id="fc-summary-title">AI summary</p>'),
    ('<dt><span class="fc-kind">관찰</span>반복 패턴</dt>', '<dt><span class="fc-kind">Observed</span>Recurring pattern</dt>'),
    ('<dd>예시 서비스 X에서 처리 지연 경고 뒤에 데이터 반영 관련 티켓과 동기화 지연 인시던트가 두 번 이어졌습니다.</dd>',
     '<dd>In sample service X, processing delay alerts were followed by data update tickets and sync delay incidents, twice.</dd>'),
    ('<dt><span class="fc-kind fc-kind-pred">예측</span>앞으로 생길 수 있는 위험</dt>', '<dt><span class="fc-kind fc-kind-pred">Forecast</span>Risk that may follow</dt>'),
    ('<dd>같은 경고가 다시 나타나면, 이 흐름이 이어져 후속 업무에 영향을 줄 가능성이 있습니다.</dd>',
     '<dd>If the same alert appears again, this sequence may continue and could affect downstream work.</dd>'),
    ('<dt><span class="fc-kind">근거</span>관련 기록 확인</dt>', '<dt><span class="fc-kind">Evidence</span>Check related records</dt>'),
    ('aria-controls="fc-evidence">관련 기록 보기</button>', 'aria-controls="fc-evidence">View related records</button>'),
    ('<p>이 요약의 근거가 된 예시 기록입니다. 아래 표에도 같은 줄을 표시했습니다.</p>', '<p>These sample records support the summary. The same rows are marked in the table below.</p>'),
    ('<li>운영 데이터 D-01 처리 지연 경고 → 티켓 T-01 데이터 반영 지연 문의 → 인시던트 이력 E 동기화 지연</li>',
     '<li>Operations data D-01 processing delay alert → Ticket T-01 data update delay question → Incident history E sync delay</li>'),
    ('<li>운영 데이터 D-03 처리 지연 경고 → 티켓 T-03 보고서 누락 문의 → 인시던트 이력 G 동기화 지연</li>',
     '<li>Operations data D-03 processing delay alert → Ticket T-03 missing report question → Incident history G sync delay</li>'),
    ('예측은 가능성이며 확정된 결과가 아닙니다. 대응 여부는 담당자가 근거를 확인한 뒤 판단합니다.',
     'A forecast is a possibility, not a confirmed outcome. Responders review the evidence and decide whether to act.'),
    ('<caption class="sr-only">예시 관련 기록</caption>', '<caption class="sr-only">Sample related records</caption>'),
    ('<th scope="col">과거 운영 데이터</th><th scope="col">관련 티켓</th><th scope="col">인시던트 이력</th>',
     '<th scope="col">Past operations data</th><th scope="col">Related tickets</th><th scope="col">Incident history</th>'),
    ('<td>D-01 처리 지연 경고</td><td>T-01 데이터 반영 지연 문의</td><td>E 동기화 지연</td>', '<td>D-01 Processing delay alert</td><td>T-01 Data update delay question</td><td>E Sync delay</td>'),
    ('<td>D-02 디스크 사용량 경고</td><td>T-02 접속 권한 요청</td><td>F 인증서 갱신</td>', '<td>D-02 Disk usage alert</td><td>T-02 Access request</td><td>F Certificate renewal</td>'),
    ('<td>D-03 처리 지연 경고</td><td>T-03 보고서 누락 문의</td><td>G 동기화 지연</td>', '<td>D-03 Processing delay alert</td><td>T-03 Missing report question</td><td>G Sync delay</td>'),
    ('<span class="fc-kind">공통점</span>처리 지연 경고 → 데이터 반영 관련 티켓 → 동기화 지연이 같은 순서로 두 번 반복됐습니다.',
     '<span class="fc-kind">In common</span>Processing delay alert → data update ticket → sync delay recurred twice in the same order.'),
    ('<strong>1. 관련 기록 수집</strong> 프로젝트에서 연결한 과거 운영 데이터·관련 티켓·인시던트 이력을 한곳에 모읍니다.',
     '<strong>1. Gather related records</strong> Past operations data, related tickets, and incident history connected for the project are brought together.'),
    ('<strong>2. 패턴 분석</strong> 기록 사이의 공통점을 찾아, 같은 순서로 반복된 흐름을 표시합니다.',
     '<strong>2. Find the pattern</strong> What the records have in common is found, and sequences that recurred in the same order are marked.'),
    ('<strong>3. 예측 요약</strong> 분석 결과를 기록 목록 위 AI 요약에서 먼저 보여 줍니다. 관찰된 패턴과 예측을 나누고, ‘관련 기록 보기’로 근거를 확인합니다.',
     '<strong>3. Forecast summary</strong> The AI summary above the records shows the result first. It separates the observed pattern from the forecast, and “View related records” shows the evidence.'),
    # 2026-10-29 사진·비주얼 재구성
]

STEPS = [
    ('시장과 사용 맥락 이해하기', 'Understand the market and context of use'),
    ('제품 경험과 현지화 가정 점검하기', 'Review the product experience and localization assumptions'),
    ('개선 방향과 우선순위 합의하기', 'Agree on direction and priorities'),
    ('현지 맥락에 맞는 경험 설계하기', 'Design for the local context'),
    ('실행 계획과 개발 연결하기', 'Plan execution and connect to development'),
    ('검증하고 다음 개선으로 이어가기', 'Validate and carry into the next iteration'),
]
APPROACH = [
    ('<title>협업 방식 — Second Context</title>', '<title>Approach — Second Context</title>'),
    ('Second Context의 6단계 접근: 시장과 사용 맥락 이해부터 설계, 개발 연결, 검증까지.',
     'Second Context’s six-step approach: from understanding the market and context of use to design, development handoff, and validation.'),
    ('모든 협업은 제품의 목표 시장과 사용자, 그리고 현재 팀이 해결해야 할 문제를 이해하는 데서 시작합니다. 현지 사용자의 업무 방식과 기대를 살펴보고, 발견한 차이를 개선 우선순위와 구체적인 디자인으로 연결합니다.',
     'Every engagement starts with understanding your product’s target market and users, and the problems your team needs to solve now. We look at how local users work and what they expect, then turn the gaps we find into improvement priorities and concrete design.'),
    ('Second Context의 6단계 접근은 시장에 대한 가정을 확인하고, 팀이 실행할 수 있는 결과물로 구체화합니다.',
     'Second Context’s six-step approach tests assumptions about the market and turns them into outcomes your team can act on.'),
    ('단계별 설명, 산출물과 기대 효과', 'Step-by-step description, deliverables, and expected outcomes'),
    ('6단계 접근', 'Six-step approach'),
    # 2026-10-29 사진·비주얼 재구성
    ('<h1>맥락을 이해하고, 실행 가능한 다음 단계를 만듭니다.</h1>', '<h1>Understand the context. Create next steps your team can act on.</h1>'),
    ('유리벽에 손으로 그린 화면 흐름을 설명하는 사람과 이를 지켜보는 동료 세 명', 'A person explaining a hand-drawn screen flow on a glass wall as three colleagues look on'),
    ('홈에서 소개한 네 단계(맥락 이해 → 문제 정의 → 디자인 및 검증 → 실행 지원)를 실제 진행 순서대로 나눈 여섯 단계입니다. 1·2단계는 맥락 이해, 3단계는 문제 정의, 4단계는 디자인 및 검증, 5단계는 실행 지원이고, 6단계는 출시 뒤 검증과 다음 개선입니다. 각 단계의 산출물이 다음 단계의 판단 근거가 되며, 단계를 누르면 자세한 설명으로 이동합니다.',
     'These six steps break the four steps on the home page (Understand context → Define the problem → Design and validate → Support delivery) into the order we actually work in. Steps 1–2 cover context, step 3 defines the problem, step 4 is design and validation, step 5 supports delivery, and step 6 validates after launch and sets up the next improvement. Each step’s deliverable informs the decisions in the next. Select a step to jump to its details.'),
    ('<span class="pr-out-k">산출물</span>', '<span class="pr-out-k">Deliverable</span>'),
    ('06단계의 검증 결과는 다음 개선 과제로 이어집니다.', 'Validation results from step 06 feed the next round of improvements.'),
    ('<h2 id="priority-title">먼저 해결할 문제와 판단 기준을 함께 정합니다.</h2>', '<h2 id="priority-title">We agree together on what to solve first, and how to decide.</h2>'),
    ('고칠 것이 많아 보일수록 기준이 필요합니다. 사용자 영향, 사업 중요도, 구현 난이도를 기준으로 먼저 해결할 문제와 목표를 정하고, 팀의 시간과 자원을 어디에 모을지 합의합니다.', 'The more there seems to fix, the more you need clear criteria. Using user impact, business importance, and implementation effort, we choose which problems and goals come first and agree where to focus the team’s time and resources.'),
    ('테이블 위에 펼친 화면 스케치를 네 사람이 함께 살펴보는 장면', 'Four people looking over screen sketches spread out on a table'),
    ('<span class="vis-title">우선순위 매트릭스</span>', '<span class="vis-title">Prioritization matrix</span>'),
    ('<span>영향 큼</span><span>영향 작음</span>', '<span>High impact</span><span>Low impact</span>'),
    ('<span>구현 쉬움</span><span>구현 어려움</span>', '<span>Easy to build</span><span>Hard to build</span>'),
    ('<p class="mx-name">먼저 해결</p><p class="mx-desc">영향 큼 · 구현 쉬움</p>', '<p class="mx-name">Do first</p><p class="mx-desc">High impact · Easy to build</p>'),
    ('<p class="mx-name">계획해서 진행</p><p class="mx-desc">영향 큼 · 구현 어려움</p>', '<p class="mx-name">Plan and schedule</p><p class="mx-desc">High impact · Hard to build</p>'),
    ('<p class="mx-name">여유 있을 때</p><p class="mx-desc">영향 작음 · 구현 쉬움</p>', '<p class="mx-name">When there’s time</p><p class="mx-desc">Low impact · Easy to build</p>'),
    ('<p class="mx-name">다시 검토</p><p class="mx-desc">영향 작음 · 구현 어려움</p>', '<p class="mx-name">Revisit</p><p class="mx-desc">Low impact · Hard to build</p>'),
    ('<li>A 첫 화면 가치 설명</li>', '<li>A Explain value on the first screen</li>'),
    ('<li>B 버튼 문구 정리</li>', '<li>B Clarify button labels</li>'),
    ('<li>C 승인 흐름 재설계</li>', '<li>C Redesign the approval flow</li>'),
    ('<li>D 아이콘 정리</li>', '<li>D Tidy up icons</li>'),
    ('<li>E 대시보드 전면 개편</li>', '<li>E Full dashboard overhaul</li>'),
] + STEPS + [(f'{i}단계: ', f'Step {i}: ') for i in range(1, 7)] + [
    ('목표 시장, 핵심 사용자, 업무 환경과 사업 목표를 함께 정리합니다.',
     'Together we define the target market, core users, work environment, and business goals.'),
    ('온보딩, 핵심 업무 흐름, 탐색 구조와 화면 문구를 검토하고 현지 사용자 관점에서 확인할 가정을 찾습니다.',
     'We review onboarding, core workflows, navigation, and UI copy, and identify the assumptions to test from a local user’s perspective.'),
    ('사용자 영향, 사업 중요도, 구현 난이도를 기준으로 먼저 해결할 문제와 목표를 정합니다.',
     'We decide which problems and goals to tackle first, based on user impact, business importance, and implementation effort.'),
    ('합의한 핵심 문제를 중심으로 사용자 흐름, 정보 구조, 화면과 문구를 설계합니다.',
     'Focusing on the agreed core problems, we design user flows, information architecture, screens, and copy.'),
    ('디자인 의도, 요구사항, 고려할 예외 상황과 다음 작업을 정리해 개발 협업으로 연결합니다.',
     'We document design intent, requirements, edge cases to consider, and next tasks, and carry them into development.'),
    ('합의된 범위에서 사용자 피드백이나 사용 데이터를 검토하고 후속 개선 과제를 정리합니다.',
     'Within the agreed scope, we review user feedback or usage data and define follow-up improvements.'),
    ('<dt>산출물</dt>', '<dt>Deliverable</dt>'),
    ('<dt>기대 효과</dt>', '<dt>Expected outcome</dt>'),
    ('시장·사용 맥락 브리프', 'Market and context-of-use brief'),
    ('검토할 문제와 협업 범위 명확화', 'Clarity on the problems to review and the scope of collaboration'),
    ('UX 진단 및 현지화 가정 목록', 'UX review and list of localization assumptions'),
    ('제품 경험의 마찰과 검증 과제 파악', 'Friction in the product experience and items to validate, identified'),
    ('우선순위 매트릭스 및 디자인 방향', 'Priority matrix and design direction'),
    ('팀의 시간과 자원을 집중할 기준 마련', 'Clear criteria for where to focus your team’s time and resources'),
    ('개선 사용자 흐름 및 합의 범위의 디자인·프로토타입', 'Improved user flows, plus designs and prototypes within the agreed scope'),
    ('제품 방향을 구체적인 경험으로 확인', 'Product direction confirmed as a concrete experience'),
    ('디자인 전달 자료 및 실행 계획', 'Design handoff materials and an execution plan'),
    ('구현 과정의 불확실성과 해석 차이 감소', 'Less uncertainty and fewer misinterpretations during implementation'),
    ('검증 결과 및 후속 개선 백로그', 'Validation results and a follow-up improvement backlog'),
    ('근거를 바탕으로 한 다음 제품 의사결정 지원', 'Evidence-based support for your next product decisions'),
    ('전체 과정과 제공물은 협업 범위에 따라 달라집니다. 짧은 상담이나 UX 진단은 필요한 단계에 집중하며, 사용자 리서치·프로토타입·개발 지원·후속 검증은 별도 합의된 범위에서 진행합니다.',
     'The overall process and deliverables depend on the scope of the engagement. Short consultations and UX reviews focus on the steps you need; user research, prototyping, development support, and follow-up validation are carried out within a separately agreed scope.'),
    ('팀의 판단과 실행을 돕는 제품 디자인.', 'Product design that supports your team’s decisions and execution.'),
    ('명확한 개선 우선순위', 'Clear improvement priorities'),
    ('먼저 해결할 문제와 그 이유를 정리합니다.', 'We define which problems to solve first, and why.'),
    ('현지 사용자에 대한 이해', 'Understanding of local users'),
    ('사용자의 기대와 실제 업무 맥락을 제품 판단에 반영합니다.', 'We bring users’ expectations and real work context into product decisions.'),
    ('원활한 디자인·개발 협업', 'Smooth design and development collaboration'),
    ('합의한 방향을 구현 가능한 요구사항과 디자인으로 연결합니다.', 'We turn the agreed direction into buildable requirements and designs.'),
    ('검증을 통한 지속적인 개선', 'Continuous improvement through validation'),
    ('피드백과 사용 근거를 다음 개선 과제로 이어갑니다.', 'We carry feedback and usage evidence into the next round of improvements.'),
]

CONTACT = [
    ('<title>문의 — Second Context</title>', '<title>Contact — Second Context</title>'),
    ('Second Context에 프로젝트를 문의하거나 30분 상담을 예약하세요.',
     'Send Second Context a project inquiry or book a 30-minute consultation.'),
    ('<p class="lead">제품과 현재 고민을 간단히 알려주세요. 범위가 정해지지 않았어도 괜찮습니다.</p>',
     '<p class="lead">Tell us briefly about your product and what you’re working through. It’s fine if the scope isn’t defined yet.</p>'),
    ('<h2 id="inquiry-title">문의 보내기</h2>', '<h2 id="inquiry-title">Send an inquiry</h2>'),
    ('</span> 필수 항목</p>', '</span> Required</p>'),
    ('value="Second Context 웹사이트 문의"', 'value="Second Context website inquiry"'),
    ('value="한국어 페이지"', 'value="English page"'),
    ('<label for="f-name">이름 ', '<label for="f-name">Name '),
    ('placeholder="예: 홍길동"', 'placeholder="e.g., Alex Kim"'),
    ('<label for="f-email">이메일 ', '<label for="f-email">Email '),
    ('<label for="f-company">회사 또는 제품명</label>', '<label for="f-company">Company or product name</label>'),
    ('placeholder="회사명 또는 제품명"', 'placeholder="Company or product name"'),
    ('<label for="f-url">제품 URL</label>', '<label for="f-url">Product URL</label>'),
    ('<label for="f-message">문의 내용 ', '<label for="f-message">Message '),
    ('placeholder="제품 소개, 현재 어려운 점, 필요한 도움을 간단히 알려주세요."',
     'placeholder="Briefly describe your product, what’s difficult right now, and the help you need."'),
    ('>문의 보내기</button>', '>Send inquiry</button>'),
    ('aria-labelledby="other-ways">', 'aria-labelledby="other-ways">'),
    ('<h2 class="label" id="other-ways">다른 연락 방법</h2>', '<h2 class="label" id="other-ways">Other ways to reach us</h2>'),
    ('<p class="way-title">이메일</p>', '<p class="way-title">Email</p>'),
    ('>이메일 주소 복사</button>', '>Copy email</button>'),
    ('이메일 주소 (선택해서 복사)', 'Email address (select to copy)'),
    ('<p class="way-title">30분 상담</p>', '<p class="way-title">30-minute call</p>'),
    ('대화로 먼저 이야기 나누고 싶다면 예약해 주세요.', 'Prefer to talk first? Book a time.'),
    ('30분 상담 예약<span class="sr-only"> (새 탭에서 열림)</span></a>\n          </div>',
     'Book a 30-minute consultation<span class="sr-only"> (새 탭에서 열림)</span></a>\n          </div>'),
    # 2026-10-29 사진·비주얼 재구성
    ('<h1>지금 고민 중인 제품 이야기를 들려주세요.</h1>', '<h1>Tell us about the product challenge on your mind.</h1>'),
]

ABOUT = [
    # 2026-11-10: 창업자 소개를 다시 별도 About 페이지로 (홈 About 섹션의 '소개 자세히 보기'에서 연결)
    ('헬스케어 제품, 엔터프라이즈 소프트웨어, 복잡한 업무 흐름을 설계해 온 Rachel Cho와 Second Context 소개.',
     'About Second Context and Rachel Cho, who designs healthcare products, enterprise software, and complex workflows.'),
    ('Second Context를 이끄는 제품·UX 컨설턴트 Rachel Cho입니다. Y Combinator 출신으로 <span class="nowrap">1,420만 달러</span>의 투자를 유치한 미국 헬스케어 스타트업에서 파운딩 디자이너로 제품 디자인을 이끌었습니다. 글로벌 기업의 업무 시스템과 제품 현지화 경험을 바탕으로, 복잡한 문제를 진단하고 개선 우선순위부터 실제 설계까지 연결합니다.', 'I’m Rachel Cho, the product and UX consultant who leads Second Context. I led product design as a founding designer at a U.S. healthcare startup from Y Combinator that raised <span class="nowrap">$14.2 million</span>. Drawing on my experience with enterprise systems and product localization for global companies, I diagnose complex problems and connect them to clear priorities and real, working design.'),
    ('직접 학비를 마련하며 공부하고, 이민자로 새로운 언어와 문화 속에서 커리어를 쌓았습니다. 디지털 노매드로 여러 나라를 여행하며 서로 다른 배경과 관점을 이해해온 경험은, 제품이 쓰이는 맥락과 그 안의 사람을 살피는 바탕이 되었습니다.', 'I funded my own education and built my career as an immigrant, navigating a new language and culture. Traveling as a digital nomad taught me to understand different backgrounds and perspectives—and it shapes how I look at the context a product is used in, and the people within it.'),
    ('지금은 제품팀과 파운더의 고민을 함께 풀며, 이민자 커뮤니티와 주니어 디자이너의 새로운 출발도 돕고 있습니다. ADPList 멘토링과 Flexwork Pro의 UX·AI 제품 디자인 강의를 통해 경험을 나누고, 막막한 상황에서도 실행 가능한 다음 걸음을 함께 찾습니다.', 'Today, I work through challenges with product teams and founders, and help immigrant communities and junior designers make a fresh start. Through mentoring on ADPList and teaching UX and AI product design at Flexwork Pro, I share what I’ve learned and help people find a practical next step, even when the way forward feels unclear.'),
    ('헬스케어, 엔터프라이즈, 복잡한 업무 흐름.', 'Healthcare, enterprise, and complex workflows.'),
    ('회사 이름은 밝히지 않고, 회사의 배경과 Rachel이 맡은 역할을 적었습니다.', 'Company names are not disclosed. Each entry describes the company’s background and Rachel’s role.'),
    ('Toptal을 통해 글로벌 기업들과 협업', 'Collaborating with global companies through Toptal'),
    ('제품·UX 디자인 컨설팅', 'Product and UX design consulting'),
    ('Y Combinator W21 출신 미국 홈헬스케어 스타트업', 'A Y Combinator W21 U.S. home healthcare startup'),
    ('파운딩 디자이너로 AI 일정 플랫폼의 제품 디자인을 이끌고, 회사의 첫 디자인 시스템을 만들었습니다.', 'Led product design for the AI scheduling platform as founding designer and built the company’s first design system.'),
    ('LA의 물류 SaaS 기업', 'A logistics SaaS company in Los Angeles'),
    ('파운딩 디자이너로 글로벌 디스플레이 제조사를 위한 선박 추적 대시보드와 React 디자인 시스템을 설계했습니다.', 'As founding designer, designed a vessel tracking dashboard for a global display manufacturer and a React design system.'),
    ('백신 운영을 지원하는 글로벌 제약사의 모니터링 플랫폼', 'A global pharmaceutical company’s monitoring platform supporting vaccine operations'),
    ('UX 디자인 에이전시를 통한 계약 Senior Product Designer로 AI 기반 인시던트 관리 경험을 설계했습니다.', 'Designed an AI-powered incident management experience as a contract Senior Product Designer through a UX design agency.'),
    ('미국의 글로벌 게임 기업', 'A global gaming company in the U.S.'),
    ('호주 본사와 협업하며 글로벌 애플리케이션을 디자인했습니다.', 'Designed global applications in collaboration with the Australian headquarters.'),
    ('글로벌 테크 기업의 한국어 제품', 'A global tech company’s Korean product'),
    ('영국 제작 에이전시, 고객사의 한국·미국 팀과 6주 동안 UX 문구와 디자인 자산을 현지화했습니다.', 'Localized UX copy and design assets over six weeks with a U.K. production agency and the client’s Korea and U.S. teams.'),
    ('그린피스, University of Florida, Diversity Way Maker, Walmart 등', 'Greenpeace, University of Florida, Diversity Way Maker, Walmart, and others'),
    ('글로벌 기업·기관과 함께 일했습니다.', 'Worked with global companies and organizations.'),
    ('경험을 나누고, 다음 걸음을 함께 찾습니다.', 'Sharing experience, finding the next step together.'),
    ('<p class="row-what">ADPList 멘토</p>', '<p class="row-what">ADPList mentor</p>'),
    ('40명 이상의 디자이너와 커리어 멘토링', 'Career mentoring with more than 40 designers'),
    ('Flexwork Pro UX 커리어 세미나', 'Flexwork Pro UX career seminar'),
    ('150명 이상 신청, 약 60명 참석', 'More than 150 sign-ups, about 60 attendees'),
    ('Flexwork Pro AI 제품 디자인 과정 강사', 'Instructor, Flexwork Pro AI product design course'),
    ('UX·AI 제품 디자인 강의', 'Teaching UX and AI product design'),
    ('멘토링은 디자인 커리어에 관한 것이며, 이민 관련 법률 자문은 제공하지 않습니다.', 'Mentoring covers design careers. It does not include immigration or legal advice.'),
    ('노트북 앞에서 상대의 이야기를 들으며 대화하는 두 사람', 'Two people in conversation at a laptop, one listening closely to the other'),
]


# 2026-11-16 홈 What we do(이전 Services + Selected Work 통합)
HOME += [
    ('복잡한 제품을, 바로 이해되는 경험으로.', 'Complex products, made into experiences people understand at a glance.'),
    ('세 가지 역량으로 제품의 다음 단계를 함께 만듭니다. 각 역량 아래의 사례는 Second Context를 시작하기 전, Rachel Cho가 이전 경력에서 수행한 프로젝트입니다. 고객사 이름은 밝히지 않습니다.',
     'We shape your product’s next step through three capabilities. The case studies under each one are projects Rachel Cho delivered in previous roles, before starting Second Context. Client names are not disclosed.'),
    ('여러 규칙과 정보, 역할이 얽힌 제품에서 사용자가 무엇을 먼저 판단하고 실행해야 하는지 정리합니다. 실제 업무 흐름을 이해하고, 우선순위와 예외 상황을 명확한 화면과 흐름으로 연결합니다.',
     'In products where rules, information, and roles are tangled together, we clarify what people need to decide and do first. We learn how the work actually flows, then turn priorities and exceptions into clear screens and flows.'),
    ('처음 시작하는 순간부터 인증과 예외 상황까지, 사용자가 현재 상태와 다음 행동을 이해할 수 있도록 설계합니다. 상황에 따라 달라지는 흐름을 정리하고, 막히는 순간에도 다음 단계로 이어지는 경험을 만듭니다.',
     'From the first moment through verification and edge cases, we design so people understand where they stand and what to do next. We untangle flows that change with circumstances and build experiences that lead to the next step, even when something goes wrong.'),
    ('언어를 바꾸는 것을 넘어, 사람들이 제품을 이해하고 사용하는 방식을 살펴봅니다. 목표 시장의 언어와 문화, 사용 환경에 맞춰 제품의 표현과 화면 구성을 조정합니다.',
     'Beyond changing the language, we look at how people understand and use a product, then adapt its wording and screen layout to the language, culture, and context of use in your target market.'),
]

# 2026-11-16 사례 목록(second-context-work.html): 이전 주소를 유지하며 네 사례 페이지로 연결
WORK_INDEX = [
    ('<h1 id="work-title">다섯 프로젝트로 보는 설계 판단</h1>', '<h1 id="work-title">Design decisions, in five projects</h1>'),
    ('Rachel Cho가 이전 경력에서 수행한 다섯 프로젝트의 사례 목록. 사례마다 문제, 역할, 핵심 설계 판단과 결과를 소개합니다.',
     'Case studies from five projects Rachel Cho delivered in previous roles, each covering the problem, role, key design decisions, and results.'),
    ('// 이전 사례 주소(second-context-work.html#case-…)는 각 사례 페이지로 옮긴다 (2026-11-16)', '// Old case URLs (second-context-work.html#case-…) move to each case page (2026-11-16)'),
]

# 2026-11-16 사례 상세 네 페이지 공통 번역 (페이지에 있는 문구만 적용, 표에 없는 한국어가 남으면 빌드가 멈춘다)
CASE_PAGES = [
    ('Rachel Cho의 이전 경력에서 수행한 프로젝트입니다. 공개 가능한 범위의 경험을 소개하며, 화면과 데이터는 설명을 위해 새롭게 구성한 예시입니다.', 'A project Rachel Cho delivered in a previous role. It covers only what can be shared publicly; screens and data are new examples created for illustration.'),
    ('헬스케어 SaaS', 'Healthcare SaaS'),
    ('복잡한 방문 일정을 명확한 다음 단계로', 'Turning complex visit scheduling into clear next steps'),
    ('엔터프라이즈 운영', 'Enterprise operations'),
    ('많은 신호 속에서 먼저 대응할 문제 찾기', 'Finding the issue to handle first among many signals'),
    ('규제 산업 모바일 앱', 'Regulated mobile app'),
    ('상황이 달라도 이어지는 본인 인증 경험', 'Identity verification that keeps moving, whatever happens'),
    ('제품 현지화', 'Product localization'),
    ('언어와 사용 맥락에 맞춘 제품 경험', 'A product experience fitted to language and context of use'),
    ('복잡한 업무를 명확한 제품으로', 'From complex work to a clear product'),
    ('시작부터 신뢰할 수 있는 경험으로', 'An experience people can trust from the start'),
    ('시장과 사용 맥락에 맞는 경험으로', 'An experience fitted to the market and its context'),
    ('이전 경력 프로젝트', 'Previous-role project'),
    ('사용자 평가', 'User rating'),
    ('업무 성과', 'Work outcome'),
    ('도입 범위', 'Adoption scope'),
    ('리서치 범위', 'Research scope'),
    ('프로젝트 기간', 'Project length'),
    ('사용 지표', 'Usage metric'),
    ('운영 지표', 'Operations metric'),
    ('측정·보고된 결과', 'Measured and reported results'),
    ('배운 점', 'What I learned'),
    ('바뀐 화면과 흐름', 'Screens and flows that changed'),
    ('확인된 산출물', 'Confirmed deliverables'),
    ('사용 맥락과 과제', 'Context and challenge'),
    ('Rachel의 역할', 'Rachel’s role'),
    ('공개 가능한 협업 범위', 'Collaboration (public scope)'),
    ('프로젝트 성격', 'Project type'),
    ('설계 설명을 위한 재구성 · 예시 문구', 'Recreated for illustration · Sample copy'),
    ('Healthcare Scheduling — Second Context', 'Healthcare Scheduling — Second Context'),
    ('미국 홈헬스케어 SaaS의 방문 일정 관리를 예약 가능한 날짜, 명확한 상태, 확인할 수 있는 AI 추천으로 바꾼 사례.', 'How visit scheduling for a U.S. home healthcare SaaS was turned into bookable dates, clear status, and AI recommendations people can check.'),
    ('복잡한 방문 일정을, <span class="tl">바로 판단할 수 있는 다음 단계로.</span>', 'Complex visit scheduling, turned into a next step you can decide on.'),
    ('미국 홈헬스케어 SaaS에서 자격·방문 빈도·인력 규칙이 겹친 일정 관리를, 예약 가능한 날짜와 명확한 상태, 사람이 확인하고 조정할 수 있는 AI 추천으로 바꿨습니다.', 'At a U.S. home healthcare SaaS, scheduling tangled in eligibility, visit-frequency, and staffing rules became bookable dates, clear status, and AI recommendations people can check and adjust.'),
    ('<span class="cs-hero-num">5.8 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 8.2</span>', '<span class="cs-hero-num">5.8 <span aria-hidden="true">→</span><span class="sr-only"> to </span> 8.2</span>'),
    ('파일럿에서 측정한 일정 계획 자신감', 'Confidence in planning schedules, measured in the pilot'),
    ('<span class="cs-hero-num">180초 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 60초</span>', '<span class="cs-hero-num">180 sec <span aria-hidden="true">→</span><span class="sr-only"> to </span> 60 sec</span>'),
    ('여러 개선을 함께 적용한 뒤의 작업 시간', 'Task time after several improvements together'),
    ('<span class="cs-hero-num">3,000명+</span>', '<span class="cs-hero-num">3,000+</span>'),
    ('AI 일정 추천을 사용하는 임상의', 'Clinicians using AI scheduling recommendations'),
    ('밝은 병원 복도를 따라 장비를 밀며 걸어가는 파란 수술복 차림의 의료진 뒷모습', 'A clinician in blue scrubs, seen from behind, wheeling equipment down a bright hospital corridor'),
    ('미국 홈헬스케어 운영팀이 임상의 방문 일정을 조정하는 AI 일정 관리 플랫폼입니다. 일정 담당자는 환자 자격·방문 빈도·인력 가용성을 함께 고려해야 했고, 이 과정에서 반복 문의와 혼란이 발생했습니다.', 'An AI scheduling platform that U.S. home healthcare operations teams use to coordinate clinician visits. Schedulers had to weigh patient eligibility, visit frequency, and staff availability together, which led to repeated questions and confusion.'),
    ('파운딩 디자이너(Senior Product Designer)로 참여했습니다.', 'Joined as the founding designer (Senior Product Designer).'),
    ('CEO와 함께 핵심 AI 일정 플랫폼의 제품 디자인 비전과 전략을 정의하고, 비즈니스 목표를 0→1 단계의 엔드투엔드 디자인 방향으로 옮겼습니다.', 'Defined the product design vision and strategy for the core AI scheduling platform with the CEO, translating business goals into end-to-end design direction from 0 to 1.'),
    ('CTO, 프런트엔드 엔지니어 6명과 함께 회사의 첫 Figma 디자인 시스템을 만들었습니다.', 'Built the company’s first Figma design system with the CTO and 6 front-end engineers.'),
    ('CEO·CTO·프런트엔드 엔지니어와 함께 일했고, 디자인·제품·엔지니어링이 함께 쓰는 회사의 첫 엔드투엔드 디자인 프로세스를 만들었습니다.', 'Worked with the CEO, CTO, and front-end engineers, and established the company’s first end-to-end design process shared by design, product, and engineering.'),
    ('이전 경력 프로젝트 · 미국 홈헬스케어 스타트업 · 2025–2026', 'Previous-role project · U.S. home healthcare startup · 2025–2026'),
    ('일정 담당자는 겹친 규칙을 머릿속으로 맞춰 보느라, 어떤 날짜에 방문을 잡을 수 있는지 바로 판단하기 어려웠습니다.', 'Schedulers had to reconcile overlapping rules in their heads, so it was hard to tell right away which dates a visit could be booked on.'),
    ('규칙을 설명하기 전에 예약 가능한 날짜와 상태를 보여 주고, 제한 이유는 문장으로, AI 추천은 확인하고 조정할 수 있는 다음 행동으로 제시했습니다.', 'Bookable dates and status come first, reasons for limits are written as sentences, and AI recommendations appear as a next step people can confirm or adjust.'),
    ('규칙보다, 예약 가능한 날짜를 먼저.', 'Bookable dates before rules.'),
    ('자격·방문 빈도·인력 가용성 규칙이 겹쳐 반복 문의와 혼란이 생겼기 때문에, 규칙을 설명하는 대신 예약 가능한 날짜와 상태를 먼저 보여주도록 했습니다.', 'Because overlapping eligibility, visit-frequency, and availability rules caused repeated questions and confusion, the design shows bookable dates and status first instead of explaining the rules.'),
    ('규칙을 외우지 않아도, 달력에서 지금 고를 수 있는 날짜가 보입니다.', 'Without memorizing rules, people can see on the calendar which dates they can choose now.'),
    ('내부 코드 대신, 이해할 수 있는 문장으로.', 'Plain sentences instead of internal codes.'),
    ('내부 코드는 사용자가 이해할 수 있는 문구로 바꿨습니다. 제한된 날짜를 고르면 무엇 때문에 막혔는지와 함께 다음에 할 일을 알려 줍니다.', 'Internal codes were replaced with wording users could understand. Choosing a blocked date explains what is blocking it and what to do next.'),
    ('담당자에게 다시 묻지 않고도 제한 이유를 이해합니다.', 'People understand why a date is blocked without having to ask someone.'),
    ('이전 방식', 'Before'),
    ('코드의 뜻을 알아야 다음 행동을 정할 수 있습니다.', 'You need to know what the code means to decide what to do next.'),
    ('바꾼 방식', 'After'),
    ('10일은 예약할 수 없습니다', 'The 10th can’t be booked'),
    ('이번 주 방문 횟수(2회)를 이미 모두 사용했습니다.', 'This week’s visit limit (2 visits) has already been used.'),
    ('가능한 날짜 보기', 'See available dates'),
    ('AI 추천은, 확인하고 조정할 수 있게.', 'AI recommendations people can check and adjust.'),
    ('의사결정 속도와 확신을 함께 높이기 위해, AI가 만든 일정 추천을 어떻게 보여주고 검증하고 조정할지 정의했습니다.', 'To improve both decision speed and confidence, defined how AI-generated schedule recommendations are surfaced, validated, and adjusted.'),
    ('추천을 그대로 따르거나 다른 시간으로 바꾸는 결정을 사람이 내립니다.', 'A person makes the call: accept the recommendation or switch to another time.'),
    ('재구성한 방문 일정·임상의 추천 화면', 'Recreated visit scheduling and clinician recommendation screen'),
    ('방문 목록에서 배정이 필요한 방문을 고르면, 자격·거리·언어·환자 선호·업무량 조건을 함께 본 추천 임상의와 그 이유를 보여 줍니다.', 'Choosing a visit that needs a clinician shows a recommendation that weighs license, distance, language, patient preference, and caseload together, with the reason.'),
    ('원본 프로젝트 화면 구조를 바탕으로 다시 구성한 화이트라벨 화면 · 예시 데이터', 'White-label screens recreated from the original project’s structure · Sample data'),
    ('모니터 화면을 가리키며 함께 검토하는 팀', 'A team reviewing a monitor together, one person pointing at the screen'),
    ('포스트잇과 함께 종이에 화면 흐름 스케치를 그리는 손', 'A hand sketching screen-flow wireframes on paper among sticky notes'),
    ('<span class="cs-metric-value">5.8 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 8.2</span>', '<span class="cs-metric-value">5.8 <span aria-hidden="true">→</span><span class="sr-only"> to </span> 8.2</span>'),
    ('<span class="cs-metric-value">180초 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 60초</span>', '<span class="cs-metric-value">180 sec <span aria-hidden="true">→</span><span class="sr-only"> to </span> 60 sec</span>'),
    ('여러 개선이 함께 적용된 후의 작업 시간', 'Task time after several improvements were applied together'),
    ('<span class="cs-metric-value">35% 감소</span>', '<span class="cs-metric-value">35% less</span>'),
    ('AI 보조 일정 워크플로의 수동 검증', 'Manual validation in the AI-assisted scheduling workflow'),
    ('<span class="cs-metric-value">50% 이상 단축</span>', '<span class="cs-metric-value">50%+ faster</span>'),
    ('디자인 시스템 도입 후 릴리스 주기', 'Release cycles after the design system was adopted'),
    ('<span class="cs-metric-value">3,000명 이상</span>', '<span class="cs-metric-value">3,000+</span>'),
    ('AI 일정 추천 경험을 사용하는 임상의', 'Clinicians using the AI scheduling recommendation experience'),
    ('<span class="cs-metric-value">23명 전원</span>', '<span class="cs-metric-value">All 23</span>'),
    ('디자인 시스템을 조직 표준으로 채택한 개발자', 'Developers who adopted the design system as the org-wide standard'),
    ('규칙이 많은 업무일수록 규칙을 먼저 설명하기보다 지금 고를 수 있는 선택을 보여 주는 편이 판단을 돕습니다. AI 추천도 사람이 확인하고 조정할 수 있을 때 실제 결정으로 이어진다는 점을 설계 원칙으로 삼았습니다.', 'In rule-heavy work, showing the choices available now helps people decide more than explaining the rules first. I also made it a design principle that AI recommendations turn into real decisions only when people can check and adjust them.'),
    ('수치는 프로젝트에서 측정·보고된 값으로, 여러 개선이 함께 적용된 결과입니다. 한 화면이나 한 사람의 단독 성과가 아닙니다.', 'Figures were measured and reported in the project and reflect several improvements applied together, not the result of a single screen or person.'),
    ('Enterprise Operations — Second Context', 'Enterprise Operations — Second Context'),
    ('글로벌 제약사의 운영 모니터링에서 흩어진 신호를 심각도와 업무 영향 중심으로 다시 구성한 인시던트 관리 UX 사례.', 'Incident management UX for a global pharmaceutical company’s operations monitoring, restructuring scattered signals around severity and business impact.'),
    ('흩어진 신호 속에서, <span class="tl">먼저 대응할 문제가 먼저 보이도록.</span>', 'Among scattered signals, the issue to handle first comes first.'),
    ('글로벌 제약사의 운영 모니터링 플랫폼에서 8개 대시보드에 흩어진 정보를 심각도와 업무 영향 중심으로 다시 구성하고, AI 인사이트를 조사 우선순위에 맞춰 보여 주는 기준을 정했습니다.', 'On a global pharmaceutical company’s operations monitoring platform, information scattered across 8 dashboards was rebuilt around severity and business impact, with criteria for showing AI insights by investigation priority.'),
    ('<span class="cs-hero-num">30분 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 3분</span>', '<span class="cs-hero-num">30 min <span aria-hidden="true">→</span><span class="sr-only"> to </span> 3 min</span>'),
    ('프로젝트에서 보고된 인시던트 조사 시간', 'Incident investigation time reported in the project'),
    ('<span class="cs-hero-num">80% 단축</span>', '<span class="cs-hero-num">80% faster</span>'),
    ('인시던트 분류(triage) 시간', 'Incident triage time'),
    ('<span class="cs-hero-num">40% 단축</span>', '<span class="cs-hero-num">40% faster</span>'),
    ('개발자 내부 도구의 티켓 처리 시간', 'Ticket processing time in developers’ internal tools'),
    ('금속 장비 캐비닛이 양옆으로 길게 늘어선 회색 통로', 'A long grey aisle lined on both sides with metal equipment cabinets'),
    ('백신 운영을 지원하는 엔터프라이즈 모니터링 플랫폼으로, 제약사 엔지니어링팀이 사용했습니다. 운영 담당자는 인시던트를 조사하기 위해 8개 대시보드를 오가며 심각도와 영향을 파악해야 했습니다.', 'An enterprise monitoring platform supporting vaccine operations, used by the company’s engineering teams. To investigate an incident, operators had to move between 8 dashboards to work out severity and impact.'),
    ('UX 디자인 에이전시를 통해 계약 Senior Product Designer로 참여했습니다.', 'Joined as a contract Senior Product Designer through a UX design agency.'),
    ('이해관계자 인터뷰 15회를 진행해 위험 예측·알림·신뢰도 같은 AI 인사이트를 어떻게 보여주고 우선순위를 정할지 정의했습니다.', 'Conducted 15 stakeholder interviews to define how AI insights such as risk predictions, alerts, and confidence levels are surfaced and prioritized.'),
    ('글로벌 IT 기업의 AI/ML 팀과 협업해 생성형 AI 기반 인시던트 관리 시스템을 설계하고, 모델 출력을 엔터프라이즈 사용자가 행동할 수 있는 신호로 바꿨습니다.', 'Designed a generative-AI incident management system with a global IT company’s AI/ML teams, translating model outputs into actionable signals for enterprise users.'),
    ('이전 경력 프로젝트 · 에이전시를 통한 계약 · 2024', 'Previous-role project · Contract through an agency · 2024'),
    ('인시던트를 조사하려면 8개 대시보드를 오가며 심각도와 영향을 직접 맞춰 봐야 해, 무엇부터 볼지 정하는 데 시간이 걸렸습니다.', 'Investigating an incident meant moving across 8 dashboards and matching severity and impact by hand, so deciding where to start took time.'),
    ('정보 구조를 심각도와 후속 영향 중심으로 다시 설계하고, AI 인사이트는 같은 무게로 나열하지 않고 조사 우선순위에 따라 보여 주었습니다.', 'The information architecture was rebuilt around severity and downstream impact, and AI insights are shown by investigation priority instead of all at the same weight.'),
    ('8개 대시보드 대신, 심각도와 영향 중심의 한 흐름.', 'One flow around severity and impact, instead of 8 dashboards.'),
    ('담당자가 8개 대시보드를 오가며 심각도와 영향을 직접 맞춰 봐야 했기 때문에, 정보 구조를 심각도와 후속 영향 중심으로 다시 설계했습니다.', 'Because operators had to piece together severity and impact across 8 dashboards themselves, the information architecture was redesigned around severity and downstream impact.'),
    ('화면을 옮겨 다니지 않고, 한 목록에서 무엇부터 조사할지 정합니다.', 'People decide what to investigate first from one list, without jumping between screens.'),
    ('재구성한 인시던트 개요 화면', 'Recreated incident overview screen'),
    ('많은 신호 중에서 심각도와 업무 영향이 큰 인시던트를 목록 맨 위에 둡니다.', 'Incidents with the highest severity and business impact sit at the top of the list.'),
    ('재구성한 인시던트 조사·AI 검색 화면', 'Recreated incident investigation and AI search screen'),
    ('선택한 인시던트의 관련 기록과 AI 검색으로 조사 맥락을 한곳에서 확인합니다.', 'Related records and AI search bring the investigation context for the selected incident into one place.'),
    ('먼저 대응할 문제를, 먼저 보이게.', 'Put the issue to handle first, first.'),
    ('기술 신호(이상 점수)와 업무 영향(막힌 팀·담당자)을 함께 보고 가장 먼저 대응할 항목을 맨 위에 둡니다. 항목을 고르면 영향받는 팀과 관련 신호, 담당자, 기록을 한곳에서 확인합니다.', 'Technical signals (anomaly scores) and business impact (blocked teams and owners) are read together to put the item to handle first at the top. Selecting an item shows affected teams, related signals, owners, and history in one place.'),
    ('알림이 많아도, 지금 가장 중요한 한 건에서 조사를 시작합니다.', 'Even with many alerts, investigation starts from the single most important item.'),
    ('AI 인사이트는, 같은 무게로 나열하지 않는다.', 'AI insights aren’t listed at equal weight.'),
    ('위험 예측·알림·신뢰도를 같은 무게로 나열하지 않고, 조사 우선순위에 따라 보여주는 기준을 정했습니다. 예측은 가능성으로만 쓰고, 근거가 된 관련 기록을 펼쳐 볼 수 있게 했습니다.', 'Rather than listing risk predictions, alerts, and confidence levels with equal weight, set criteria for showing them by investigation priority. Predictions are framed only as possibilities, with the related records behind them available to expand.'),
    ('AI 요약을 믿을지 판단할 근거를 바로 확인합니다.', 'People can check the evidence right away before deciding whether to trust an AI summary.'),
    ('<span class="cs-metric-value">30분 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 3분</span>', '<span class="cs-metric-value">30 min <span aria-hidden="true">→</span><span class="sr-only"> to </span> 3 min</span>'),
    ('<span class="cs-metric-value">80% 단축</span>', '<span class="cs-metric-value">80% faster</span>'),
    ('의사결정 지원 흐름과 신호 표시를 다시 설계한 뒤의 인시던트 분류(triage) 시간', 'Incident triage time after redesigning decision-support workflows and signal display'),
    ('<span class="cs-metric-value">40% 단축</span>', '<span class="cs-metric-value">40% faster</span>'),
    ('<span class="cs-metric-value">15회</span>', '<span class="cs-metric-value">15</span>'),
    ('AI 인사이트의 표시와 우선순위를 정하기 위한 이해관계자 인터뷰', 'Stakeholder interviews to define how AI insights are shown and prioritized'),
    ('신호가 많은 화면에서는 모든 정보를 보여 주는 것보다, 조사 순서를 정하는 기준을 팀과 함께 합의하는 일이 설계의 출발점이었습니다. AI 출력도 그 기준 안에서 근거와 함께 보여 줄 때 행동할 수 있는 신호가 됩니다.', 'On signal-heavy screens, the starting point was agreeing with the team on how to order an investigation, not showing every piece of information. AI output also becomes an actionable signal when it appears within those criteria, together with its evidence.'),
    ('수치는 프로젝트에서 측정·보고된 값이며, 측정 방식은 지표마다 다릅니다. 데모는 설계 설명을 위한 재구성으로, 수치를 데모 하나의 결과로 보지 않습니다.', 'Figures were measured and reported in the project; methods differ by metric. The demos are recreated for illustration, and the figures are not the result of any single demo.'),
    ('인터넷 연결이 끊겼습니다', 'You’re offline'),
    ('무엇을 확인할지 알려 주고, 다시 시도할 수 있게 합니다.', 'Says what to check, then offers a way back.'),
    ('연결 확인 후 다시 시도', 'Check connection and retry'),
    ('서버에 일시적인 문제가 있습니다', 'A temporary server problem'),
    ('사용자 잘못이 아니라는 점을 분명히 합니다.', 'Makes clear it isn’t the user’s fault.'),
    ('잠시 후 다시 시도', 'Try again shortly'),
    ('이미 가입된 계정이 있습니다', 'An account already exists'),
    ('중복 계정이 만들어지기 전에 멈춥니다.', 'Stops a duplicate account before it’s created.'),
    ('기존 계정으로 로그인', 'Sign in to your account'),
    ('이메일을 잘못 입력했나요?', 'Used the wrong email?'),
    ('인증 코드만 다시 보낼 수 있어 막히던 지점에 출구를 만듭니다.', 'Adds a way out where people could only resend the code.'),
    ('이메일 변경', 'Change email'),
    ('Identity Verification — Second Context', 'Identity Verification — Second Context'),
    ('건너뛸 수 없는 본인 인증(KYC)을 이유·현재 상태·다음 행동이 보이는 흐름으로 다시 설계한 모바일 앱 사례.', 'A mobile app case study redesigning mandatory identity verification (KYC) into a flow where the reason, current status, and next action are always visible.'),
    ('건너뛸 수 없는 본인 인증을, <span class="tl">이해할 수 있는 단계로.</span>', 'Mandatory identity verification, made into a step people understand.'),
    ('규정상 건너뛸 수 없는 본인 인증(KYC)에서 많은 사용자가 이탈했습니다. 마찰을 없애는 대신, 이유와 현재 상태, 다음 행동이 보이는 흐름으로 다시 설계했습니다.', 'Many users dropped off at an identity verification (KYC) step that regulation made mandatory. Instead of removing the friction, the flow was redesigned so the reason, current status, and next action are always visible.'),
    ('<span class="cs-hero-num">+95%</span>', '<span class="cs-hero-num">+95%</span>'),
    ('본인 인증 완료 성공률', 'Successful verification completion'),
    ('<span class="cs-hero-num">+25%</span>', '<span class="cs-hero-num">+25%</span>'),
    ('인증 후 첫 거래 완료율', 'First-transaction completion after verification'),
    ('<span class="cs-hero-num">−25%</span>', '<span class="cs-hero-num">−25%</span>'),
    ('본인 인증 관련 고객 문의', 'Verification-related support inquiries'),
    ('책상 위 키보드 앞에서 두 손으로 휴대폰을 들고 지문 인증 화면에 손가락을 올리려는 모습', 'Two hands holding a phone above a keyboard, about to place a finger on a fingerprint verification screen'),
    ('규제를 받는 산업의 모바일 앱에서, 사용자는 서비스를 이용하기 전에 반드시 본인 인증(KYC, Know Your Customer)을 마쳐야 했습니다. 건너뛸 수 없는 단계였고, 많은 사용자가 바로 이 단계에서 이탈했습니다.', 'In a mobile app in a regulated industry, people had to complete identity verification (KYC, Know Your Customer) before using the service. The step couldn’t be skipped, and many users dropped off right there.'),
    ('리서치, 인증 흐름의 상태·예외 로직, UI 디자인을 이끌었습니다.', 'Led research, the status and exception logic of the verification flow, and UI design.'),
    ('디자인 시스템을 공동으로 맡아, 컴포넌트와 상태를 주석과 함께 개발팀에 전달했습니다.', 'Co-owned the design system and handed components and states to engineering with annotations.'),
    ('프로덕트 오너, 프로덕트 매니저, 비즈니스 분석가, 개발자와 함께 일했습니다. 본인 인증 규정이 서로 다른 두 시장에 같은 원칙의 흐름을 적용했습니다.', 'Worked with a product owner, product manager, business analyst, and developers, applying one set of principles to two markets with different identity-verification regulations.'),
    ('이전 경력 프로젝트 · 고객사와 제품 이름은 공개하지 않습니다', 'Previous-role project · Client and product names are not disclosed'),
    ('사용자를 멈추게 한 것은 신분증 촬영이 아니라, 왜 필요한지·지금 어떤 상태인지·실패하면 무엇을 해야 하는지 알 수 없다는 점이었습니다.', 'What stopped people wasn’t scanning an ID. It was not knowing why it was needed, where things stood, or what to do if it failed.'),
    ('인증이 필요한 이유를 먼저 설명하고, 현재 상태를 항상 보여 주고, 실패할 때마다 한 가지 분명한 다음 행동을 안내했습니다.', 'Explain why verification is needed up front, always show the current status, and offer one clear next action whenever something fails.'),
    ('왜 필요한지, 무엇 때문인지, 얼마나 걸리는지 먼저.', 'Why, what triggered it, and how long—first.'),
    ('인증을 시작하기 전에 인증이 필요한 이유, 어떤 행동 때문에 시작됐는지, 예상 소요 시간을 알려 줍니다. 제출할 수 있는 서류를 모두 나열하지 않고, 지금 쓸 수 있는 권장 경로만 보여 줍니다.', 'Before verification starts, the screen explains why it’s needed, which action triggered it, and how long it will take. Instead of listing every document option, it shows only the recommended path available now.'),
    ('‘왜 이 정보가 필요하지?’라는 질문에 답을 들은 뒤 인증을 시작합니다.', 'People start verifying after “Why do they need this?” has been answered.'),
    ('재구성한 본인 인증 흐름 네 화면', 'Recreated four-screen identity verification flow'),
    ('이유와 방법 안내 → 신분증 촬영 → 이메일 확인(잘못 입력했을 때 바꾸는 길) → 완료 후 미리 채운 정보까지, 한 흐름으로 이어집니다.', 'Why and how → ID capture → email confirmation (with a way to fix a wrong email) → done, with details prefilled, in one continuous flow.'),
    ('재구성한 본인 인증 안내 화면', 'Recreated verification intro screen'),
    ('본인 확인이 필요합니다', 'We need to verify your identity'),
    ('<dt>이유</dt>', '<dt>Why</dt>'),
    ('관련 규정에 따라 서비스를 이용하기 전에 본인 확인이 필요합니다.', 'Regulations require identity verification before you can use the service.'),
    ('<dt>시작된 이유</dt>', '<dt>What triggered it</dt>'),
    ('방금 회원가입을 마쳤습니다.', 'You just finished signing up.'),
    ('<dt>예상 시간</dt>', '<dt>Time needed</dt>'),
    ('약 2분 · 신분증과 셀피 1장', 'About 2 minutes · an ID and one selfie'),
    ('신분증으로 시작', 'Start with your ID'),
    ('다른 서류로 진행', 'Use a different document'),
    ('지금 어디쯤인지, 항상 보이게.', 'Always show where things stand.'),
    ('인증 상태를 시작 전 · 검토 중 · 승인 · 조치 필요 네 가지로 나누고, 어느 화면에서든 같은 방식으로 보여 줍니다. 처리에 30~60초가 걸리는 동안에는 기다리는 시간을 알려, 조용한 화면이 실패처럼 느껴지지 않게 했습니다.', 'Verification status is split into four states—not started, in review, approved, action required—and shown the same way on every screen. During the 30–60 seconds of processing, the wait time is stated so a quiet screen doesn’t feel like failure.'),
    ('제출한 뒤에도 ‘된 건가, 아직인가’를 묻지 않습니다.', 'After submitting, people no longer wonder “Did it go through?”'),
    ('재구성한 인증 상태 표시', 'Recreated verification status display'),
    ('네 가지 상태', 'Four states'),
    ('시작 전</li>', 'Not started</li>'),
    ('검토 중</li>', 'In review</li>'),
    ('승인</li>', 'Approved</li>'),
    ('조치 필요</li>', 'Action required</li>'),
    ('색과 함께 아이콘 모양과 문구로 상태를 구분합니다.', 'States are told apart by icon shape and wording, not color alone.'),
    ('재구성한 처리 중 화면', 'Recreated processing screen'),
    ('<p class="cs-mock-label">처리 중</p>', '<p class="cs-mock-label">Processing</p>'),
    ('서류를 확인하고 있습니다', 'Checking your documents'),
    ('보통 30~60초 걸립니다. 이 화면을 닫아도 확인은 계속됩니다.', 'This usually takes 30–60 seconds. Checking continues if you close this screen.'),
    ('실패해도, 다음 단계는 하나로.', 'Even on failure, one next step.'),
    ('실패 메시지는 무엇이 일어났는지와 지금 할 수 있는 한 가지 행동을 함께 알려 줍니다. 진행을 막는 오류는 빨간색으로 경고·안내와 구분하고, 색만이 아니라 문구와 아이콘으로도 상태를 알립니다.', 'Each failure message says what happened together with the one thing to do now. Blocking errors use red to stay distinct from warnings and guidance, and status is conveyed by wording and icons, not color alone.'),
    ('막혀도 처음부터 다시 시작하지 않고, 다음 단계로 이어집니다.', 'Even when blocked, people continue to the next step instead of starting over.'),
    ('<span class="cs-metric-value">+95%</span>', '<span class="cs-metric-value">+95%</span>'),
    ('<span class="cs-metric-value">+25%</span>', '<span class="cs-metric-value">+25%</span>'),
    ('<span class="cs-metric-value">−25%</span>', '<span class="cs-metric-value">−25%</span>'),
    ('인증 전에 이유·시작 계기·예상 시간을 알려 주는 안내', 'An intro that gives the reason, trigger, and expected time before verification'),
    ('어느 화면에서든 같은 방식으로 보이는 네 가지 인증 상태', 'Four verification states shown the same way on every screen'),
    ('실패 상황마다 무엇이 일어났는지와 한 가지 다음 행동', 'For each failure, what happened and one next action'),
    ('잘못 입력한 이메일을 고칠 수 있는 변경 경로', 'A path to change a mistyped email'),
    ('규정이 다른 두 시장에 같은 원칙으로 적용한 흐름', 'One set of principles applied to two markets with different regulations'),
    ('규정이 요구하는 마찰은 없앨 수 없을 때가 많습니다. 사용자가 이유와 현재 상태, 다음 행동을 알 수 있으면 같은 단계도 납득할 수 있는 과정이 된다는 점을 이 프로젝트의 중심 원칙으로 삼았습니다.', 'Friction that regulation requires often can’t be removed. The core principle of this project was that when people know the reason, the current status, and the next action, the same step becomes a process they can accept.'),
    ('수치는 출시 후 프로젝트에서 측정·보고된 값으로, 여러 설계 변화가 함께 적용된 결과입니다. 화면은 설계 설명을 위해 새로 구성한 예시입니다.', 'Figures were measured and reported in the project after launch and reflect several design changes applied together. Screens are new examples created for illustration.'),
    ('Product Localization — Second Context', 'Product Localization — Second Context'),
    ('글로벌 테크 기업의 제품 콘텐츠를 한국 시장에 맞춰 문구, 이름·날짜·시간 표기, 타이포그래피와 간격까지 조정한 현지화 사례.', 'A localization case adapting a global tech company’s product content for Korea, from copy to name, date, and time formats, typography, and spacing.'),
    ('번역된 문장을 넘어, <span class="tl">한국어 사용자에게 자연스러운 제품으로.</span>', 'Beyond translated sentences, a product that feels natural in Korean.'),
    ('글로벌 테크 기업의 데스크톱 제품 콘텐츠를 한국 시장에 맞추며, 문구와 함께 이름·날짜·시간 표기, 타이포그래피와 간격까지 한국어 사용 맥락에 맞게 조정했습니다.', 'Adapting a global tech company’s desktop product content for Korea, the work went beyond copy to name, date, and time formats, typography, and spacing suited to how Korean is read and used.'),
    ('창가 라운지에 둘러앉아 커피를 들고 이야기를 나누는 여러 국적의 동료들', 'Colleagues of different backgrounds talking over coffee in a lounge by the window'),
    ('5K 디스플레이 데스크톱 제품 관련 콘텐츠를 한국 시장에 맞추는 프로젝트였습니다. 글로벌 브랜드의 표현과 한국어의 자연스러운 문구·레이아웃을 함께 유지해야 했습니다.', 'A project adapting content for a 5K-display desktop product to the Korean market, keeping the global brand’s expression while making Korean copy and layout read naturally.'),
    ('UX 문구와 디자인 자산을 현지화하고, 팀 간 소통을 지원했습니다.', 'Localized UX copy and design assets and supported communication between teams.'),
    ('2019년 6주 동안 영국의 글로벌 제작 에이전시, 고객사의 한국 팀·미국 팀과 협업했습니다.', 'Worked for 6 weeks in 2019 with a global production agency in the U.K. and the client’s Korea and U.S. teams.'),
    ('이전 경력 프로젝트 · 6주 · 2019', 'Previous-role project · 6 weeks · 2019'),
    ('영어 원문을 그대로 옮기면 이름 순서, 날짜·시간 표기, 문장 길이와 줄바꿈이 한국어 사용자에게 어색하게 읽혔습니다.', 'Carrying the English original over as-is made name order, date and time formats, sentence length, and line breaks read awkwardly for Korean users.'),
    ('글로벌 브랜드의 표현은 지키면서, 한국어 사용자가 익숙한 표기 순서와 읽는 흐름에 맞춰 문구와 화면 구성을 조정했습니다.', 'Keeping the global brand’s expression, copy and layout were adjusted to the formats and reading flow Korean users expect.'),
    ('문구만이 아니라, 이름·날짜·시간 표기까지.', 'Not just copy—name, date, and time formats too.'),
    ('글로벌 브랜드의 표현과 한국어의 자연스러움을 함께 지켜야 했기 때문에, 문구만 옮기지 않고 이름·날짜·시간 표기 방식까지 한국어 관례에 맞췄습니다.', 'Because both the global brand’s expression and natural Korean had to be preserved, name, date, and time formats were matched to Korean conventions, not just the copy.'),
    ('같은 정보를 익숙한 순서로 읽어, 다시 해석할 필요가 없습니다.', 'The same information reads in a familiar order, with nothing to reinterpret.'),
    ('한국어 문장에 맞춘 타이포그래피와 간격.', 'Typography and spacing fitted to Korean text.'),
    ('같은 이유로 타이포그래피와 간격을 한국어 문장에 맞춰 조정했습니다. 문구 길이가 달라져도 버튼과 줄바꿈이 자연스럽게 읽히도록 레이아웃을 맞췄습니다.', 'For the same reason, typography and spacing were adjusted for Korean text, and layouts were tuned so buttons and line breaks still read naturally when copy length changes.'),
    ('번역된 화면이 아니라, 처음부터 한국어로 만든 화면처럼 읽힙니다.', 'Screens read as if they were made in Korean, not translated.'),
    ('노트북 화면을 함께 보며 문구를 검토하는 두 동료', 'Two colleagues reviewing copy together on a laptop screen'),
    ('출력한 화면 위에 포스트잇을 붙이며 흐름을 정리하는 워크숍', 'A workshop placing sticky notes on printed screens to map a flow'),
    ('세 팀의 관점이 어긋나지 않도록.', 'Keeping three teams aligned.'),
    ('영국·한국·미국 팀의 관점이 어긋나지 않도록 팀 간 소통을 지원했습니다. 브랜드 표현과 한국어 관례가 부딪히는 지점을 함께 확인하며 산출물을 정리했습니다.', 'Supported communication so the U.K., Korea, and U.S. teams stayed aligned, working through the points where brand expression and Korean conventions met before finalizing deliverables.'),
    ('한국어 사용자에게 닿는 문구와 화면이 한 방향으로 정리됩니다.', 'Copy and screens that reach Korean users land in one consistent direction.'),
    ('협업 구조', 'How the teams worked together'),
    ('<span class="loc-where">영국</span>', '<span class="loc-where">U.K.</span>'),
    ('글로벌 제작 에이전시', 'Global production agency'),
    ('<span class="loc-where">현지화</span>', '<span class="loc-where">Localization</span>'),
    ('Rachel · 한국어 UX 문구와 디자인 자산', 'Rachel · Korean UX copy and design assets'),
    ('<span class="loc-where">한국</span>', '<span class="loc-where">Korea</span>'),
    ('고객사 한국 팀', 'Client’s Korea team'),
    ('<span class="loc-where">미국</span>', '<span class="loc-where">U.S.</span>'),
    ('고객사 미국 팀', 'Client’s U.S. team'),
    ('한국 시장에 맞춘 UX 문구와 디자인 자산', 'UX copy and design assets tailored to the Korean market'),
    ('이름·날짜·시간 표기', 'Name, date, and time formats'),
    ('한국어 타이포그래피와 간격을 반영한 현지화 레이아웃', 'Localized layouts reflecting Korean typography and spacing'),
    ('<span class="cs-metric-value">6주</span>', '<span class="cs-metric-value">6 weeks</span>'),
    ('2019년, 제작 에이전시와 고객사의 한국·미국 팀이 함께한 현지화 기간', 'Localization period in 2019, with a production agency and the client’s Korea and U.S. teams'),
    ('현지화는 번역의 정확도만이 아니라, 사용자가 익숙한 표기와 읽는 흐름을 지키는 디자인 작업이라는 점을 배웠습니다.', 'I learned that localization is design work that protects the formats and reading flow people are used to, not only a matter of translation accuracy.'),
    ('이 프로젝트는 확인된 성과 수치가 없어 산출물과 배운 점으로 정리했습니다. 비교 화면의 문구는 실제 프로젝트 화면이 아닌 예시입니다.', 'There are no confirmed performance figures for this project, so it is summarized through deliverables and lessons. Copy in the comparison screens is sample text, not actual project screens.'),
    ('사용자에게 생긴 차이', 'What changed for users'),
    ('분야와 역량', 'Field and capability'),
    ('주요 결과', 'Key results'),
    ('프로젝트 소개', 'About the project'),
    ('문제와 설계 대응', 'Problem and design response'),
    ('핵심 설계 판단', 'Key design decisions'),
    ('결과와 배운 점', 'Results and lessons'),
    ('관련 사례', 'Related case studies'),
    ('서비스 영역으로 돌아가기', 'Back to What we do'),
    ('사용자 기반', 'User base'),
    ('기능', 'Features'),
    ('배우기 쉬움', 'Easy to learn'),
    ('무료', 'Free'),
    ('브랜딩', 'Branding'),
    ('Globalization · Online Go Server', 'Globalization · Online Go Server'),
    ('전통적인 아시아 전략 게임인 바둑을 글로벌 사용자들이 보다 쉽게 이해하고 즐길 수 있도록 디지털 경험을 재설계한 프로젝트입니다.', 'Redesigning a global Go platform to make a traditional Asian strategy game more accessible, intuitive, and engaging for international players.'),
    ('게임 · 온라인 커뮤니티', 'Gaming / Online Community'),
    ('웹 · 모바일(iOS/Android)', 'Web &amp; Mobile (iOS/Android)'),
    ('리드 UX/UI 디자이너 · 소프트웨어 엔지니어, 프로덕트 매니저, CEO와 협업', 'Lead UX/UI Designer · with a software engineer, product manager, and the CEO'),
    ('문화 간 제품 경험', 'Cross-Cultural Product Experience'),
    ('공개 프로젝트', 'Public project'),
    ('문화가 달라도, <span class="tl">바둑을 쉽게 시작할 수 있도록.</span>', 'Making Go Accessible Across Cultures'),
    ('한국에서 바둑이라 부르는 Go는 수백 년의 역사를 가진 전략 게임입니다. Online Go Server(OGS)는 온라인 대국과 학습, 커뮤니티로 전 세계 플레이어를 연결합니다.', 'Go, known as Baduk in Korea, is a centuries-old strategy game. Online Go Server connects players around the world through digital gameplay, learning, and community.'),
    ('웹과 모바일(iOS·Android) 모두에서 대국할 수 있는 OGS의 <b>리드 UX/UI 디자이너</b>로 디자인 파트를 맡았습니다. 리서치, 정보구조, 데스크톱·모바일 UI, 디자인 시스템, 프로토타입과 사용성 테스트를 담당했고, 개발은 OGS의 엔지니어와 함께 진행했습니다.', 'I led the design side of OGS as <b>Lead UX/UI Designer</b>—a platform where people play Go on the web and on mobile (iOS and Android). I owned research, information architecture, desktop and mobile UI, the design system, prototyping, and usability testing, and worked with OGS’s engineer on the build.'),
    ('다크 모드와 라이트 모드로 나란히 놓인 OGS 리디자인 화면: 빠른 대국 찾기, 진행 중인 대국 목록과 바둑판', 'OGS redesign screens in dark and light mode: quick match finder, active games list, and Go boards'),
    ('복잡한 온보딩', 'Complex onboarding'),
    ('대국을 시작하기 전 단계가 많고 불분명해, 가입 과정에서 이탈이 많았습니다.', 'Too many unclear steps before a first game led to high drop-off during sign-up.'),
    ('혼란스러운 탐색과 매치메이킹', 'Confusing navigation and matchmaking'),
    ('대기실 입장과 대국 상대 찾기 방식이 이해하기 어려웠고, 실력이 맞지 않는 상대와 연결되기도 했습니다.', 'Entering the lobby and finding an opponent were hard to follow, and players were sometimes matched with mismatched skill levels.'),
    ('일관되지 않은 UI와 아이콘', 'Inconsistent UI and icons'),
    ('화면마다 시각 디자인과 아이콘 언어가 달라, 무엇을 먼저 봐야 할지 알기 어려웠습니다.', 'Visual design and icon language varied from screen to screen, so it was hard to know what to look at first.'),
    ('초보자에게 높은 진입 장벽', 'A high barrier for beginners'),
    ('정보가 빽빽한 홈 화면에 분명한 다음 행동이 없어, 처음 온 사용자가 어디서 시작할지 몰랐습니다.', 'A dense homepage with no clear call to action left first-time users unsure where to begin.'),
    ('모바일과 데스크톱의 차이', 'Mobile and desktop out of step'),
    ('기기마다 경험이 달라, 초보자와 모바일 사용자의 재방문이 낮았습니다.', 'The experience differed across devices, and retention was low among beginners and mobile users.'),
    ('익숙하지 않은 전통 게임을, 새로 오는 글로벌 사용자도 다가갈 수 있게 만드는 일이었습니다.', 'Making a complex traditional game approachable to new and international audiences.'),
    ('리디자인 전 OGS의 어두운 대시보드: 작은 바둑판 목록과 오른쪽의 빽빽한 링크 목록', 'The pre-redesign OGS dashboard: small boards and a dense column of links on the right'),
    ('리디자인 전 대시보드. 정보는 많지만 먼저 할 행동이 보이지 않았습니다.', 'The dashboard before the redesign: lots of information, but no visible first action.'),
    ('리디자인 전 홈 화면에 시스템 알림·튜토리얼 링크·빠른 링크 등의 문제를 표시한 주석 화면', 'The pre-redesign homepage annotated with issues such as system notifications, tutorial links, and quick links'),
    ('기존 홈 화면 분석. 알림, 튜토리얼 링크, 빠른 링크가 한 화면에서 경쟁했습니다.', 'Analysis of the old homepage: notifications, tutorial links, and quick links all competed on one screen.'),
    ('익숙하지 않은 게임의 첫 문턱', 'The first threshold of an unfamiliar game'),
    ('명이 참여한 2분 설문 (초보·중급 플레이어)', 'active players in a 2-minute survey (beginner and intermediate)'),
    ('개 경쟁 플랫폼 분석 (KGS · Tygem 중심)', 'competing platforms analyzed (focus on KGS and Tygem)'),
    ('대기실 입장·매치메이킹 과정이 헷갈린다고 응답', 'were confused by lobby entry and matchmaking'),
    ('아이콘이 오래되고 직관적이지 않다고 응답', 'found the iconography outdated and unintuitive'),
    ('더 단순한 레이아웃과 깔끔한 글꼴을 선호', 'preferred a simpler layout with cleaner typography'),
    ('작업 흐름이 복잡하고 여러 곳에 흩어져 있다', 'A complicated, fragmented workflow'),
    ('시각 디자인과 아이콘 언어가 일관되지 않다', 'Inconsistent visual design and icon language'),
    ('온보딩과 대국 시작 방법이 분명하지 않다', 'Unclear onboarding and match start'),
    ('홈 화면이 정보로 가득해 부담스럽다', 'An overwhelming homepage with dense information'),
    ('설문, 사용성 테스트, 카드 소팅으로 초보·중급 플레이어 20명의 경험을 살펴보고, 10개 이상의 바둑 플랫폼을 비교했습니다. 대기실 매치메이킹 UX, 모바일 접근성, 커뮤니티 기능을 중심으로 KGS와 Tygem을 자세히 분석했습니다.', 'Through surveys, usability testing, and card sorting, I studied 20 beginner and intermediate players and compared more than 10 Go platforms, looking closely at KGS and Tygem for lobby matchmaking UX, mobile accessibility, and community features.'),
    ('리서치 결과', 'Research findings'),
    ('<span class="sr-only">강점</span>', '<span class="sr-only">Strength</span>'),
    ('<span class="sr-only">부족</span>', '<span class="sr-only">Gap</span>'),
    ('경쟁 플랫폼 비교', 'Competitive comparison'),
    ('강점', 'Strength'),
    ('부족', 'Gap'),
    ('경쟁 플랫폼 비교(원본 분석 자료를 다시 그림). 세 플랫폼 모두 ‘배우기 쉬움’이 약했고, 이 지점을 OGS의 기회로 삼았습니다.', 'Competitive comparison (redrawn from the original analysis). Ease of learning was weak across platforms, so it became OGS’s opportunity.'),
    ('무엇이 문제였나', 'What wasn’t working'),
    ('리서치 수치는 2023년 프로젝트에서 진행한 소규모 설문(20명) 결과입니다.', 'Research figures come from a small survey (20 participants) run during the 2023 project.'),
    ('누가, 어디서 멈추는지부터', 'Who stops, and where'),
    ('명확한 정보구조', 'Clear information architecture'),
    ('내비게이션을 Play · Learn · Watch · Community 중심으로 다시 짜고, 핵심 기능이 먼저 보이도록 이름과 위계를 정리했습니다.', 'Restructured navigation around core actions such as Play, Learn, Watch, and Community, with clearer labels and hierarchy.'),
    ('이해하기 쉬운 탐색', 'Navigation that explains itself'),
    ('처음 보는 용어 대신 직관적인 이름을 쓰고, 지금 어디에 있는지와 다음에 갈 곳을 분명하게 보여 주었습니다.', 'Used intuitive names instead of unfamiliar terms, showing clearly where you are and where to go next.'),
    ('신규 사용자 중심 온보딩', 'Onboarding for newcomers'),
    ('단계와 진행 상태가 보이는 가입 흐름과, 실력에 맞춘 선택형 빠른 튜토리얼을 설계했습니다.', 'Designed a sign-up flow with visible steps and progress, plus an optional quick-start tutorial tailored to skill level.'),
    ('게임 참여와 매치메이킹', 'Getting into a game'),
    ('바둑판 크기와 대국 속도를 고르면 바로 상대를 찾는 빠른 대국 찾기로, 대국 시작까지의 결정을 줄였습니다.', 'A quick match finder lets players pick board size and game speed and find an opponent right away, cutting the decisions before a first game.'),
    ('글로벌 사용자에게 일관된 경험', 'One experience for players everywhere'),
    ('언어 선택과 국가 표시를 가입 직후 흐름에 넣고, 화면마다 같은 색·글꼴·아이콘 규칙을 적용했습니다.', 'Put language selection and country display into the post-sign-up flow, and applied the same color, type, and icon rules on every screen.'),
    ('반응형 제품 디자인', 'Responsive product design'),
    ('데스크톱과 모바일에서 같은 구조와 행동이 이어지도록 반응형 화면을 함께 설계했습니다.', 'Designed responsive screens so structure and actions carry over between desktop and mobile.'),
    ('번역만으로는 부족했습니다. 처음 보는 게임의 구조와 개념이 화면만 보고도 이해되도록, 정보 구조와 흐름 자체를 다시 설계했습니다.', 'Translation alone wasn’t enough. I redesigned the information architecture and flows so the structure and concepts of an unfamiliar game make sense from the screen itself.'),
    ('가입 후 홈 화면에서 국기와 함께 English·Chinese·Bengali·South Korea 언어를 고르는 메뉴', 'The post-sign-up home screen with a language menu listing English, Chinese, Bengali, and South Korea with flags'),
    ('가입 직후 언어 선택 — 플레이어가 익숙한 언어로 바로 바꿀 수 있습니다.', 'Language selection right after sign-up, so players can switch to a familiar language immediately.'),
    ('데스크톱 대국 화면: 큰 바둑판과 오른쪽의 두 플레이어 정보·채팅 패널', 'Desktop game screen: a large board with both players’ details and a chat panel on the right'),
    ('모바일 대국 화면: 바둑판 아래 두 플레이어의 실력·남은 시간', 'Mobile game screen: the board with both players’ rank and remaining time below'),
    ('모바일 대국 카드: 바둑판 위아래에 플레이어 이름·점수·시간', 'Mobile game card: player name, points, and time above and below the board'),
    ('웹과 모바일(iOS·Android) 어디서든 같은 대국 경험 — 바둑판, 플레이어 정보, 남은 시간을 기기마다 같은 위계로 설계했습니다.', 'The same game on the web and on mobile (iOS and Android): board, player details, and remaining time follow the same hierarchy on every device.'),
    ('문화의 맥락을, 이해되는 제품 경험으로', 'From cultural context to a product people understand'),
    ('리디자인 전 빠른 대국 찾기: 회색 버튼 네 개와 바둑판 크기 선택', 'The old quick match finder: four grey buttons and board-size options'),
    ('Before — 대국 방식이 버튼 이름만으로 구분되어 차이를 알기 어려웠습니다.', 'Before — game types were told apart only by button labels, so the differences were unclear.'),
    ('리디자인한 빠른 대국 찾기: 바둑판 크기 선택, 대국 속도 카드, 내 실력 위치를 보여 주는 그래프', 'The redesigned quick match finder: board-size selection, game-speed cards, and a chart showing your skill position'),
    ('After — 바둑판 크기와 속도를 먼저 고르고, 각 방식의 시간을 함께 보여 줘 선택이 분명해졌습니다.', 'After — choose board size and speed first, with each mode’s timing shown, so the choice is clear.'),
    ('로그인 전 홈에서 대국을 고르고 가입한 뒤 대국 화면으로 들어가는 전체 흐름', 'The full flow from the logged-out home to choosing a game, signing up, and entering a game'),
    ('전체 흐름 — 처음 방문한 사용자가 대국을 보고, 가입하고, 첫 대국으로 들어가는 과정을 한 흐름으로 이었습니다.', 'End-to-end flow — a first-time visitor watches a game, signs up, and enters a first game in one continuous flow.'),
    ('가입 창이 열리고 아이디·비밀번호를 입력한 뒤 소셜 계정으로도 가입할 수 있는 흐름', 'The sign-up dialog opening, entering a username and password, with social sign-up options'),
    ('온보딩 — 가입을 한 창 안에서 끝내고, 소셜 계정 가입도 같은 자리에 두었습니다.', 'Onboarding — sign-up finishes in a single dialog, with social sign-up in the same place.'),
    ('상단 메뉴에서 국기 아이콘을 눌러 사이트 언어를 바꾸는 프로토타입', 'A prototype changing the site language from the flag icon in the top menu'),
    ('글로벌 — 상단 국기 아이콘에서 언어를 바로 바꾸는 흐름을 프로토타입으로 검증했습니다.', 'Global — changing language straight from the flag icon was tested as a prototype.'),
    ('라이트 모드 대시보드: 대국 찾기 버튼과 프로필 패널', 'Dashboard in light mode: find-a-game button and profile panel'),
    ('라이트 모드', 'Light mode'),
    ('다크 모드 대시보드: 대국 찾기 버튼과 프로필 패널', 'Dashboard in dark mode: find-a-game button and profile panel'),
    ('다크 모드 — 오래 두는 대국에도 눈이 편하도록 두 모드를 함께 설계했습니다.', 'Dark mode — both modes were designed so long games stay easy on the eyes.'),
    ('디자인 시스템 — 원본 색상·글꼴 규칙을 다시 그렸습니다. 색과 글자 대비에 WCAG 2.1 AA 기준을 적용했습니다.', 'Design system — the original color and type rules, redrawn. Color and text contrast follow WCAG 2.1 AA.'),
    ('카페 테이블에서 휴대폰으로 리디자인한 OGS 화면을 보며 웃는 테스트 참가자', 'A test participant at a café table smiling at the redesigned OGS screens on a phone'),
    ('같은 참가자가 휴대폰 화면의 바둑판을 손가락으로 누르는 모습', 'The same participant tapping the Go board on the phone screen'),
    ('사용성 테스트 — 카페에서 20명과 게릴라 테스트를 하며 리디자인 전후를 비교했습니다(실제 테스트 사진).', 'Usability testing — guerrilla tests with 20 people at a café compared the experience before and after (actual test photos).'),
    ('“OGS를 좋아하는데, 이제 훨씬 쓰기 쉬워요.”', '“I love OGS and it’s pretty easy to use.”'),
    ('— 게릴라 테스트 참가자, OGS 사용자', '— Guerrilla test participant, OGS user'),
    ('그려 보고, 비교하고, 다시 확인한 화면', 'Explored, compared, and checked again'),
    ('Online Go Server는 리디자인과 별개로, 지금도 전 세계 바둑 플레이어가 이용하는 공개 서비스입니다. 아래 수치는 플랫폼 전체의 규모가 아니라, 리디자인 이후 프로젝트에서 기록된 변화입니다.', 'Independent of this redesign, Online Go Server is a public service used by Go players worldwide. The figures below are not the size of the platform; they are changes recorded in the project after the redesign.'),
    ('영어권이 아닌 지역에서 늘어난 신규 가입', 'growth in new registrations from non-English-speaking regions'),
    ('월간 활성 사용자(MAU)', 'Monthly active users (MAU)'),
    ('신규 가입자', 'New user registrations'),
    ('매치메이킹 완료율', 'Matchmaking completion rate'),
    ('평균 세션 시간', 'Average session duration'),
    ('사용성 평가 · 설문 응답자, 5점 만점', 'Usability rating · survey respondents, out of 5'),
    ('<span class="sr-only">3.1에서 4.5</span>', '<span class="sr-only">3.1 to 4.5</span>'),
    ('수치는 2023년 프로젝트 기록(기존 포트폴리오) 기준이며, 여러 개선이 함께 적용된 결과입니다.', 'Figures are as recorded in the 2023 project (original portfolio) and reflect several improvements applied together.'),
    ('더 많은 사람이, <span class="tl">더 오래 두게 되었습니다</span>', 'More people playing, for longer'),
    ('OGS는 누구나 들어가 볼 수 있는 공개 서비스입니다. 현재 사이트는 이 프로젝트 이후에도 OGS 팀이 계속 운영하고 바꿔 온 화면이라, 이 사례의 디자인과 다를 수 있습니다.', 'OGS is a public service anyone can visit. The current site has continued to be run and changed by the OGS team since this project, so it may differ from the designs shown here.'),
    ('직접 둘러보기', 'See it live'),
    ('Online Go Server(OGS) 사례 — Second Context', 'Online Go Server (OGS) case study — Second Context'),
    ('전통적인 아시아 전략 게임 바둑을 글로벌 사용자가 쉽게 이해하고 즐길 수 있도록 Online Go Server의 온보딩·탐색·매치메이킹을 재설계한 Globalization 사례.', 'A Globalization case study redesigning Online Go Server’s onboarding, navigation, and matchmaking so international players can understand and enjoy Go, a traditional Asian strategy game.'),
]

PATHS = [
    ('href="favicon.ico"', 'href="../favicon.ico"'),
    ('href="assets/', 'href="../assets/'),
    ('src="assets/', 'src="../assets/'),
    # Hero 영상 경로(site.js가 읽는 data 속성)도 en/ 기준으로
    ('data-hero-video="assets/', 'data-hero-video="../assets/'),
    ('data-hero-video-sm="assets/', 'data-hero-video-sm="../assets/'),
]

TABLE = {PAGES[0]: HOME, PAGES[1]: APPROACH, PAGES[2]: CONTACT, PAGES[3]: ABOUT, PAGES[4]: WORK_INDEX}
TABLE.update({c: [] for c in CASES})
# 이전 사례 페이지 표(WORK: 데모 문구)는 이제 사례 페이지들이 나눠 쓴다. 사례 공통 표와 함께 페이지에 있는 문구만 적용
SHARED = CASE_TEXT + WORK + CASE_PAGES
KEEP = re.compile(r'<!--i18n:keep-->.*?<!--/i18n:keep-->', re.S)  # 비교 자료처럼 두 언어에서 그대로 두는 부분

for page in PAGES:
    s = prep_korean(page)
    # 한국어 원본의 줄바꿈 없는 공백(고유명사 Y Combinator·Flexwork Pro 등)은 번역 표와 맞추기 위해 일반 공백으로 읽는다
    s = s.replace('\u00a0', ' ')
    e = s.replace(f'<link rel="canonical" href="{url(page)}">', f'<link rel="canonical" href="{url(page, "en")}">')
    e = e.replace(lang_nav(page, "ko"), lang_nav(page, "en"))
    e = e.replace(footer_lang(page, "ko"), footer_lang(page, "en"))
    e = OG_RE.sub("", e)  # 한국어 Open Graph 태그는 빼고, 번역이 끝난 뒤 영어 title·description으로 다시 만든다
    # i18n:keep 영역은 번역하지 않고 그대로 둔다
    kept = KEEP.findall(e)
    for i, k in enumerate(kept):
        e = e.replace(k, f'@@KEEP{i}@@', 1)
    # 사례 문구는 이 페이지에 있는 것만 페이지 표에 더한다 (홈 요약·사례 상세가 같은 번역을 공유)
    table = TABLE[page] + [(ko, en) for ko, en in SHARED if ko in s and ko not in dict(TABLE[page])]
    # 홈 #contact에는 문의 페이지와 같은 문의 폼이 있다: 문의 페이지 번역 중 홈에 있는 문구만 더한다
    if page == PAGES[0]:
        table += [(ko, en) for ko, en in CONTACT if ko in s and ko not in dict(table)]
    # 긴 문장부터 바꿔야 짧은 문구가 긴 문장 일부를 먼저 바꾸지 않는다
    table.sort(key=lambda p: -len(p[0]))
    # 페이지 표 먼저(긴 문장), 그다음 공통 문구
    for ko, en in table + COMMON + PATHS:
        if page == PAGES[2] and ko == 'Rachel과 Book a 30-minute call':
            continue
        # 페이지별 표의 문구는 반드시 있어야 한다. 공통 문구·경로는 페이지에 있을 때만 바꾼다
        assert ko not in dict(TABLE[page]) or e.count(ko) >= 1, (page, ko[:50])
        e = e.replace(ko, en)
    if page == PAGES[2]:
        e = e.replace('Rachel과 Book a 30-minute call', 'Book a 30-minute call with Rachel')
    # 짧은 고유명사는 영어 문장에서도 줄 끝에서 갈리지 않게(2026-11-11: "Y / Combinator" 방지)
    for name in ('Y Combinator', 'Flexwork Pro'):
        e = e.replace(name, name.replace(' ', '\u00a0'))
    # 반응형 이미지(srcset)의 후보 경로도 en/ 기준으로 바꾼다
    e = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + re.sub(r'(^|, )assets/', r'\1../assets/', m.group(1)) + '"', e)
    # 한국어 작업 메모 주석은 영어 페이지에 옮기지 않는다 (화면에 보이지 않음)
    e = re.sub(r'[ \t]*<!--[^>]*[가-힣][^>]*-->\n', '', e)
    # lang="ko"로 표시한 한국어 예시(예: 호칭 ‘님’)는 영어 페이지에도 그대로 둔다
    check = re.sub(r'<span lang="ko">[^<]*</span>', '', e)
    left = [m for m in re.findall(r'[^<>"]*[가-힣][^<>"]*', check) if m.strip() != '한국어']
    assert not left, (page, left)
    for i, k in enumerate(kept):
        e = e.replace(f'@@KEEP{i}@@', k, 1)
    e = add_og(page, "en", e)
    os.makedirs(os.path.join(R, 'en'), exist_ok=True)
    open(os.path.join(R, 'en', page), 'w', encoding='utf-8').write(e)
    print('built en/' + page)
