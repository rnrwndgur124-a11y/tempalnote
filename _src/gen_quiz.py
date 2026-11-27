"""오늘의 퀴즈 문제 풀 만들기: 우리 데이터(보스·사냥터·아이템·히든·기능 해금·클래스)에서 사실 문제를 만든다.
출력 data/quiz.json = {"at":날짜, "q":[[유형, 문제, 정답, [오답3], 해설, 링크페이지]]}"""
import json, re, random
P = '/home/claude/tempal/'
D = lambda f: json.load(open(P + 'data/' + f, encoding='utf-8'))
rnd = random.Random(20261127)
def J(w, pair):  # 받침에 맞는 조사
    c = w.rstrip('」)』 ')[-1:] or '가'
    has = '가' <= c <= '힣' and (ord(c) - 0xAC00) % 28 != 0
    if not ('가' <= c <= '힣'): has = c in '0123456789' and c in '013678'
    a, b = {'은는': ('은', '는'), '이가': ('이', '가'), '을를': ('을', '를'), '과와': ('과', '와')}[pair]
    return w + (a if has else b)
Q = []
def add(t, q, a, pool, ex, link):
    pool = [x for x in dict.fromkeys(pool) if x != a and x]
    if len(pool) < 3: return
    Q.append([t, q, a, rnd.sample(pool, 3), ex, link])

dr = D('drops.json')
bosses = dr['bosses']
places = [b[5] for b in bosses if b[1] != '야탄 신전']
for b in bosses:
    n, ty, lv, _, reg, pl = b[:6]
    if ty != '야탄 신전':
        add('boss', f'{ty} 「{n}」, 어디서 만날 수 있을까?', pl, places, f'{J(n,"은는")} {reg} {pl}에 나와요. 레벨 {lv}.', 'drops')
    near = [str(x[2]) for x in bosses if abs(x[2] - lv) <= 15]
    add('blv', f'「{n}」({ty})의 레벨은?', str(lv), near, f'{n}: 레벨 {lv} · {pl}', 'drops')

hx = D('huntxp.json')['g']
gnames = [g[0] for g in hx]
seen = set()
for g in hx:
    for m in g[3]:
        mon = m[0]
        if mon in seen: continue
        homes = [x[0] for x in hx if any(y[0] == mon for y in x[3])]
        if len(homes) != 1: continue
        seen.add(mon)
        others = [x for x in gnames if x not in homes]
        add('mon', f'몬스터 「{mon}」(Lv.{m[1]})가 나오는 사냥터는?', g[0], others, f'{J(mon,"은는")} '+(g[1]+' ' if not g[0].startswith(g[1]) else '')+f'「{g[0]}」에 나와요.', 'hunt')

GR = ['노멀', '레어', '에픽', '유니크', '레전드리']
items = [i for i in D('items_all.json') if i[1] in GR and not i[0].startswith('[도안]')]
for i in rnd.sample(items, min(220, len(items))):
    add('item', f'아이템 「{i[0]}」의 등급은?', i[1], GR, f'{i[0]} — {i[1]} 등급 {i[2]}', 'codex')

hq = D('hidden.json')['q']
regs = sorted({q[0] for q in hq if q[0] != '공통'})
for q in hq:
    if q[0] == '공통': continue
    add('hid', f'히든 퀘스트 {J("「"+q[1]+"」","은는")} 어느 지역에서 할까?', q[0], regs, f'{J("「"+q[1]+"」","은는")} {q[0]} 지역 히든 퀘스트예요.', 'hidden')

ul = D('growth.json')['ul']
lvs = []
for n, c in ul:
    m = re.fullmatch(r'레벨 (\d+) 이상 달성', c)
    if m: lvs.append((n, int(m.group(1))))
pool = sorted({str(l) for _, l in lvs} | {'20', '25', '30', '35', '40', '45', '50'})
for n, l in lvs:
    add('ul', f'「{n}」 기능은 몇 레벨에 열릴까?', str(l), pool, f'{n}: 레벨 {l} 이상이면 열려요.', 'growth')
for n, c in ul:
    if '완료' in c and not c.startswith('레벨'):
        qs = [x[1] for x in ul if '완료' in x[1] and x[1] != c and not x[1].startswith('레벨')]
        add('ulq', f'「{n}」 기능을 여는 조건은?', c, qs, f'{n}: {c}', 'growth')

s = open(P + 'index.html', encoding='utf-8').read()
CLS = json.loads(re.search(r"const CLS=(\[.*?\]);\n", s, re.S).group(1))
WP = ['대검', '활', '지팡이', '바이블']
for c in CLS:
    if c['w'] in WP:
        add('cls', f'클래스 {J("「"+c["n"]+"」","은는")} 어떤 무기를 쓸까?', c['w'], WP, f'{c["n"]}: {c["tier"]} {c["w"]} 클래스', 'weapons')
    add('clt', f'클래스 「{c["n"]}」의 등급은?', c['tier'], ['레어', '에픽', '유니크', '레전드리'], f'{c["n"]}: {c["tier"]} 등급 · {c["w"]}', 'weapons')

json.dump({'at': D('drops.json')['at'], 'q': Q}, open(P + 'data/quiz.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print('퀴즈', len(Q), dict(Counter(q[0] for q in Q)))

# ---------- 레벨별 할 일(lvplan.json) ----------
LP = {'at': D('drops.json')['at'], 'ul': [], 'uq': [], 'g': [], 'b': []}
for n, c in ul:
    m = re.fullmatch(r'레벨 (\d+) 이상 달성', c)
    if m: LP['ul'].append([n, int(m.group(1))])
    else: LP['uq'].append([n, c])
LP['ul'].sort(key=lambda x: x[1])
for g in hx:
    lv = [m[1] for m in g[3]]; xp = [m[2] for m in g[3]]
    if not lv: continue
    LP['g'].append([g[0], g[1], min(lv), max(lv), round(sum(xp) / len(xp)), len(g[3])])
for b in bosses:
    LP['b'].append([b[0], b[1], b[2], b[5]])
json.dump(LP, open(P + 'data/lvplan.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('레벨 계획', len(LP['ul']), len(LP['uq']), len(LP['g']), len(LP['b']))
