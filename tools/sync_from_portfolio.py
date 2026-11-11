"""my-portfolio의 Second Context 페이지를 운영 사이트(docs/)로 옮긴다 (2026-11-11, 다크 리디자인 반영).

디자인·문구의 원본은 my-portfolio(second-context*.html, assets/, tools/sc_chrome.py)다. 그쪽에서 고치고
sc_chrome.py · build_en_pages.py를 실행한 뒤, 이 스크립트로 한국어 페이지와 쓰이는 파일만 docs/로 복사한다.

- second-context.html → docs/index.html, 홈 링크 second-context.html(#섹션) → ./(#섹션)
- 페이지가 실제로 쓰는 assets/ 파일(이미지·영상·CSS·JS)과 OG 이미지·파비콘만 복사한다(원본 PNG는 옮기지 않음)
- assets/lang.js는 운영 사이트 전용판(홈이 / · /en/ 폴더 주소)을 그대로 둔다
- docs/assets 안에서 더 이상 쓰지 않는 파일은 지운다(지운 목록을 출력)
- 마지막에 tools/build_en_pages.py docs로 영어 페이지·canonical·hreflang·OG 태그를 만든다

사용: python3 tools/sync_from_portfolio.py ../my-portfolio docs
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAGES = {
    "second-context.html": "index.html",
    "second-context-approach.html": "second-context-approach.html",
    "second-context-contact.html": "second-context-contact.html",
    "second-context-about.html": "second-context-about.html",
    "second-context-work.html": "second-context-work.html",
}
KEEP = {"assets/lang.js"}  # 운영 전용판 유지


def home_links(s):
    """홈 주소를 폴더 주소로: second-context.html#x → ./#x, second-context.html → ./"""
    s = s.replace('"second-context.html#', '"./#').replace('"second-context.html"', '"./"')
    return s.replace("'second-context.html#", "'./#").replace("'second-context.html'", "'./'")


def main(src, dst):
    src, dst = Path(src).resolve(), Path(dst).resolve()
    used = {"assets/second-context.css", "assets/favicon-32.png"}
    for name, out in PAGES.items():
        s = (src / name).read_text()
        # my-portfolio 빌드가 넣은 canonical·hreflang·OG·언어 링크는 build_en_pages.py가 운영 주소로 다시 만든다
        s = home_links(s)
        (dst / out).write_text(s)
        used |= set(re.findall(r'(assets/[A-Za-z0-9_./-]+\.[a-z0-9]+)', s))
    used |= {str(p.relative_to(src)) for p in (src / "assets" / "og").glob("*.png")}

    for rel in sorted(used - KEEP):
        f = src / rel
        if not f.exists():
            sys.exit(f"원본에 없는 파일: {rel}")
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".js"):
            (dst / rel).write_text(home_links(f.read_text()))
        else:
            shutil.copy2(f, dst / rel)
    shutil.copy2(src / "favicon.ico", dst / "favicon.ico")

    stale = [p for p in (dst / "assets").rglob("*")
             if p.is_file() and str(p.relative_to(dst)) not in used | KEEP and p.name != ".DS_Store"]
    for p in stale:
        print("지움:", p.relative_to(dst))
        p.unlink()

    subprocess.run([sys.executable, str(Path(__file__).with_name("build_en_pages.py")), str(dst)], check=True)
    print(f"복사한 assets {len(used - KEEP)}개, 지운 파일 {len(stale)}개")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../my-portfolio", sys.argv[2] if len(sys.argv) > 2 else "docs")
