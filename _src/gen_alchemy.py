"""넥슨 확률 공개표(장비 연금)를 사이트용 작은 JSON으로 바꾼다.
입력: data/alchemy_raw.json  [[부위, 연금 종류, 슬롯, 결과, 확률], ...]
출력: <site>/data/alchemy.json
  {"at": 기준일, "parts": [...], "d": {부위: {종류: {슬롯: [[능력치, 단위, [[값, 확률], ...]], ...]}}}}
"""
import json, os, re, sys
from collections import OrderedDict

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'alchemy_raw.json')
rows = json.load(open(SRC, encoding='utf-8'))
ORDER = ['무기', '보조무기', '방어구', '목걸이 및 반지', '귀걸이 및 허리띠', '성검', '방패', '성배', '나침반']
d = OrderedDict()
for part, var, slot, res, p in rows:
    m = re.match(r'^(.+?) ([\d.]+)(%?)$', res)
    fam, val, unit = (m.group(1), float(m.group(2)), m.group(3)) if m else (res, 0.0, '')
    sl = d.setdefault(part, OrderedDict()).setdefault(var, OrderedDict()).setdefault(slot, OrderedDict())
    e = sl.setdefault(fam, [unit, []])
    e[1].append([int(val) if val == int(val) else val, round(float(p), 4)])
out = {'at': '2026-11-27', 'parts': [x for x in ORDER if x in d] + [x for x in d if x not in ORDER], 'd': {}}
for part in out['parts']:
    out['d'][part] = {v: {s: [[f, u, sorted(vals)] for f, (u, vals) in fams.items()] for s, fams in slots.items()} for v, slots in d[part].items()}
os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
dst = os.path.join(OUT, 'data', 'alchemy.json')
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'alchemy: 부위 {len(out["parts"])} · 줄 {len(rows)} → {dst} ({os.path.getsize(dst)//1024}KB)')
