"""Second Context 한국어 페이지에 언어 전환·hreflang을 넣고, 번역 표로 en/ 영어 페이지를 만든다.
사용: python3 tools/build_en_pages.py docs   (배포 폴더 docs/ 기준, 여러 번 실행해도 결과가 같다)
운영 도메인(2026-11-09 분리): 한국어 홈 index.html → https://second-context.com/, 영어 홈 en/index.html → /en/"""
import os, re, sys

R = sys.argv[1]
BASE = "https://second-context.com/"
PAGES = ["index.html", "second-context-approach.html", "second-context-contact.html", "second-context-work.html"]


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


# Open Graph 이미지(tools/make_og_images.py로 만든 assets/og/<이름>-<언어>.png)
OG_IMAGE = {PAGES[0]: "home", PAGES[1]: "approach", PAGES[2]: "contact", PAGES[3]: "work"}
OG_RE = re.compile(r'(<meta (?:property="og:|name="twitter:)[^>]*>\n)+')
DESC_RE = re.compile(r'<meta name="description" content="[^"]*">\n')


def og_tags(page, lang, s):
    """페이지의 title·description으로 Open Graph·Twitter 카드 태그를 만든다. 이미지 설명은 이미지 속 h1 문구"""
    title = re.search(r'<title>(.*?)</title>', s).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
    img_page = PAGES[0] if OG_IMAGE[page] == "home" else page
    src = s if img_page == page else open(os.path.join(R, ("en/" if lang == "en" else "") + img_page), encoding="utf-8").read()
    h1 = re.sub(r'<[^>]+>', '', re.search(r'(?s)<h1[^>]*>(.*?)</h1>', src).group(1)).strip()
    alt = f'Second Context 로고와 “{h1}” 문구' if lang == "ko" else f'Second Context logo with the text “{h1}”'
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


def prep_korean(page):
    """한국어 원본에 canonical·hreflang·언어 전환만 추가한다. 본문은 건드리지 않는다."""
    p = os.path.join(R, page)
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'<link rel="canonical"[^>]*>\n(<link rel="alternate"[^>]*>\n)*', "", s)
    s = add_og(page, "ko", OG_RE.sub("", s))
    s = s.replace('<script src="assets/lang.js"></script>\n', '')
    s = re.sub(r'    <nav class="lang".*?    </nav>\n', "", s, flags=re.S)
    anchor = '<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">\n'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + f'<link rel="canonical" href="{url(page)}">\n' + head_links(page)
                  + '<script src="assets/lang.js"></script>\n')
    end = "    </nav>\n  </div>\n</header>"
    assert s.count(end) == 1
    s = s.replace(end, "    </nav>\n" + lang_nav(page, "ko") + "  </div>\n</header>")
    open(p, "w", encoding="utf-8").write(s)
    return s


COMMON = [
    ('<html lang="ko">', '<html lang="en">'),
    ('본문 바로가기', 'Skip to main content'),
    ('aria-label="Second Context 홈"', 'aria-label="Second Context home"'),
    ('aria-label="주요 메뉴"', 'aria-label="Main menu"'),
    ('(새 탭에서 열림)', '(opens in a new tab)'),
    ('30분 상담 예약하기', 'Book a 30-minute call'),
    ('30분 상담 예약', 'Book a 30-min call'),
    ('프로젝트 문의하기', 'Send a project inquiry'),
    ('30분 상담으로 시작합니다.', 'Start with a 30-minute call.'),
    # 2026-10-29 사진·비주얼 재구성
    ('<span class="ex-label">예시 산출물</span>', '<span class="ex-label">Example deliverable</span>'),
]

HOME = [
    ('<title>Second Context — 시장을 넘나드는 제품 디자인</title>', '<title>Second Context — Product design across markets.</title>'),
    ('미국 시장을 준비하는 한국 B2B SaaS 팀을 위한 제품 UX 진단과 디자인.',
     'Product UX reviews and design for Korean B2B SaaS teams preparing for the U.S. market.'),
    ('헬스케어 · 엔터프라이즈 · 복잡한 운영 워크플로', 'Healthcare · Enterprise · Complex operational workflows'),
    ('번역 중심 현지화', 'Translation-first localization'),
    ('화면 문구는 영어로 바꿨지만 온보딩이 국내 사용자를 전제로 설계되어, 첫 사용자가 제품의 가치를 이해하지 못합니다.',
     'The UI copy is now in English, but onboarding still assumes a Korean user, so first-time users don’t grasp the product’s value.'),
    ('처음 방문한 사용자가 가치를 이해하고 시작할 수 있는가?', 'Can a first-time user understand the value and get started?'),
    ('업무 방식 차이', 'Different ways of working'),
    ('핵심 워크플로가 현지 팀의 역할 분담과 승인 방식에 맞지 않아, 실제 업무에 쓰이지 않습니다.',
     'Core workflows don’t fit how local teams divide roles and handle approvals, so the product isn’t used in day-to-day work.'),
    ('핵심 업무 흐름이 목표 사용자의 실제 업무 방식에 맞는가?', 'Do core workflows match how target users actually work?'),
    ('<h3>구조와 문구</h3>', '<h3>Structure and wording</h3>'),
    ('메뉴 구조와 버튼 문구가 다음 행동을 분명하게 안내하지 못합니다.',
     'Menu structure and button labels don’t make the next step clear.'),
    ('화면의 구조와 문구가 다음 행동을 명확하게 안내하는가?', 'Do the screen structure and wording clearly guide the next action?'),
    ('우선순위 부재', 'No clear priorities'),
    ('고칠 것이 많아 보이지만, 출시 전에 무엇부터 해야 할지 정하지 못합니다.',
     'There seems to be a lot to fix, but the team can’t decide what to tackle first before launch.'),
    ('출시 전에 어떤 UX 문제부터 개선해야 하는가?', 'Which UX problems should be fixed first before launch?'),
    ('위 내용은 자주 나타나는 시행착오 유형을 설명하기 위한 예시입니다.',
     'The examples above illustrate common types of trial and error; they are not specific client cases.'),
    ('온보딩·핵심 작업·정보 구조·화면 문구', 'Onboarding, core tasks, information architecture, UI copy'),
    ('우선순위를 포함한 UX 진단 보고서', 'UX review report with priorities'),
    ('목표 사용자·업무 방식·현지화 가정', 'Target users, ways of working, localization assumptions'),
    ('상담 및 핵심 권고 요약', 'Consultation and a summary of key recommendations'),
    ('합의한 문제의 설계·프로토타입·개발 협업', 'Design, prototyping, and development collaboration on agreed problems'),
    ('범위에 맞춘 제품 디자인 결과물', 'Product design deliverables matched to the agreed scope'),
    ('비슷한 과제를 고민하고 계신가요?', 'Working through a similar challenge?'),
    ('제품과 현재 상황을 함께 살펴보겠습니다.', 'Let’s look at your product and where it stands today.'),
    ('협업 방식 보기', 'See how we work'),
    ('aria-label="경력 요약"', 'aria-label="Career summary"'),
    ('<span class="stat-label">완료한 프로젝트</span>', '<span class="stat-label">Projects completed</span>'),
    ('<span class="stat-label">함께 일한 글로벌·다국적 기업</span>', '<span class="stat-label">Global &amp; multinational companies worked with</span>'),
    ('<span class="stat-label">여행한 국가</span>', '<span class="stat-label">Countries visited</span>'),
    ('<p class="metric-value">35% 감소</p>', '<p class="metric-value">35% less</p>'),
    ('AI 보조 일정 워크플로에서의 수동 검증', 'Manual validation in the AI-assisted scheduling workflow'),
    ('제품과 목표 시장, 현재 고민하고 계신 과제를 알려 주세요. <span class="keep">협업할 범위를 함께 살펴보겠습니다.</span>',
     'Tell us about your product, your target market, and the challenges you’re working through. We’ll explore the right scope of collaboration together.'),
    # 2026-10-29 사진·비주얼 재구성
    ('<h1>새로운 <span class="hero-hl">시장</span>의 <span class="hero-hl">맥락</span>을, 제품의 다음 단계로.</h1>', '<h1>New <span class="hero-hl">market</span> <span class="hero-hl">context</span>, your product’s next step.</h1>'),
    ('사용자와 업무 환경의 차이를 이해하고, 제품 경험과 실행 우선순위를 함께 설계합니다.', 'We understand how your users and their work environments differ, then design the product experience and execution priorities with your team.'),
    ('>사례 살펴보기</a>', '>Explore our work</a>'),
    ('제품 대시보드가 띄워진 화면 앞에서 손짓으로 설명하며 팀의 디자인 논의를 이끄는 Rachel Cho', 'Rachel Cho leading a team design discussion, gesturing as she explains in front of a screen showing a product dashboard'),
    ('<h2>제품과 사람, 비즈니스를 함께 이해합니다.</h2>', '<h2>We understand products, people, and business—together.</h2>'),
    ('번역만으로는 제품이 현지에서 쓰이지 않습니다. 같은 제품도 시장과 사용자가 달라지면 일하는 방식, 제품을 이해하는 방식, 신뢰를 판단하는 기준이 함께 달라지고, 한국 시장에 맞춰 제품을 만들어 온 팀은 이 차이를 내부에서 발견하기 어렵습니다.', 'Translation alone won’t get your product used in a new market. When the market and users change, how people work, how they make sense of a product, and how they judge trust all shift too—and teams that built for the Korean market often find these differences hard to see from the inside.'),
    ('노트북을 사이에 두고 웃으며 제품 이야기를 나누는 세 사람', 'Three people smiling as they talk about a product over a laptop'),
    ('화이트보드에 그린 화면 흐름을 가리키며 팀에게 설명하는 사람', 'A person pointing to a screen flow drawn on a whiteboard while explaining it to the team'),
    ('좋은 판단이 팀의 실행으로 이어지도록.', 'So good decisions turn into team action.'),
    ('디자인은 화면을 만드는 데서 끝나지 않습니다. 설계 의도와 우선순위를 팀이 이해할 수 있는 말로 설명하고, 다음에 무엇을 할지 함께 정합니다.', 'Design doesn’t end with screens. We explain design intent and priorities in language the whole team can use, and decide together what happens next.'),
    ('사용자 영향·사업 중요도·구현 난이도로 우선순위의 이유를 설명합니다.', 'Explain the reasons behind priorities using user impact, business importance, and implementation effort.'),
    ('디자인 의도와 요구사항, 예외 상황을 개발 전에 정리합니다.', 'Document design intent, requirements, and edge cases before development.'),
    ('합의한 방향을 팀이 실행할 수 있는 다음 작업으로 나눕니다.', 'Break the agreed direction into next tasks the team can act on.'),
    ('경험한 제품과 맡은 역할', 'Products and roles'),
    ('회사의 배경과 Rachel이 맡은 역할을 나누어 적었습니다.', 'Each entry separates the company’s background from Rachel’s role.'),
    ('<p class="proof-field">헬스케어 SaaS</p>', '<p class="proof-field">Healthcare SaaS</p>'),
    ('<p class="proof-field">엔터프라이즈 모니터링</p>', '<p class="proof-field">Enterprise monitoring</p>'),
    ('<p class="proof-field">제품 현지화</p>', '<p class="proof-field">Product localization</p>'),
    ('<dt>회사 배경</dt>', '<dt>Company background</dt>'),
    ('<dt>Rachel의 역할</dt>', '<dt>Rachel’s role</dt>'),
    ('Y Combinator W21 출신으로 투자를 유치한 미국 홈헬스케어 스타트업', 'A venture-backed U.S. home healthcare startup from Y Combinator’s W21 batch'),
    ('파운딩 디자이너로 AI 일정 플랫폼의 제품 디자인을 이끌고, 회사의 첫 디자인 시스템을 만들었습니다.', 'Led product design for the AI scheduling platform as founding designer and built the company’s first design system.'),
    ('백신 운영을 지원하는 글로벌 제약사의 모니터링 플랫폼', 'A global pharmaceutical company’s monitoring platform supporting vaccine operations'),
    ('UX 디자인 에이전시를 통한 계약 Senior Product Designer로 AI 기반 인시던트 관리 경험을 설계했습니다.', 'Designed an AI-based incident management experience as a contract Senior Product Designer through a UX design agency.'),
    ('<dd>글로벌 테크 기업의 한국어 제품</dd>', '<dd>Korean-language products for a global tech company</dd>'),
    ('영국 제작 에이전시, 고객사의 한국·미국 팀과 6주 동안 UX 문구와 디자인 자산을 현지화했습니다.', 'Localized UX copy and design assets over six weeks with a U.K. production agency and the client’s Korea and U.S. teams.'),
    ('<h2>지금 제품에 필요한 도움부터 시작합니다.</h2>', '<h2>Start with the help your product needs now.</h2>'),
    ('팀에 필요한 범위로 함께합니다. 짧은 진단부터 제품 설계와 개발 협업까지, 현재 단계에 맞춰 시작할 수 있습니다.', 'We work at the scope your team needs. From a short review to product design and development collaboration, you can start where you are today.'),
    ('테이블에 둘러앉아 노트북 화면을 함께 보며 이야기하는 세 사람', 'Three people at a table talking while looking at a laptop screen together'),
    ('</span> 아래 화면은 서비스 결과물의 형태를 보여 주는 예시이며, 실제 프로젝트 결과가 아닙니다.', '</span> The screens below show what deliverables can look like. They are examples, not actual project results.'),
    ('UX 진단 예시', 'Example UX review'),
    ('제품의 가치를 설명하기 전에 입력부터 요청합니다.', 'Asks for input before explaining the product’s value.'),
    ('미국 사용자에게 없는 사업자등록번호를 요구합니다.', 'Requires a Korean business registration number that U.S. users don’t have.'),
    ('‘Submit’이 다음에 일어날 일을 알려 주지 않습니다.', '“Submit” doesn’t say what happens next.'),
    ('현지화 비교 예시', 'Example localization comparison'),
    ('<li>날짜·시간 표기 순서</li>', '<li>Date and time order</li>'),
    ('<li>이름 순서와 호칭</li>', '<li>Name order and honorifics</li>'),
    ('<li>문구 길이에 맞춘 버튼과 여백</li>', '<li>Buttons and spacing sized to the copy</li>'),
    ('사용자 흐름 설계 예시', 'Example user flow'),
    ('목록에서 문제를 고릅니다.', 'Pick an issue from the list.'),
    ('원인과 영향을 확인합니다.', 'Check the cause and impact.'),
    ('다음 행동을 확정합니다.', 'Confirm the next action.'),
    ('<dt>검토 범위</dt>', '<dt>Scope</dt>'),
    ('<dt>결과물</dt>', '<dt>Deliverable</dt>'),
    ('제품의 문제를, 구현할 수 있는 디자인으로.', 'From product problems to buildable design.'),
    ('합의한 문제를 사용자 흐름과 화면으로 설계하고, 프로토타입과 개발 협업까지 이어갑니다. 디자인 의도와 요구사항, 고려할 예외 상황을 함께 정리해 구현 과정의 해석 차이를 줄입니다.', 'We design agreed problems as user flows and screens, then carry them through prototyping and development collaboration. Documenting design intent, requirements, and edge cases together reduces differences in interpretation during implementation.'),
    ('<span class="vis-title">컴포넌트 상태 정의</span>', '<span class="vis-title">Component state definitions</span>'),
    ('<p class="st-name">기본</p>', '<p class="st-name">Default</p>'),
    ('<p class="st-name">오류</p>', '<p class="st-name">Error</p>'),
    ('<p class="st-name">비활성</p>', '<p class="st-name">Disabled</p>'),
    ('<span class="st-btn">보내기</span>', '<span class="st-btn">Send</span>'),
    ('! 이메일 형식을 확인해 주세요', '! Check the email format'),
    ('입력 테두리는 배경과 3:1 이상', 'Input border at 3:1 or more against the background'),
    ('색과 함께 문구로 원인 안내', 'Explain the cause in words, not just color'),
    ('왜 누를 수 없는지 함께 안내', 'Explain why it can’t be pressed'),
    ('노트북으로 작업하며 회의 테이블의 동료들에게 의견을 말하는 사람', 'A person working on a laptop while sharing a view with colleagues at a meeting table'),
    ('밝은 실내에서 의자에 앉아 미소 짓는 Rachel Cho', 'Rachel Cho smiling, seated in a bright room'),
    ('<h2>복잡한 문제를 함께 풀어가는 디자인 파트너.</h2>', '<h2>A design partner for working through complex problems together.</h2>'),
    ('Second Context를 이끄는 제품·UX 컨설턴트 Rachel Cho입니다. Y Combinator 출신으로 1,420만 달러의 투자를 유치한 미국 헬스케어 스타트업에서 파운딩 디자이너로 제품 디자인을 이끌었습니다. 글로벌 기업의 업무 시스템과 제품 현지화 경험을 바탕으로, 복잡한 문제를 진단하고 개선 우선순위부터 실제 설계까지 연결합니다.', 'I’m Rachel Cho, the product and UX consultant who leads Second Context. I led product design as a founding designer at a U.S. healthcare startup from Y Combinator that raised $14.2 million. Drawing on my experience with enterprise systems and product localization for global companies, I diagnose complex problems and connect them to clear priorities and real, working design.'),
    ('직접 학비를 마련하며 공부하고, 이민자로 새로운 언어와 문화 속에서 커리어를 쌓았습니다. 디지털 노매드로 여러 나라를 여행하며 서로 다른 배경과 관점을 이해해온 경험은, 제품이 쓰이는 맥락과 그 안의 사람을 살피는 바탕이 되었습니다.', 'I funded my own education and built my career as an immigrant, navigating a new language and culture. Traveling as a digital nomad taught me to understand different backgrounds and perspectives—and it shapes how I look at the context a product is used in, and the people within it.'),
    ('지금은 제품팀과 파운더의 고민을 함께 풀며, 이민자 커뮤니티와 주니어 디자이너의 새로운 출발도 돕고 있습니다. ADPList 멘토링과 Flexwork Pro의 UX·AI 제품 디자인 강의를 통해 경험을 나누고, 막막한 상황에서도 실행 가능한 다음 걸음을 함께 찾습니다.', 'Today, I work through challenges with product teams and founders, and help immigrant communities and junior designers make a fresh start. Through mentoring on ADPList and teaching UX and AI product design at Flexwork Pro, I share what I’ve learned and help people find a practical next step, even when the way forward feels unclear.'),
    ('노트북 앞에서 상대의 이야기를 들으며 대화하는 두 사람', 'Two people in conversation at a laptop, one listening closely to the other'),
    ('<h3 class="sr-only" id="services-cards-title">서비스별 예시 산출물</h3>', '<h3 class="sr-only" id="services-cards-title">Example deliverables by service</h3>'),
    ('<h3 class="sr-only" id="work-list-title">사례 목록</h3>', '<h3 class="sr-only" id="work-list-title">Case list</h3>'),
]

# 사례 문구: 홈 Work 요약과 사례 페이지(second-context-work.html)가 함께 쓰는 번역. 페이지에 있는 것만 적용한다
CASE_TEXT = [
    ('복잡한 업무와 새로운 사용 맥락을, 명확한 제품 경험으로.', 'Turning complex work and new contexts of use into clear product experiences.'),
    ('Second Context를 시작하기 전, Rachel Cho가 이전 경력에서 수행한 세 프로젝트입니다. 고객사 이름은 밝히지 않습니다.',
     'Three projects Rachel Cho delivered in previous roles, before starting Second Context. Client names are not disclosed.'),
    # 01 홈헬스케어
    ('미국 홈헬스케어 SaaS의 일정 관리 UX', 'Scheduling UX for a U.S. home healthcare SaaS'),
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
    ('파일럿에서 일정 계획 자신감 5.8 → 8.2', 'Schedule-planning confidence 5.8 → 8.2 in the pilot'),
    ('여러 개선이 함께 적용된 후 작업 시간 180초 → 60초', 'Task time 180 sec → 60 sec after several improvements were applied together'),
    ('AI 보조 일정 워크플로에서 수동 검증 35% 감소', 'Manual validation reduced by 35% in the AI-assisted scheduling workflow'),
    ('임상의 3,000명 이상이 사용하는 일정 추천 경험', 'Scheduling recommendation experience used by 3,000+ clinicians'),
    ('디자인 시스템을 개발자 23명 전원이 조직 표준으로 채택', 'Design system adopted by all 23 developers as the org-wide standard'),
    ('디자인 시스템 도입 후 릴리스 주기 50% 이상 단축', 'Release cycles accelerated by 50%+ after the design system was adopted'),
    # 02 운영 모니터링
    ('글로벌 제약사의 운영 모니터링·인시던트 관리 UX', 'Operations monitoring and incident management UX for a global pharmaceutical company'),
    ('많은 정보 속에서 심각도·영향 범위·조사 우선순위를 연결했습니다.',
     'Connected severity, scope of impact, and investigation priority across a large volume of information.'),
    ('8개 대시보드에 흩어진 정보를 심각도와 후속 영향 중심으로 다시 구조화해, 무엇부터 조사할지 먼저 판단할 수 있게 했습니다.',
     'Restructured information scattered across 8 dashboards around severity and downstream impact, so teams could first decide what to investigate.'),
    ('30분 <span aria-hidden="true">→</span><span class="sr-only">에서</span> 3분', '30 min <span aria-hidden="true">→</span><span class="sr-only"> to </span> 3 min'),
    ('<p class="metric-value">80% 단축</p>', '<p class="metric-value">80% faster</p>'),
    ('의사결정 지원 흐름과 신호 표시를 다시 설계한 뒤의 인시던트 분류(triage) 시간',
     'Incident triage time after redesigning decision-support workflows and signal display'),
    ('<p class="metric-value">40% 단축</p>', '<p class="metric-value">40% faster</p>'),
    ('개발자 내부 도구의 티켓 처리 시간 40% 단축', 'Developer internal-tool ticket processing time reduced by 40%'),
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
    ('프로젝트에서 보고된 인시던트 조사 시간 30분 → 3분', 'Incident investigation time 30 min → 3 min, as reported in the project'),
    ('프로젝트에서 보고된 인시던트 조사 시간', 'Incident investigation time reported in the project'),
    ('의사결정 지원 흐름 재설계와 신호 명확화 후 인시던트 분류(triage) 시간 80% 단축',
     'Incident triage time reduced by 80% after redesigning decision-support workflows and clarifying signals'),
    ('이해관계자 인터뷰 15회', '15 stakeholder interviews'),
    # 03 한국어 현지화
    ('글로벌 테크 기업의 한국어 제품 현지화', 'Korean product localization for a global tech company'),
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
    ('</span> 홈헬스케어 일정 관리</a>', '</span> Home healthcare scheduling</a>'),
    ('</span> 운영 모니터링</a>', '</span> Operations monitoring</a>'),
    ('</span> 한국어 현지화</a>', '</span> Korean localization</a>'),
    ('<dt>문제</dt>', '<dt>Problem</dt>'),
    ('<dt>내 역할</dt>', '<dt>My role</dt>'),
    ('<dt>핵심 설계 판단</dt>', '<dt>Key design decisions</dt>'),
    ('<dt>바뀐 화면과 흐름</dt>', '<dt>Screens and flows changed</dt>'),
    ('<dt>확인된 결과(산출물)</dt>', '<dt>Confirmed results (deliverables)</dt>'),
    ('<dt>확인된 결과</dt>', '<dt>Confirmed results</dt>'),
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
    ('<span class="wh-cap">01 일정 관리</span>', '<span class="wh-cap">01 Scheduling</span>'),
    ('<span class="wh-cap">02 우선 대응</span>', '<span class="wh-cap">02 Priority triage</span>'),
    ('<span class="wh-cap">03 한국어 현지화</span>', '<span class="wh-cap">03 Korean localization</span>'),
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
    ('<span class="wh-cap">01 일정 관리</span>', '<span class="wh-cap">01 Scheduling</span>'),
    ('<span class="wh-cap">02 우선 대응</span>', '<span class="wh-cap">02 Priority triage</span>'),
    ('<span class="wh-cap">03 한국어 현지화</span>', '<span class="wh-cap">03 Korean localization</span>'),
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
    ('각 단계의 산출물이 다음 단계의 판단 근거가 됩니다. 단계를 누르면 자세한 설명으로 이동합니다.', 'Each step’s deliverable informs the decisions in the next. Select a step to jump to its details.'),
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
    ('30분 상담 예약하기<span class="sr-only"> (새 탭에서 열림)</span></a>\n          </div>',
     'Book a 30-minute consultation<span class="sr-only"> (새 탭에서 열림)</span></a>\n          </div>'),
    # 2026-10-29 사진·비주얼 재구성
    ('<h1>지금 고민 중인 제품 이야기를 들려주세요.</h1>', '<h1>Tell us about the product challenge on your mind.</h1>'),
]


PATHS = [
    ('href="favicon.ico"', 'href="../favicon.ico"'),
    ('href="assets/', 'href="../assets/'),
    ('src="assets/', 'src="../assets/'),
]

TABLE = {PAGES[0]: HOME, PAGES[1]: APPROACH, PAGES[2]: CONTACT, PAGES[3]: WORK}
KEEP = re.compile(r'<!--i18n:keep-->.*?<!--/i18n:keep-->', re.S)  # 비교 자료처럼 두 언어에서 그대로 두는 부분

for page in PAGES:
    s = prep_korean(page)
    e = s.replace(f'<link rel="canonical" href="{url(page)}">', f'<link rel="canonical" href="{url(page, "en")}">')
    e = e.replace(lang_nav(page, "ko"), lang_nav(page, "en"))
    e = OG_RE.sub("", e)  # 한국어 Open Graph 태그는 빼고, 번역이 끝난 뒤 영어 title·description으로 다시 만든다
    # i18n:keep 영역은 번역하지 않고 그대로 둔다
    kept = KEEP.findall(e)
    for i, k in enumerate(kept):
        e = e.replace(k, f'@@KEEP{i}@@', 1)
    # 사례 문구는 이 페이지에 있는 것만 페이지 표에 더한다 (홈 요약·사례 상세가 같은 번역을 공유)
    table = TABLE[page] + [(ko, en) for ko, en in CASE_TEXT if ko in s and ko not in dict(TABLE[page])]
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
