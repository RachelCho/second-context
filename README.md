# Second Context

Rachel Cho의 제품 UX 컨설팅 Second Context 웹사이트입니다. 주소: https://second-context.com (한국어) · https://second-context.com/en/ (English)

- `docs/` — GitHub Pages로 배포되는 정적 사이트
- `tools/sync_from_portfolio.py` — 디자인 원본인 my-portfolio의 Second Context 페이지와 쓰이는 파일을 `docs/`로 옮기고(홈 → `index.html`), 영어 페이지까지 만듭니다
- `tools/build_en_pages.py` — 한국어 페이지에서 영어 페이지(`docs/en/`)와 canonical·hreflang·Open Graph 태그를 만듭니다 (sync가 마지막에 실행)

```
python3 tools/sync_from_portfolio.py ../my-portfolio docs
```

로컬 미리보기: `python3 -m http.server 8001 --directory docs` 후 http://127.0.0.1:8001/
