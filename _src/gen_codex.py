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

# 3-2) 방송 화면에서 확인한 획득처 (공식 확률표에 없는 것)
for name, label, text, g in [
    ('엑카루 아인형 데이터', '상자 몬스터 (엑카루 사냥)', '획득처 표시 · 방송 화면 11/26', '노멀'),
    ('노튼 아인형 데이터', '상자 몬스터 (노튼 사냥)', '지역 데이터는 상자 몬스터에서', None),
]:
    add(name, label, text, g, True)

# 3-3) 우리 데이터 파일(드롭 · 몬스터 도감 성장 · 히든 퀘스트 · 수집 · 전체 아이템)에서 획득처 · 사용처 보강
DD = os.path.join(os.path.dirname(SRC))
def J(f):
    try: return json.load(open(os.path.join(DD, f), encoding='utf-8'))
    except FileNotFoundError: return None
def short(lst, n=6):
    lst = list(dict.fromkeys(lst)); return ' · '.join(lst[:n]) + (f' 외 {len(lst) - n}곳' if len(lst) > n else '')
DR = J('drops.json')
if DR:
    IT = DR['items']; bn, bd, gn = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
    for b in DR['bosses']:
        for i in b[6]: bn[IT[i][0]].append(f"{b[0]} Lv.{b[2]}")
        for i in b[7]: bd[IT[i][0]].append(b[0])
    for g in DR['grounds']:
        lv = min([m[1] or 99 for m in g[3]] or [0])
        for m in g[3]:
            for i in m[2] + m[3]: gn[IT[i][0]].append(f"{g[0]} Lv.{lv}")
    for k, vv in bn.items(): add(k, '보스 드롭', short(vv))
    for k, vv in bd.items(): add(k, '차원 보스 드롭', short(vv))
    for k, vv in gn.items(): add(k, '사냥터 · 던전 드롭', short(vv))
GW = J('growth.json')
if GW:
    mg = collections.defaultdict(list)
    for m in GW['mg']:
        for st in m[3]:
            if st[2] and st[2] != '골드': mg[st[2]].append(f"{m[0]} {st[0]}단계 ×{st[3]}")
    for k, vv in mg.items(): add(k, '몬스터 도감 보상', short(vv, 4))
HQ = J('hidden.json')
if HQ:
    hq = collections.defaultdict(list)
    for q in HQ['q']:
        for st in q[4]:
            for it in st[4][4]:
                nm = re.sub(r' \d+$', '', re.sub(r' \(계정 1회\)$', '', it)); hq[nm].append(q[1])
    for k, vv in hq.items(): add(k, '히든 퀘스트 보상', short(vv, 4))
COLD = J('collect.json')
COL = collections.defaultdict(list)
if COLD:
    for c in COLD['c']:
        for sl in c[2]:
            nm = COLD['items'][sl[0]][0]; COL[norm(nm)].append([c[0], sl[2], sl[1]])
EQT = set('대검 활 바이블 지팡이 완갑 아대 투구 갑옷 각반 장갑 신발 망토 목걸이 귀걸이 반지 허리띠 성배 나침반 보옥 펜던트 방패 성검 곡괭이'.split())
def kind(t):
    if t in EQT: return '장비'
    if t == '몬스터 도감 재료': return '도감 재료'
    if t in ('소환권', '펫 주얼 소환권', '소환 아이템'): return '소환권'
    if t in ('제작 재료', '재료', '수집 재료'): return '재료'
    if t in ('펫 소환 재료', '펫 성장 재료'): return '펫 재료'
    if '상자' in t: return '상자'
    if t == '도안': return '제작법'
    if '기서' in t or '스킬북' in t or t == '스킬 강화 재료': return '스킬 재료'
    if t in ('연금 재료', '감정 재료'): return '연금 재료'
    if '강화' in t: return '강화 재료'
    return '소모품'
ALL = [[n, g if g not in ('특별',) else '', kind(t), t] for n, g, t in (J('items_all.json') or [])]

# 4) 펫 주얼 (소환권 5종 확률)
TK = ['펫 주얼 1회 소환권(귀속)', '펫 주얼 11회 소환권(귀속)', '미지의 펫 주얼 1회 소환권(귀속)', '미지의 펫 주얼 11회 소환권(귀속)', '고급 펫 주얼 1회 소환권(귀속)']
pj = collections.OrderedDict()
for _, _, t, g, name, p in v['펫 주얼 소환']['rows']:
    o = pj.setdefault((name, g), [None] * 5)
    o[TK.index(t)] = float(p)
PJ = [[n, g, ps] for (n, g), ps in pj.items()]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({'v': '11.27', 'src': src, 'pj': PJ, 'all': ALL, 'col': COL, 'pjt': ['일반 1회', '일반 11회', '미지의 1회', '미지의 11회', '고급 1회']},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'codex: 획득처 {len(src)}종 · 전체 {len(ALL)}종 · 수집 사용 {len(COL)}종 · 펫 주얼 {len(PJ)}종 → {OUT} ({os.path.getsize(OUT)//1024}KB)')
