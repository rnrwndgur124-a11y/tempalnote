"""넥슨 공식 확률표(아이템 상자 · 분해 · 베니스의 행운 상자 · 펫 주얼 소환)에서
아이템별 획득처와 펫 주얼 목록을 뽑아 /data/codex.json 으로 만든다.
페이지(도감)는 이 파일 + index.html 안의 CRAFT · CLS · GM · PETS · TITLES · WMOD 를 합쳐서 보여 준다."""
import json, re, os, sys, collections

SRC = '/home/claude/tempal/data/prob_items.json'
OUT = (sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site') + '/data/codex.json'
v = json.load(open(SRC, encoding='utf-8'))

def norm(n):
    n = re.sub(r'\s*x\d+$', '', n.strip())
    return n.replace('(귀속)', '').strip()

def pf(p):
    p = float(p)
    if p >= 10: s = f'{p:.1f}'.rstrip('0').rstrip('.')
    elif p >= 0.1: s = f'{p:.2f}'.rstrip('0').rstrip('.')
    elif p >= 0.001: s = f'{p:.4f}'.rstrip('0').rstrip('.')
    else: s = f'{p:.2g}'
    return s + '%'

src = collections.OrderedDict()   # name -> {'g':grade, 'b':bound, 's':[[label, text]]}
def add(name, label, text, grade=None, bound=None):
    k = norm(name)
    if not k or k == '추가 획득 없음': return
    o = src.setdefault(k, {'s': []})
    if grade and grade not in ('', '특별') and 'g' not in o: o['g'] = grade
    if bound is not None: o['b'] = 1 if (o.get('b', 1) and bound) else 0
    if [label, text] not in o['s']: o['s'].append([label, text])

# 1) 아이템 상자: 상자 → 결과
box = collections.defaultdict(lambda: collections.defaultdict(float))
grades = {}
for _, _, b, g, item, p in v['아이템 상자']['rows']:
    box[norm(b)][item] += float(p); grades[norm(item)] = g
for b, items in box.items():
    agg = collections.defaultdict(lambda: [0.0, []])
    for item, p in items.items():
        k = norm(item); agg[k][0] += p
        m = re.search(r'x(\d+)$', item.strip()); agg[k][1].append(int(m.group(1)) if m else 1)
    for k, (p, qs) in agg.items():
        q = f' (×{min(qs)}~{max(qs)})' if min(qs) != max(qs) else (f' (×{qs[0]})' if qs[0] > 1 else '')
        add(k, b, pf(p) + q, grades.get(k), True)

# 2) 분해: 구분(노멀 장비 · 에픽 무기 …)별로 강화 구간 확률 범위
dis = collections.defaultdict(lambda: collections.defaultdict(float))   # (구분, 상세) -> item -> p(1개 이상)
for _, cat, det, res, p in v['아이템 분해']['rows']:
    for part in res.split(','):
        k = norm(part)
        if k and k != '추가 획득 없음': dis[(cat, det)][k] += float(p)
rng = collections.defaultdict(lambda: collections.defaultdict(list))
for (cat, det), items in dis.items():
    for k, p in items.items(): rng[k][cat].append(min(100.0, p))
for k, cats in rng.items():
    for cat, ps in cats.items():
        a, b = pf(min(ps)), pf(max(ps))
        add(k, f'{cat} 분해', a if a == b else f'{a} ~ {b} (강화 높을수록 ↑)', None, True)

# 3) 베니스의 행운 상자 (단계별)
lk = collections.defaultdict(lambda: collections.defaultdict(float))
for _, _, step, g, item, p in v['베니스의 행운 상자']['rows']:
    lk[norm(item)][step] += float(p)
    if g and g != '특별': grades.setdefault(norm(item), g)
for k, steps in lk.items():
    add(k, '베니스의 행운 상자', ' · '.join(f'{s} {pf(p)}' for s, p in steps.items()), grades.get(k))

# 4) 펫 주얼 (소환권 5종 확률)
TK = ['펫 주얼 1회 소환권(귀속)', '펫 주얼 11회 소환권(귀속)', '미지의 펫 주얼 1회 소환권(귀속)', '미지의 펫 주얼 11회 소환권(귀속)', '고급 펫 주얼 1회 소환권(귀속)']
pj = collections.OrderedDict()
for _, _, t, g, name, p in v['펫 주얼 소환']['rows']:
    o = pj.setdefault((name, g), [None] * 5)
    o[TK.index(t)] = float(p)
PJ = [[n, g, ps] for (n, g), ps in pj.items()]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({'v': '11.26', 'src': src, 'pj': PJ, 'pjt': ['일반 1회', '일반 11회', '미지의 1회', '미지의 11회', '고급 1회']},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'codex: 획득처 {len(src)}종 · 펫 주얼 {len(PJ)}종 → {OUT} ({os.path.getsize(OUT)//1024}KB)')
