"""사이트 전체 검색용 색인(/data/search.json)을 만든다.
index.html의 화면(section.view)마다 카드 제목과 본문을 뽑아, 검색창에서 카드 단위로 찾을 수 있게 한다."""
import json, os, re, sys
from bs4 import BeautifulSoup

SRC = '/home/claude/tempal/index.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
SKIP = {'privacy', 'terms', 'contact', 'backup', 'about'}

soup = BeautifulSoup(open(SRC, encoding='utf-8').read(), 'lxml')
items = []
seen = set()
for sec in soup.select('section.view[data-v]'):
    k = sec['data-v']
    if not k or k in SKIP:
        continue
    h1 = sec.find('h1')
    page = h1.get_text(' ', strip=True) if h1 else k
    for card in sec.select('.card'):
        if 'faq' in (card.get('class') or []):
            # 자주 묻는 질문은 질문마다 따로
            for q in card.find_all('h3'):
                a = q.find_next_sibling('p')
                t = q.get_text(' ', strip=True)
                x = a.get_text(' ', strip=True) if a else ''
                key = (k, t)
                if t and key not in seen:
                    seen.add(key)
                    items.append({'k': k, 'p': page, 't': t, 'x': re.sub(r'\s+', ' ', x)[:600], 'f': 1})
            continue
        h = card.find(['h3', 'h2'])
        if not h:
            continue
        t = h.get_text(' ', strip=True)
        if not t:
            continue
        key = (k, t)
        if key in seen:
            continue
        seen.add(key)
        body = card.get_text(' ', strip=True)
        body = re.sub(r'\s+', ' ', body)
        if body.startswith(t):
            body = body[len(t):].strip()
        items.append({'k': k, 'p': page, 't': t, 'x': body[:1500]})

# 자바스크립트 표(사냥터)도 색인
import subprocess
src = open(SRC, encoding='utf-8').read()
m = re.search(r'const HU=(\[\[.*?\]\]);', src, re.S)
if m:
    hu = json.loads(subprocess.run(['node', '-e', 'console.log(JSON.stringify(eval(process.argv[1])))', m.group(1)], capture_output=True, text=True, check=True).stdout)
    for h in hu:
        lv = h[0] if h[0] is not None else (h[4] if len(h) > 4 else None)
        note = re.sub(r'<[^>]+>', '', h[3] or '')
        items.append({'k': 'hunt', 'p': '레벨별 사냥터', 't': '사냥터 · ' + h[1], 'x': (f'Lv.{lv} · ' if lv else '') + h[2] + (' · ' + note if note else '')})

os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
p = os.path.join(OUT, 'data', 'search.json')
json.dump(items, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'search: 카드 {len(items)}개 → {p} ({os.path.getsize(p)//1024}KB)')
