"""빌드된 페이지를 브라우저로 한 번 열어, 자바스크립트가 채우는 목록(제작 도감, 방송인 서버, 버그 목록, 메뉴 등)을
HTML 안에 미리 넣어 둔다. 네이버처럼 자바스크립트를 잘 안 돌리는 검색로봇도 내용을 읽을 수 있게 하기 위함.
채워 넣은 뒤 다시 열어 화면이 똑같은지 확인하고, 다르게 나오는 칸은 넣지 않는다."""
import asyncio, re, os, sys, threading, functools, http.server, socketserver
from playwright.async_api import async_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
PORT = 8813
SKIP = {'toast', 'sres', 'hwDate', 'ownerStat', 'cdmBody', 'slotList'}
EMPTY = re.compile(r'<(\w+)((?:\s[^<>]*?)?\sid="([A-Za-z0-9_-]+)"[^<>]*)></\1>')


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Q, directory=OUT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def pages():
    for root, _, files in os.walk(OUT):
        if 'index.html' in files and '/img' not in root and '/.git' not in root:
            rel = os.path.relpath(root, OUT)
            yield ('' if rel == '.' else rel + '/'), os.path.join(root, 'index.html')


def inject(html, filled):
    def sub(m):
        i = m.group(3)
        return f'<{m.group(1)}{m.group(2)}>{filled[i]}</{m.group(1)}>' if i in filled else m.group(0)
    return EMPTY.sub(sub, html)


async def grab(ctx, path, ids):
    pg = await ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
    await pg.goto(f'http://127.0.0.1:{PORT}/{path}')
    await pg.wait_for_timeout(900)
    got = await pg.evaluate('ids=>Object.fromEntries(ids.map(i=>{const e=document.getElementById(i);return [i,e?e.innerHTML:null]}))', ids)
    await pg.close()
    return got, errs


async def main():
    srv = serve()
    total = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for path, f in pages():
            src = open(f, encoding='utf-8').read()
            ids = [m.group(3) for m in EMPTY.finditer(src) if m.group(3) not in SKIP]
            if not ids:
                continue
            ctx = await b.new_context(timezone_id='Asia/Seoul', locale='ko-KR', viewport={'width': 1366, 'height': 900})
            first, errs = await grab(ctx, path, ids)
            filled = {i: v for i, v in first.items() if v and v.strip() and len(v) < 600000 and '</script' not in v}
            await ctx.close()
            if errs:
                print('skip (js error)', path, errs[:1]); continue
            open(f, 'w', encoding='utf-8').write(inject(src, filled))
            # 다시 열어 같은지 확인 → 다르면 그 칸은 빼고 다시 쓴다
            ctx = await b.new_context(timezone_id='Asia/Seoul', locale='ko-KR', viewport={'width': 1366, 'height': 900})
            second, errs2 = await grab(ctx, path, ids)
            await ctx.close()
            bad = [i for i in filled if second.get(i) != first.get(i)]
            if errs2 or bad:
                for i in bad:
                    filled.pop(i)
                open(f, 'w', encoding='utf-8').write(inject(src, filled) if not errs2 else src)
            total += len(filled)
            print(f'{path or "/":12s} filled {len(filled):2d}' + (f'  dropped {bad}' if bad else '') + (f'  ERR {errs2[:1]}' if errs2 else ''))
        await b.close()
    srv.shutdown()
    print('prerendered blocks:', total)

asyncio.run(main())
