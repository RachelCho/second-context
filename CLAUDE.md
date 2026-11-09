# Second Context 운영 사이트

## 프로젝트 개요
- Second Context(Rachel Cho의 제품 UX 컨설팅) 운영 웹사이트. 도메인 https://second-context.com
- 2026-11-09 my-portfolio(수업·개인 포트폴리오 저장소)에서 분리했다. my-portfolio의 Second Context 페이지·링크·Pages 설정은 그대로 두고, 이후 운영 수정은 이 저장소에서 한다
- 저장소: https://github.com/RachelCho/second-context (공개). GitHub Pages는 main 브랜치의 docs/ 폴더를 배포하고, Custom domain은 second-context.com(docs/CNAME)

## 폴더 구조
- docs/ — 배포되는 파일만: 한국어 페이지, en/ 영어 페이지(빌드 결과), assets/(CSS·JS·로고·웹용 사진·OG 이미지), favicon.ico, 404.html, sitemap.xml, robots.txt, CNAME, .nojekyll
- tools/build_en_pages.py — 한국어 페이지의 canonical·hreflang·OG 태그·언어 전환을 넣고 번역 표로 docs/en/을 만든다(BASE = https://second-context.com/, 홈은 / 와 /en/)
- tools/make_og_images.py — OG 카드 이미지(하단 표기 second-context.com)
- 사진 원본 PNG와 웹용 사진을 만드는 도구(make_hero_images.py)는 my-portfolio에 남아 있다. 사진을 바꿀 때는 그쪽에서 만든 JPG를 docs/assets/images/로 복사한다
- 페이지나 경로를 추가하면 docs/sitemap.xml도 함께 고친다

## 작업 기준
- 화면 문구는 한국어 HTML과 tools/build_en_pages.py의 번역 표에서만 고치고, docs/en/*.html을 직접 고치지 않는다
- 작업 후 변경 사항과 실제로 확인한 결과를 설명한다. 실제 문의 전송·상담 예약은 시험하지 않는다(Formspree 요청은 가로채서 확인)
- 비밀키·토큰을 HTML·JS·Git에 넣지 않는다. Formspree 폼 주소는 공개용 주소다

## 브랜드·구현 규칙 (my-portfolio CLAUDE.md에서 옮김, 필수)
- 적용 대상: second-context.html, plan-draft.html, plan-draft.md 등 Second Context 관련 화면과 문서
- 포트폴리오(index.html)의 스타일 C 기준과 별개로 적용한다.
- 아래 컬러 토큰과 WCAG 2.2 AA 색상 대비 조건은 필수 디자인 규칙이다. 화면을 바꿀 때마다 hover·active·focus를 포함해 대비를 다시 계산한다.

### 확정 컬러 토큰
| 토큰 | HEX | 역할 |
|---|---|---|
| Primary / Context Plum | #30232E | 제목, 본문, Primary 버튼 |
| Secondary / Accessible Orange | #A83E20 | 기능성 강조, Secondary 버튼, 강조 글자 |
| Background / White | #FFFFFF | 기본 배경 (2026-10-28 크림에서 변경) |
| Neutral Surface | #F6F6F4 | 옅은 중립 면. 문의 폼처럼 꼭 필요한 영역에만 |
| Brand Cream | #F4F0E8 | 작은 브랜드 요소 전용: 플럼·오렌지 버튼 위 글자, 파비콘 바탕 |
| Surface / Soft Sage | #9DAE9A | 보조 배경, 정보 패널 |
| Decorative Accent / Signal Orange | #DA613E | 승인 로고, 순수 장식 선·그래픽 전용 |

### 접근성 필수 조건 (WCAG 2.2 AA 색상 대비)
- 일반 글자: 배경과 4.5:1 이상
- 큰 글자: 최소 3:1 이상, 브랜드 내부 목표는 가능하면 4.5:1 이상
- 식별에 필요한 아이콘·컨트롤 경계·상태 표시: 인접 색상과 3:1 이상
- 링크는 밑줄 등 색상 이외의 구분을 함께 제공
- 오류·성공·선택 상태는 문구나 아이콘을 함께 제공
- hover, active, focus 상태도 실제 배경과의 대비를 검증
- 키보드 포커스는 명확하게 보이고 다른 요소에 가려지지 않게 구현
- 색상 대비는 WCAG 기준의 일부입니다. 대비 검증만으로 사이트 전체가 WCAG를 충족한다고 표현하지 않습니다.

### 승인된 조합
| 글자 / 배경 | 대비 |
|---|---|
| 플럼 / 화이트 | 14.94:1 |
| 조정 오렌지 / 화이트 | 6.22:1 |
| 플럼 / 중립 면(#F6F6F4) | 13.81:1 |
| 조정 오렌지 / 중립 면(#F6F6F4) | 5.75:1 |
| 플럼 / 크림 | 13.15:1 |
| 크림 / 플럼 | 13.15:1 |
| 조정 오렌지 / 크림 | 5.48:1 |
| 크림 / 조정 오렌지 | 5.48:1 |
| 플럼 / 세이지 | 6.37:1 |
| 조정 오렌지 / 흰색 | 6.22:1 |
| Hero 강조 오렌지(--orange-on-dark #F0845C) / 홈 Hero 다크 합성 배경 | 5.93:1 이상 (2026-11-04 실측). 조정 오렌지와 같은 색 계열을 밝힌 값, 어두운 Hero 위 글자 전용·밝은 배경 금지 |

### 버튼
- Primary: 플럼 배경 + 크림 문구
- Secondary 채움: 조정 오렌지 배경 + 크림 문구
- Secondary 외곽선: 화이트 배경 + 조정 오렌지 문구·테두리. hover는 중립 면(#F6F6F4) 바탕(5.75:1), active는 중립 면 + #8A3219 문구·테두리(7.61:1). 채우지 않아 주요 버튼보다 가볍게 유지 (2026-11-05)

### 사용 금지 조합
- 플럼 ↔ 조정 오렌지 (약 2.40:1): 서로를 글자·배경이나 기능 식별용 경계로 조합하지 않는다
- 세이지 / 크림 (약 2.06:1): 글자나 기능성 아이콘에 쓰지 않는다
- 장식 오렌지 #DA613E: 글자·버튼·기능 요소에 쓰지 않는다

### 창업자 소개 (Founder)
- 사진(2026-10-29 갱신): 창업자 소개 페이지 히어로는 실제 프로필 assets/profile.jpg(웹용 assets/images/about-profile-*.jpg), 홈 #founder 미리보기는 AI 연출 인물 사진 founder-portrait-*.jpg(+ "AI로 연출한 이미지" 캡션). 흑백 rachel-portrait-bw.png는 현재 페이지에서 쓰지 않는다. 얼굴·외모를 편집하지 않고, 원본 비율을 유지하며 얼굴과 머리를 자르지 않는다
- 사진 아래 3줄: Rachel Cho / Founder & Product UX Consultant / Product Designer · Startup Strategy Coach · Career Mentor
- 구성(2026-10-29 갱신): 홈 #founder는 미리보기 — 작은 세로 사진 + 사진 아래 3줄 + 제목 "복잡한 문제를 함께 풀어가는 디자인 파트너." + 첫 문단(YC 파운딩 디자이너·글로벌 경력) + 경력 수치 + "창업자 소개 보기" 링크. 창업자 소개 페이지: 히어로 h1 "새로운 환경에서, 나만의 길을 만들어왔습니다." + 둘째 문단(학비·이민·노매드) → 경력(첫 문단 + 수치 + 확인된 사실만 쓴 타임라인 2019/2024/2025–2026/현재) → 멘토링(셋째 문단 + 멘토링 사진) → 커뮤니티(작은 사진 + 다양성·디자인 커뮤니티 참여). 세 문단은 문구를 바꾸지 않고 위치만 나눈다. 메뉴에는 About을 따로 두지 않는다
- 창업자 소개 통합(2026-10-29): 별도 페이지 second-context-about.html(한·영)은 홈 #founder로 옮겨 주는 안내 페이지(meta refresh + location.replace, noindex, 링크)만 남긴다. 홈 #founder = 인물 사진(4:5)·3줄 + 제목 "복잡한 문제를 함께 풀어가는 디자인 파트너." + 사용자가 준 세 문단(전문 경력 → 개인 여정 → 컨설팅·멘토링, 문구 그대로) + 경력 수치 카운트업. 창업자 소개 링크 없음. 투자 금액은 사용자가 확정한 1,420만 달러($14.2 million)를 회사 이력으로만 쓴다. 타임라인·커뮤니티 등 상세 내용은 현재 노출하지 않는다(아래 타임라인 기록은 자료로 보관)
- 홈 마지막 상담 섹션(#contact): .media-split — 왼쪽 라벨·h2 "30분 상담으로 시작합니다."·설명·버튼(Calendly 새 탭 / 문의 폼), 오른쪽 멘토링 사진 about-mentoring-session(4:3). 머리글 → 버튼 32px. 실제 고객 상담·멘토링 기록이라고 설명하지 않는다
- 창업자 소개 보강(2026-10-29, 출처: yeagyeong.com/about, 웹사이트용 이력서 2026-10-19본. LinkedIn은 로그인 없이 경력이 보이지 않아 쓰지 않음): 타임라인 2019 SVA BFA 일러스트레이션 · 2019 현지화 · 2023년 이전 그린피스·University of Florida·게이츠 재단 관련 교육 사이트(사용자 제공, 실명) · 2019–2020 VR 게임 스타트업 프로덕트 디자이너(사용자 제공, 회사명 없음) · 2020 General Assembly 프로그래밍 과정 수강(사용자 제공) · 2023 Aristocrat Gaming USA(호주 본사와 협업, 글로벌 애플리케이션, 사용자 제공, 실명) · 2024 제약사 · 2024 LA 물류 SaaS 중견기업 파운딩 디자이너(사용자 확인: 2024, 이력서의 2024–2025 대신)(글로벌 디스플레이 제조사 선박 추적 대시보드, React 디자인 시스템) · 2025–2026 YC 헬스케어 · 2026 Toptal을 통해 글로벌 기업들과 협업(사용자 제공, 실명) · 2026 Flexwork Pro 강사 · 현재. 멘토링 활동: ADPList 멘토(2024–2026, 40명 이상), Flexwork Pro UX 커리어 세미나(2026, 150명 이상 신청·약 60명 참석), AI 제품 디자인 과정 강사. 회사·고객사 이름은 익명(FNS·LG Display 포함), 학교·커뮤니티 이름은 실명
- 자료끼리 다른 값(확인 전까지 쓰지 않음): ADPList 순위(Top 10 vs TOP100), 멘티 취업 수(29+ vs 25+), 방문 국가(27 vs 21+), 현지화 연도(2019 vs 2020)
- 1인칭(나/저)으로 쓰고, '자수성가'·'역경 극복'·'글로벌 리더' 같은 수식어 대신 구체적 경험(직접 학비 마련, 이민자로 쌓은 커리어, 27개국 디지털 노매드)으로 보여준다. 확인되지 않은 어려움·감정·가족사·재정 상황은 덧붙이지 않는다
- 경력 수치(Rachel 제공): 40+ 완료한 프로젝트 / Projects completed · 12+ 함께 일한 글로벌·다국적 기업 / Global & multinational companies worked with · 27 여행한 국가 / Countries visited. 12+를 "약 12개"로 바꾸지 않고, 27은 여행한 국가 수로만 쓴다(일한 국가·시장 수 아님). 투자금은 개인 수치에 넣지 않는다
- 카운트업(assets/count-up.js): HTML에는 최종 값, 화면 60% 진입 시 세 숫자를 동시에 0→최종 값 900ms(ease-out), 방문당 한 번, 언어 전환으로 들어온 페이지에서는 다시 재생하지 않음(lang.js가 sc:counted 전달). 움직임 줄이기·IntersectionObserver 미지원이면 최종 값 그대로. 보이는 숫자는 aria-hidden, sr-only로 최종 값만 읽음, aria-live 없음. tabular-nums + 최종 자릿수만큼 폭 확보
- 회사명은 쓰지 않는다("Y Combinator W21 출신의 미국 헬스케어 스타트업"). 투자금은 회사의 이력이며 개인 성과로 쓰지 않고, 금액은 사용자가 2026-10-29에 1,420만 달러($14.2 million)로 확정했다($15M 표기는 쓰지 않는다)
- 기업 경험은 실제 참여 형태를 존중하고, 27개국은 개인 배경으로만 쓴다(27개 시장 업무·리서치로 바꾸지 않는다)
- 경력 수치는 창업자 소개에만, 프로젝트 개선 수치는 해당 사례(#work)에만 둔다. 프로젝트 성과를 Rachel 개인의 단독 성과로 쓰지 않는다
- 투자 유치를 다시 언급할 때는 회사의 이력으로만 쓴다. 멘토링을 언급할 때는 이민 법률 자격이나 법률 서비스 제공을 주장하지 않는다

### 페이지 구조와 구현 규칙
- 정적 HTML, GitHub Pages(저장소 RachelCho/second-context의 docs/ 폴더, 도메인 https://second-context.com). 페이지 링크·이미지는 상대 경로만 쓴다(404.html만 / 기준)
- 페이지(docs/): index.html(홈), second-context-approach.html, second-context-work.html, second-context-contact.html, 404.html. 영어는 docs/en/ 같은 이름. 홈으로 가는 링크는 ./ (영어 ../ · en/), 섹션은 ./#work 형태. 창업자 소개 안내 페이지(second-context-about.html)는 운영 사이트에 두지 않는다
- 공통 스타일은 assets/second-context.css 하나로 관리하고, 헤더·푸터·본문 바로가기는 세 페이지에 같은 구조로 둔다
- 현재 페이지 메뉴에는 aria-current="page"를 넣고 밑줄·굵기로도 표시한다
- 새 탭 링크에는 "(새 탭에서 열림)"을 화면 밖 텍스트(sr-only)로 붙인다
- 버튼은 최소 44×44px, 모바일(900px 이하)에서도 메뉴 링크를 숨기지 않고 줄바꿈한다
- Calendly는 새 탭으로 여는 직접 링크로만 연결한다 (Contact 페이지 일정표 임베드는 2026-10-28에 제거)
- Contact 페이지(2026-10-29 4차): 사진 없음(사용자 요청). 다른 페이지와 같은 머리글(라벨 Contact, h1 "지금 고민 중인 제품 이야기를 들려주세요.", .lead) → 폼 7 | 다른 연락 방법 5 (900px 이하 폼 → 다른 연락 방법). 폼 열을 px로 고정하지 않는다(1024~1280px에서 왼쪽 열이 눌려 깨졌던 원인). 같은 안내를 양쪽에 반복하지 않는다. 달력 임베드·사업장 주소·"무료"·"24시간 내 답변" 같은 확인되지 않은 약속 없음
- 문의 폼: 옅은 중립 면(--surface) 하나로 묶고, 입력은 흰 바탕 + 1px 테두리(--field-border, 화이트 대비 3.58:1)·높이 46px. 라벨→입력 8px, 필드 사이 20px, 문의 내용 160px. 데스크톱은 이름|이메일, 회사·제품명|제품 URL 두 열, 600px 이하 한 열
- 항목: 이름*(예: 홍길동)·이메일*(name@company.com)·회사 또는 제품명(회사명 또는 제품명)·제품 URL(https://yourproduct.com)·문의 내용*(제품 소개, 현재 어려운 점, 필요한 도움을 간단히 알려주세요.). 라벨은 항상 보이고, placeholder는 입력 예시로만 연한 회색(--placeholder #7A737C, 화이트 4.59:1). 날짜 항목은 없음
- 폼 동작은 assets/contact-form.js: 필수·이메일·URL 형식 검증, 오류를 aria-invalid·aria-describedby로 연결, 상태는 role=status, 전송 중 버튼 "전송 중… / Sending…"·중복 제출 방지, 실패 시 입력 유지·재시도, 서버 2xx 뒤에만 성공 표시와 초기화
- 문의 수신 주소: rachel.cho5257@gmail.com (2026-10-28 사용자 확인)
- Formspree 폼 주소: https://formspree.io/f/mwllbenr (공개용 주소, 비밀키 아님). second-context-contact.html의 data-endpoint에 넣고 빌드 스크립트로 영어 페이지에 복사된다
- 전송 서비스: Formspree. form의 data-endpoint에 https://formspree.io/f/<폼ID>를 넣으면 버튼이 켜진다. 보내는 항목 이름: name, email(Formspree가 Reply-To로 사용), company, product_url, message, _subject(메일 제목), language(어느 언어 페이지인지), _gotcha(스팸 방지 숨김 칸)
- 이메일: 주소는 mailto 링크(보조 수단) + "이메일 주소 복사 / Copy email" 버튼(클립보드 쓰기가 실제 성공했을 때만 완료 안내, 실패 시 선택 가능한 주소 칸 표시)
- 방문자 화면에는 연결 상태·개발 설정 안내를 쓰지 않는다. 버튼은 항상 플럼 단색 채움, 포커스 외곽선 유지. 기본 상태에서는 오류·상태 문구를 숨기고, 제출할 때만 보내는 중·성공·실패를 role=status로 알린다
- 문구: 보내는 중… / Sending… · 성공 "문의가 접수되었습니다. 남겨주신 이메일로 답변드리겠습니다." / "Thank you. Your inquiry has been received. I’ll reply to the email address you provided." · 실패 "전송하지 못했습니다. 작성하신 내용은 이 화면에 그대로 남아 있습니다. 다시 시도해 주세요." / "Your message couldn’t be sent. What you entered is still on this page. Please try again." (영구 저장을 암시하지 않음)
- 전송 주소는 form의 data-endpoint에만 넣는다. 비어 있으면 보내지 않고 실패 문구만 보인다(성공 표시 금지). data-endpoint가 비어 있는 상태로 배포하지 않는다. 비밀키를 HTML·JS·Git에 넣지 않는다. mailto로 폼 제출을 대신하지 않는다
- 성과 수치·고객 실적·매출 증가 등을 임의로 추가하거나 보장하지 않는다
- 파비콘: 승인 로고(Second context framed wordmark logo.png)의 두 열린 사각 프레임 심볼만 크림 배경 위에 사용한다. 워드마크·가운데 채움 네모는 넣지 않는다
  - 파일: favicon.ico(16·32·48px, 저장소 루트), assets/favicon-32.png(32×32)
  - 연결: 페이지마다 <title> 바로 아래에 상대 경로로 둔다(docs/favicon.ico, docs/assets/favicon-32.png)
    `<link rel="icon" href="favicon.ico" sizes="any">`
    `<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">`
  - 새 페이지를 만들면 같은 두 줄을 넣는다
- Open Graph(2026-11-03): 글자 중심 브랜드 카드 1200×630 PNG, assets/og/<home|approach|work|contact>-<ko|en>.png (흰 배경 · 승인 로고 · 라벨 조정 오렌지 · h1 플럼 · 장식 오렌지 선, 사진 없음). 이전 창업자 소개 주소는 홈 이미지를 쓴다
  - 태그는 tools/build_en_pages.py가 한국어·영어 페이지의 description 바로 아래에 만든다(title·description·canonical에서 생성, HTML에서 직접 고치지 않음). og:image는 공유 서비스용이라 절대 URL을 쓴다
  - 페이지의 라벨·h1을 바꾸면 `python3 tools/build_en_pages.py docs` 다음에 `python3 tools/make_og_images.py docs`로 이미지를 다시 만든다

### 레이아웃 간격 규칙 (공통 컨테이너)
| 역할 | 변수 | 데스크톱 (901px~) | 태블릿 (601~900px) | 모바일 (~600px) |
|---|---|---|---|---|
| 콘텐츠 최대 폭 | --max | 1200px | 1200px | 1200px |
| 좌우 여백 (공통 기준선) | --gutter | 32 | 32 | 16 |
| 섹션 위아래 | --section-y | 96 | 64 | 64 |
| 라벨 → 제목 | --gap-label | 16 | 16 | 16 |
| 제목 → 설명 문단, 짧은 주석 | --gap-lead | 24 | 24 | 24 |
| 제목·설명 → 본문 블록(카드 목록·두 열·CTA 줄) | --gap-block | 48 | 48 | 48 |
| 문단 ↔ 문단 | --gap-para | 24 | 24 | 24 |
| 패널 제목 → 내용 | --gap-sub | 16 | 16 | 16 |
| 두 열(사진·본문, 소개·문의, 단계 제목·설명) 사이 | --gap-split | 64 | 세로 쌓임 | 세로 쌓임 |
| 두 열이 세로로 쌓일 때 | --gap-stack | — | 32 | 32 |
| 카드 목록 사이 | --gap-grid | 24 | 24 | 24 |
| 카드·패널 안쪽 | --card-pad | 32 | 32 | 24 |
| 라벨 ↔ 값, 목록 항목 (반 단계) | --gap-tight | 4 | 4 | 4 |

- 모든 Second Context 페이지(Home·Approach·Contact)는 헤더·각 섹션·푸터에 같은 `.wrap` 컨테이너 하나만 쓴다. `.wrap`을 중첩하거나 페이지별로 좌우 padding을 따로 주지 않는다
- 배경이 화면 전체를 채우는 섹션도 배경은 `section`에, 내용은 안쪽 `.wrap`에 두어 같은 기준선에 맞춘다
- 간격은 assets/second-context.css의 변수만 쓰고, 값은 8 / 16 / 24 / 32 / 48 / 64 / 96px 간격 체계에서 고른다 (예외: --gap-tight 4px)
- 버튼 안쪽 여백: 기본 16·24px, 헤더 버튼 8·16px, 최소 높이 44px
- 창업자 소개는 홈 #founder에 있다 (운영 사이트에는 별도 창업자 소개 페이지가 없다)
- 머리글(.page-header): 라벨 + 제목(h1/h2) + 첫 소개 문단(.lead)을 하나로 묶는다. Home Hero·Why Us·Use Cases·Contact 안내, Approach·Contact 페이지 도입에 공통 적용 (한국어·영어 동일)
- 첫 소개 문단(.lead): 글자 20px(모바일 600px 이하 18px, --lead-size), 줄 높이 1.7, 굵기 400, 자간 0, 최대 너비 720px, 제목 → 문단 24px(--gap-lead), padding 0. 문단 기본 margin은 지우고 이 규칙으로만 간격을 준다
- 소개 문단 → 다음 콘텐츠: 64px(모바일 40px, --gap-after-lead). `.page-header + [class]` 규칙이 개별 블록의 margin-top보다 우선한다. 본문 중간 문단·카드 설명은 .lead를 쓰지 않는다
- Home Hero(2026-10-29 3차, 풀블리드): 사이트에서 Hero만 이미지 중심 다크 스타일. 사진(home-hero-team)이 화면 좌우 끝까지 채우고(cover, 둥근 모서리·테두리 없음), 텍스트는 .wrap 안 왼쪽 아래라 아래 섹션과 시작선이 같다. 높이 80svh에서 시작해 콘텐츠에 따라 늘어난다. 음영: 데스크톱은 왼쪽·아래 그라데이션, 900px 이하는 사진을 위쪽에 따로 크롭하고 텍스트 블록 뒤만 균일하게 어둡게(확대해도 대비 유지). 제목 흰색, 본문 #ECE7EB, 보조 #DDD5DB. 버튼: Primary 아이보리(크림) 채움 + 플럼 글자, Secondary 어두운 반투명 + 흰 테두리·글자, focus는 흰 외곽선 + 어두운 링. 600px 이하 버튼 세로 배치. 대비는 합성된 실제 배경 픽셀로 측정해 일반 4.5:1·큰 글자 3:1 이상 유지. 제목 "새로운 시장의 맥락을, 제품의 다음 단계로."(2026-11-04: '시장'·'맥락' 두 단어만 .hero-hl --orange-on-dark, 영어는 market·context) / 버튼 "프로젝트 문의하기"(문의 폼) · "사례 살펴보기"(#work). 사진 속 인물을 실제 CEO·고객으로 소개하지 않는다
- Home Hero 4차(2026-11-04, .hero-full--focus): 왼쪽 제목 · 오른쪽 인물. 흰 상의 인물이 중심 인물. 데스크톱(901px~)은 재구성 와이드 사진 home-hero-focus-wide(2304×1024, 얼굴 가로 67%, 빈 왼쪽은 원본 왼쪽을 반전·흐림으로 채움) + object-position 67% 30%로 화면 폭과 관계없이 얼굴이 ⅔ 지점. 텍스트 폭 min(600px, 50%), 음영은 왼쪽 0~50% 진하게 → 60%에서 0(얼굴 주변 음영 없음) + 오른쪽 위 모니터 살짝 낮춤. 900px 이하는 얼굴이 가운데인 4:3 사진 home-hero-focus(최대 60svh)를 위에 따로, 텍스트·버튼은 아래 플럼 바탕(겹침 없음). 두 사진 모두 tools/make_hero_images.py가 원본 "Startup leaders align around operations.png"에서 만들고, 중심 인물 밖은 밝기·채도를 낮춘다(얼굴·피부 편집 없음). 예전 home-hero-team-*.jpg는 Hero에서 쓰지 않음
- Home Hero 5차(2026-11-05, 대표 이미지 교체): 사용자가 준 assets/Product designer leading a studio critique.png(1774×887) — 복잡한 제품 화면(대형 화면·노트북 대시보드)을 바탕으로 팀의 디자인 논의를 이끄는 Rachel. 웹용은 tools/make_hero_images.py가 만든 assets/images/home-hero-rachel-design-review-<1280|1774>.jpg(데스크톱 2:1 원본 비율) · -tablet-<768|1152>.jpg(601~900px, 오른쪽 4:3, 16:10으로 표시) · -mobile-<640|987>.jpg(~600px, Rachel 얼굴·손·노트북에 가까운 4:3). 보정·원본보다 큰 확대 없음, 품질 86·4:4:4. 한국어·영어 홈이 같은 파일을 쓴다. 데스크톱 object-position 75% 30%(얼굴 가로 ¾, 손 ⅔), 음영은 왼쪽 그라데이션 하나(0~53% 진하게 → 62%에서 0, 위·아래·오른쪽 음영 없음). 글 상자 min(600px, 48%), 영어는 901px 이상에서 53%·h1 12.5em으로 제목 두 줄. 이전 home-hero-focus-*.jpg는 쓰지 않는다
- Approach·Work Hero(2026-10-29): 홈과 같은 풀블리드 다크 Hero(.hero-full). Approach(.hero-full--low)는 approach-brainstorming 사진을 전체 폭으로, 인물 얼굴·유리벽 스케치가 위에 보이도록 텍스트를 아래에 두고 음영은 주로 아래쪽. 원래 Hero에 있던 강조 문장은 6단계 섹션 맨 앞으로 옮겼다. Work(.hero-full--plain)는 사진 없이 다크 배경 + 재구성 제품 화면 미리보기(연출 사진을 프로젝트 증거로 쓰지 않는 규칙), 사례 바로가기 링크는 흰 글자. 대비는 합성 배경 픽셀로 측정
- 홈 Services·Work Hero 띠(2026-10-29, .hero-full--band): 섹션 첫머리를 화면 전체 폭 다크 띠로. Services 띠는 가로 사진 services-product-discussion을 배경으로(세로 사진은 띠에서 얼굴이 텍스트와 겹쳐서 개발 협업 블록으로 옮김, 4:3), Work 띠는 사진 없이 재구성 제품 화면 미리보기. 띠 다음 내용은 .section-after-band(위 구분선 없음). #services·#work 앵커는 띠에 둔다. 대비 측정은 전체 페이지 캡처 대신 요소를 화면 안으로 스크롤해 측정(전체 캡처는 vh가 바뀌어 위치가 어긋남)
- 창업자 소개 그리드: 사진 열 --founder-photo 340px(320~360 범위) + 열 사이 --gap-split 64px + 본문은 남은 너비(본문에 별도 max-width를 두지 않음). 위쪽 정렬, 사진은 원본 비율, 900px 이하에서 세로 배치(사진 최대 440px)
- 사진·비주얼(2026-10-29): 사용자가 준 AI 연출 사진 11장의 웹용 사본은 assets/images/<영문-소문자-하이픈>-<폭>.jpg(가로 768/1152/1536, 세로 560/1122, JPEG 84·4:4:4)이고 srcset·sizes·width/height를 둔다. 원본 PNG(assets/)는 지우지 않는다. 첫 화면 히어로만 fetchpriority="high", 나머지는 loading="lazy"
- AI 연출 사진에 캡션을 붙이지 않는다(2026-10-29 사용자 요청으로 모든 "AI로 연출한 이미지" 표시 제거). 사진을 실제 고객·직원·행사·프로젝트 수행 증거처럼 설명하지 않는다
- 사진 배치: 홈 Hero(home-hero-rachel-design-review, 2026-11-05) · Why Us 머리(why-us-meeting) · Why Us 리더십(why-us-leadership) · Services 머리(services-collaboration, 세로 원본을 4:3로, object-position 50% 30%) · Services 개발 협업(services-product-discussion) · 홈 #founder(founder-portrait) · Approach 히어로(approach-brainstorming) · Approach 우선순위(approach-priority-meeting, 아래에 매트릭스) · 창업자 소개 멘토링(about-mentoring-session) · 커뮤니티(about-values-community). Contact에는 사진을 두지 않는다
- 공통 레이아웃(2026-10-29 통일, 새 화면도 이것만 쓴다):
  - .media-split: 장면 사진 + 글, 두 열 1:1, 사이 --gap-split, 세로 가운데. 사진은 .frame-photo(4:3, object-fit: cover, 기본 50% 50%). 900px 이하는 항상 글 → 사진. 같은 섹션 안 다음 블록은 64px(모바일 48px)
  - .profile-split(--end): 인물 사진 열 --profile-w 320px, .frame-profile 4:5 cover(object-position 50% 25%), 사진 아래 3줄. 900px 이하는 사진 → 글
  - .frame-product·.vis·.thumb·.demo: 제품 화면·사례 데모는 cover로 자르지 않고 원본 비율·내용 그대로
  - 글자 위계 토큰: --fs-display 48(1100px 이하 40, 600px 이하 34) 페이지 h1 · --fs-h2 36(28) 섹션 제목 · --fs-h3 24(22) 하위 제목·사례·단계 제목 · --fs-h4 20 항목·카드 제목 · --fs-stat 30(26) 수치. 페이지별로 h1·h2 크기를 따로 덮어쓰지 않는다
  - 한 줄로 읽혀야 하는 짧은 문장(홈 Work 제목, Approach 6단계 강조 문장)은 .text-wide로 읽기 폭 제한을 풀어 데스크톱에서 한 줄로. 좁은 칸에서 줄 끝에 갈리면 안 되는 구(상담 설명의 "협업할 범위를 함께 살펴보겠습니다.")는 .keep(601px 이상 한 덩어리). 문장을 별도 문단으로 나누지 않는다(2026-10-29 사용자 요청)
  - 간격·줄 간격(2026-10-29 실측 점검 후 통일): 라벨 → 제목 16 · 제목 → 소개 문단 24 · 머리글 → 다음 블록 64(모바일 40) · 소제목(24px) → 설명 24 · 항목 제목(20px) → 설명 8 · 사례 제목 → 한 줄 강점 8 · 소개 문단 → 그 블록 24 · 버튼 줄 앞 32(--gap-cta, 머리글·사진+글 안 포함) · 버튼 ↔ 버튼 32(.cta·.cta-row gap --s4, 2026-11-04 16에서 변경, 줄바꿈·세로 배치 때도 32) · 사진+글 블록 앞뒤 64(모바일 48, --after-split) · 문단 ↔ 문단 24 · 목록 항목 8 · 정의 목록 라벨 → 값 4, 값 → 다음 라벨 16(사례 상세는 24) · 섹션 위아래 96(모바일 64, 사례 섹션 포함). 줄 간격: 본문 17px 1.7(--lh-body) · 작은 글 12~15px 1.6(--lh-small) · 수치 1.25(--lh-stat) · 라벨 1.4. 예시 화면·데모 안의 UI 글자는 제외
  - 예전 그리드(.hero-grid, .intro-grid, .split, .svc-intro, .about-hero, .values-grid, .founder-preview, .prio-grid, .wide-media, .founder)는 지웠다. 되살리지 않는다
- 홈 서비스 카드(.svc-card, 2026-11-05): 예시 화면 / 캡션 / 제목 / 정의 목록 네 행을 subgrid로 함께 써서 예시 화면 높이·캡션 시작선을 맞춘다. 데스크톱 3열 · 601~900px 2열 · 600px 이하 1열
- 사진이 없는 곳은 HTML/CSS 비주얼: 서비스별 예시 산출물(UX 진단 주석 화면 · 현지화 비교(i18n:keep) · 사용자 흐름 3화면), 개발 협업 컴포넌트 상태(기본·오류·비활성), Why Us 경력(회사 배경 vs Rachel의 역할), Approach 6단계 프로세스 다이어그램(데스크톱 6열 → 1100px 이하 3열 → 600px 이하 세로)과 우선순위 매트릭스, 홈 Work·사례 페이지 히어로의 재구성 화면 미리보기, 창업자 소개 타임라인. 예시 산출물에는 "예시 산출물" 표시와 "실제 프로젝트 결과가 아님" 안내를 붙이고, 예시로 성과를 만들지 않는다
- 읽기 너비(--text 720px)는 컨테이너가 아니라 안쪽 요소(.lead, h2, 기획서의 .body > *)에만 건다. `.wrap`과 폭 제한 클래스를 같은 요소에 같이 쓰지 않는다 — 섹션 전체가 가운데로 밀린다
- overflow-x: hidden으로 넘침을 가리지 않는다. 고정 높이는 헤더·버튼 최소 높이, 장식 선에만 쓴다
- 기획서(plan-draft.html)는 자체 CSS를 쓰되 같은 이름의 변수(--gutter·--section-y·--gap-*·--card-pad·--founder-photo)로 같은 규칙을 따른다. 기획서 섹션 위아래는 64px(모바일 48px)

### Selected Work (홈 #work, 메뉴 이름 Work)
- 세 사례는 Rachel의 이전 경력 프로젝트로 소개한다. Second Context가 수주한 고객 프로젝트처럼 쓰지 않는다 (소개 문단: "Second Context를 시작하기 전, Rachel Cho가 이전 경력에서 수행한 세 프로젝트입니다. 고객사 이름은 밝히지 않습니다.")
- 공개 페이지에는 회사·협업사·제품 이름(고객사, 에이전시, 협업 IT 기업, 제품명)과 로고를 넣지 않는다. 제목은 01 미국 홈헬스케어 SaaS의 일정 관리 UX · 02 글로벌 제약사의 운영 모니터링·인시던트 관리 UX · 03 글로벌 테크 기업의 한국어 제품 현지화
- 홈 사례 구조: 왼쪽 번호·분야·연도·제목(h3)·강점 한 줄 | 오른쪽 핵심 설계 판단 → 대표 수치(.metrics) → "사례 자세히 보기" 링크(second-context-work.html#case-…)
- 사례 페이지 second-context-work.html: 사례마다 문제 / 내 역할 / 핵심 설계 판단 / 바뀐 화면과 흐름 / 확인된 결과 | 재구성 화면 + 3단계 인터랙션(assets/case-demo.js). 데스크톱(1101px~)은 화면이 따라 내려오고, 900px 이하는 화면을 먼저 보여 준다
- 재구성 화면: "설계 설명을 위한 재구성 · 예시 데이터"를 작게 표시하고, 예시 데이터는 "예시 환자 A·예시 인시던트 A"처럼 실제 데이터로 보이지 않게 쓴다. 자료에 있는 설계 판단만 보여 주고 새 기능·결과를 만들지 않는다
- 인터랙션: 단계 버튼(aria-current="step", 좌우 화살표), 모션 재생·정지·다시 보기(사용자가 시작, 마지막 단계에서 한 번 멈춤), 사례끼리 상태 공유 없음, 움직임 줄이기 설정에서는 전환 효과 없이 단계 이동만. 언어를 바꾸면 lang.js가 각 사례의 단계를 넘겨 준다
- 사례 02(운영 모니터링)는 데모 두 개를 탭 "우선 대응 판단 / AI 예측 요약"으로 하나씩 보여 준다(2026-10-29 위아래 배치 → 같은 날 사례가 길어져 탭으로 변경, 카루셀·자동 전환 없음, 탭을 바꾸면 재생 중지, 언어 전환 시 고른 탭 유지). 근거: Toptal-2CS-Axle-Pfizer-60min.pdf. A "먼저 대응할 문제를, 먼저 보이게." — 여러 알림 → 기술 신호(이상 점수)+업무 영향(막힌 팀·담당자)으로 P1을 맨 위로(순서 이동은 시연, 실제 화면은 처음부터 이 순서) → 항목 클릭 시 영향받는 팀·관련 신호·담당자·기록. B "과거의 기록에서, 다음에 주의할 신호를." — 프로젝트에서 연결한 관련 기록 수집 → 반복 패턴 → 목록 위 AI 요약(관찰 / 예측 / 근거, '관련 기록 보기'로 근거 펼침). 예측은 가능성으로만 쓰고, 정확도·신뢰도 %·데이터 규모·예측 시간·자동 대응을 만들지 않으며, 성과 수치를 데모 하나의 결과로 연결하지 않는다
- 한 데모를 재생하면 다른 데모의 재생은 멈춘다. 언어 전환 시 lang.js가 데모별 단계·선택 항목(data-sel)·펼침 상태를 넘긴다
- 현지화 비교 화면은 <!--i18n:keep--> 안에 두어 두 언어 페이지에서 원문·한국어를 그대로 유지한다. 실제 프로젝트 화면이 아닌 예시 문구임을 표시한다
- 대표 수치는 숫자 바로 옆에 지표 종류(사용자 평가·업무 성과·도입 범위·리서치 범위·프로젝트 기간)와 어떤 변화의 결과인지를 함께 쓴다. 숫자만 나열하지 않는다
- 기존 수치와 단위를 그대로 유지한다. 요약하면서 지우거나 "효율 개선"처럼 모호하게 바꾸지 않고, 서로 다른 지표를 합치지 않으며, 새 수치나 근거 없는 인과관계를 넣지 않는다
- 수치 출처는 공개 자료만: 이전 사이트 사례(4d60b08), 웹사이트용 이력서 PDF, yeagyeong.com 홈 카드. 자료끼리 값이 충돌하면 둘 다 보존하고 사용자에게 검토 항목으로 알린다
- 세 사례 아래 공통 마무리: "비슷한 과제를 고민하고 계신가요?" + [30분 상담 예약하기](Calendly) [협업 방식 보기](Approach)
### 다국어 (한국어·영어)
- 기본 언어는 한국어. 한국어 URL은 그대로 두고, 영어는 en/ 폴더에 같은 파일 이름으로 둔다 (en/second-context.html, en/second-context-approach.html, en/second-context-contact.html)
- 첫 방문은 한국어. 브라우저 언어·접속 국가에 따른 자동 이동을 하지 않는다. 실시간 번역 API를 쓰지 않는다
- assets/lang.js(모든 페이지 head, 빌드 스크립트가 넣음): 언어 링크를 누르면 선택을 localStorage에 기억하고, 영어를 고른 뒤 한국어(기본) 주소로 다시 오면 같은 페이지의 영어판으로 이어 준다. 전환할 때 보던 영역(섹션·사례 id 기준), 펼친 사례(details id), 작성 중인 문의 입력을 sessionStorage로 넘겨 복원한다. 저장이 막혀도 페이지는 그대로 동작한다
- 사례·펼침 id는 언어와 무관하게 고정: case-healthcare · case-monitoring · case-localization (+ -detail)
- 헤더 오른쪽에 언어 링크 "한국어 / EN"(국기·스위치 금지, EN은 화면 밖 텍스트 English로 읽힘). `<nav class="lang">`, 현재 언어는 aria-current="true" + 굵기·밑줄, 각 링크에 lang·hreflang, 누르는 영역 44×44px 이상. 1100px 이하에서도 첫 줄(로고 옆)에 둔다
- 언어 링크는 현재 페이지의 다른 언어 페이지로 연결하고, 각 언어의 내부 링크는 같은 언어 페이지로만 연결한다 (선택 언어 유지)
- 페이지마다 html lang, title, description, canonical(자기 언어 URL), hreflang ko·en·x-default(한국어)를 둔다. 한국어 title은 한국어(Second Context — 시장을 넘나드는 제품 디자인 / 협업 방식 / 문의)
- 번역 관리: 화면 문구는 한국어 HTML(원본)과 tools/build_en_pages.py의 번역 표 한 곳에서만 관리하고, 폼·복사 안내 메시지는 assets/contact-form.js 안의 ko/en 묶음에서 관리한다. en/*.html을 직접 고치지 않는다
- 실제 제품 스크린샷을 넣을 때는 화면 속 문구를 번역용으로 바꾸지 않고, 주석·설계 포인트·해설만 HTML 텍스트로 두어 번역 표로 전환한다
- 영어 페이지는 한국어 페이지에서 만든다: 한국어 문구를 고친 뒤 `python3 tools/build_en_pages.py docs`를 실행하고, 새 문구는 스크립트의 번역 표에 추가한다. 표에 없는 한국어가 남으면 스크립트가 멈춘다
- 이름·브랜드명·숫자(40+, 12+, 27, 사례별 수치와 단위)·서비스 범위를 그대로 유지한다
- 메뉴 표기: Why Us · Services · Work · Approach · Contact (두 언어 공통, 대문자 강제 변환 없음)
- 헤더는 1100px 이하에서 두 줄(로고·언어 / 메뉴), 그 위에서는 한 줄. 영어 길이 때문에 버튼·메뉴를 고정 폭·고정 높이로 자르지 않는다
- Calendly 예약 화면의 언어는 Calendly 쪽 설정을 따르며 사이트 번역 범위가 아니다

### 공식 기준
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
- https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
