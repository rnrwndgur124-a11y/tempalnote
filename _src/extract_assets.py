"""모든 페이지에 똑같이 들어 있는 큰 스타일·스크립트를 /assets/ 파일 하나로 빼서
페이지마다 다시 받지 않게(브라우저 캐시) 한다. 파일 이름에 내용 해시를 붙여 바뀌면 새로 받는다."""
import os, re, sys, hashlib, glob
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
A = os.path.join(OUT, 'assets'); os.makedirs(A, exist_ok=True)
pages = [p for p in glob.glob(os.path.join(OUT, '**', 'index.html'), recursive=True) if '/.git/' not in p and '/_src/' not in p and '/img/' not in p]
pages += [os.path.join(OUT, '404.html')] if os.path.exists(os.path.join(OUT, '404.html')) else []
STY = re.compile(r'<style>(.*?)</style>', re.S)
SCR = re.compile(r"<script>(\n\{\nconst \$=s=>document\.querySelector.*?)</script>", re.S)
found_css, found_js = {}, {}
for p in pages:
    s = open(p, encoding='utf-8').read()
    m = STY.search(s)
    if m and len(m.group(1)) > 20000: found_css.setdefault(m.group(1), []).append(p)
    m = SCR.search(s)
    if m: found_js.setdefault(m.group(1), []).append(p)
def name(body, ext):
    return 'site.' + hashlib.sha1(body.encode()).hexdigest()[:10] + ext if ext == '.css' else 'app.' + hashlib.sha1(body.encode()).hexdigest()[:10] + ext
keep = set(); done = 0
for body, ps in list(found_css.items()):
    fn = name(body, '.css'); keep.add(fn)
    open(os.path.join(A, fn), 'w', encoding='utf-8').write(body)
    for p in ps:
        s = open(p, encoding='utf-8').read()
        s = s.replace('<style>' + body + '</style>', f'<link rel="stylesheet" href="/assets/{fn}">', 1)
        open(p, 'w', encoding='utf-8').write(s); done += 1
for body, ps in list(found_js.items()):
    fn = name(body, '.js'); keep.add(fn)
    open(os.path.join(A, fn), 'w', encoding='utf-8').write(body)
    for p in ps:
        s = open(p, encoding='utf-8').read()
        s = s.replace('<script>' + body + '</script>', f'<script src="/assets/{fn}"></script>', 1)
        open(p, 'w', encoding='utf-8').write(s)
for f in os.listdir(A):
    if f not in keep and (f.startswith('app.') or f.startswith('site.')):
        os.remove(os.path.join(A, f))
sz = sum(os.path.getsize(os.path.join(A, f)) for f in keep)
print(f'assets: css {len(found_css)}종 · js {len(found_js)}종 → /assets ({sz//1024}KB, 페이지 {len(pages)}개)')
