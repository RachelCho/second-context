# Second Context

Rachel Cho의 제품 UX 컨설팅 Second Context 웹사이트입니다. 주소: https://second-context.com (한국어) · https://second-context.com/en/ (English)

- `docs/` — GitHub Pages로 배포되는 정적 사이트
- `tools/build_en_pages.py` — 한국어 페이지에서 영어 페이지(`docs/en/`)와 canonical·hreflang·Open Graph 태그를 만듭니다
- `tools/make_og_images.py` — 공유용 Open Graph 이미지를 만듭니다 (Google Chrome 필요)

```
python3 tools/build_en_pages.py docs
python3 tools/make_og_images.py docs
```

로컬 미리보기: `python3 -m http.server 8001 --directory docs` 후 http://127.0.0.1:8001/
