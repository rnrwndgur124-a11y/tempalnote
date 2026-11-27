"""배포 전 자동 점검. 하나라도 실패하면 배포를 멈춘다(종료 코드 1).
1) 모든 페이지가 열리고, 화면이 하나 보이고, 내용이 있고, 자바스크립트 오류가 없는지 (PC·폰 크기)
2) 페이지 안의 모든 링크를 실제로 눌렀을 때 빈 화면이 뜨지 않는지 (#해시 링크 포함)
3) 다른 페이지를 돌아다녀도 내 기록(숙제·계산기·체크리스트)이 지워지지 않는지
4) 가로로 넘치는 화면이 없는지"""
import asyncio, os, re, sys, threading, functools, http.server, socketserver
from playwright.async_api import async_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
PORT = 8814
U = f'http://127.0.0.1:{PORT}/'
fails = []


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), functools.partial(Q, directory=OUT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def keys():
    ks = []
    for root, _, files in os.walk(OUT):
        if 'index.html' in files and '/img' not in root and '/.git' not in root:
            rel = os.path.relpath(root, OUT)
            ks.append('home' if rel == '.' else rel)
    return sorted(ks)


def path(k):
    return '' if k == 'home' else k + '/'


async def view_ok(pg, want=None):
    v = await pg.evaluate("(()=>{const s=document.querySelectorAll('section.view.on');return {n:s.length,v:s[0]?s[0].dataset.v:'',t:s[0]?s[0].innerText.length:0}})()")
    return v['n'] == 1 and v['t'] > 100 and (want is None or v['v'] == want), v


async def main():
    srv = serve()
    ks = keys()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h in [(1366, 900), (390, 844)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, timezone_id='Asia/Seoul', locale='ko-KR')
            await ctx.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
            hrefs = {}
            for k in ks:
                await pg.goto(U + path(k)); await pg.wait_for_timeout(450)
                ok, v = await view_ok(pg, k)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if not ok: fails.append(f'[{w}] {k}: 화면 이상 {v}')
                if sw > w + 1: fails.append(f'[{w}] {k}: 가로 넘침 {sw}px')
                if errs: fails.append(f'[{w}] {k}: JS 오류 {errs[:1]}'); errs.clear()
                for hr in await pg.evaluate("[...new Set([...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')))]"):
                    hrefs.setdefault(hr, k)
            # 링크 전부 확인
            for hr, k in sorted(hrefs.items()):
                if hr.startswith('#'):
                    t = hr[1:]
                    if not t or t not in ks:
                        continue
                    await pg.goto(U + path(k) + hr); await pg.wait_for_timeout(700)
                    ok, v = await view_ok(pg, t)
                    if not ok: fails.append(f'[{w}] {k} 페이지의 링크 {hr} → 빈 화면/엉뚱한 화면 {v}')
                elif hr.startswith('/') or hr.startswith('https://tempalnote.com/'):
                    rel = hr.replace('https://tempalnote.com', '').split('#')[0].split('?')[0]
                    f = os.path.join(OUT, rel.lstrip('/'))
                    if rel.endswith('/'): f = os.path.join(f, 'index.html')
                    if not os.path.exists(f): fails.append(f'{k} 페이지의 링크 {hr} → 없는 주소')
            if errs: fails.append(f'[{w}] 링크 이동 중 JS 오류 {errs[:1]}')
            await ctx.close()
        # 기록 유지
        ctx = await b.new_context(viewport={'width': 1366, 'height': 900})
        await ctx.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
        pg = await ctx.new_page()
        await pg.goto(U + 'trade/'); await pg.wait_for_timeout(400); await pg.fill('#tdPrice', '1234')
        await pg.goto(U + 'calc/'); await pg.wait_for_timeout(400); await pg.fill('#cP', '12')
        await pg.goto(U + 'homework/'); await pg.wait_for_timeout(400); await pg.locator('#hwList input[type=checkbox]').first.check()
        await pg.goto(U + 'starter/'); await pg.wait_for_timeout(400); await pg.locator('#ckList input').nth(1).check()
        for k in ks:
            await pg.goto(U + path(k)); await pg.wait_for_timeout(250)
        await pg.goto(U + 'trade/'); await pg.wait_for_timeout(400)
        if await pg.input_value('#tdPrice') != '1234': fails.append('다른 페이지를 다녀오면 거래 계산기 입력이 지워짐')
        await pg.goto(U + 'calc/'); await pg.wait_for_timeout(400)
        if await pg.input_value('#cP') != '12': fails.append('다른 페이지를 다녀오면 강화 계산기 입력이 지워짐')
        await pg.goto(U + 'homework/'); await pg.wait_for_timeout(400)
        if '오늘 1 /' not in (await pg.inner_text('#hwCnt')): fails.append('다른 페이지를 다녀오면 숙제 체크가 지워짐')
        await pg.goto(U + 'starter/'); await pg.wait_for_timeout(400)
        if not (await pg.inner_text('#ckCnt')).startswith('1 '): fails.append('다른 페이지를 다녀오면 첫 주 체크리스트가 지워짐')
        await ctx.close()
        await b.close()
    srv.shutdown()
    if fails:
        print('점검 실패 — 배포 중단'); [print(' -', f) for f in fails[:40]]; sys.exit(1)
    print(f'점검 통과: 페이지 {len(ks)}개 × PC·폰, 링크 전부, 기록 유지')

asyncio.run(main())
