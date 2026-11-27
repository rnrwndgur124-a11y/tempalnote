"""대장간노트 단일 HTML(index.html)을 tempalnote.com용 여러 페이지로 만든다.
각 화면(#quiz 등)을 /quiz/index.html 같은 실제 주소로 내보내고, 페이지마다 제목·설명·canonical을 붙인다."""
import re, os, sys, html, datetime

SRC = '/home/claude/tempal/index.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site'
BASE = 'https://tempalnote.com'
SITE = '템빨 : 대장간노트'

PAGES = {
 'home':    ('템빨 : 대장간노트 | 템빨 오버기어드 강화 계산기·숙제·무기 추천', '템빨 오버기어드 비공식 팬 도구. 강화 기록기, 강화 기대값 계산기, 숙제 체크리스트, 무기 추천 테스트, 첫날 가이드, 로드맵을 한곳에.'),
 'quiz':    ('템빨 무기 추천 테스트 — 나에게 맞는 무기는?', '질문 다섯 개로 템빨 오버기어드 지팡이·대검·활·바이블 중 내 취향에 맞는 무기를 찾아 드려요.'),
 'enhance': ('템빨 강화 기록기 — 오버기어드 단계별 성공률', '템빨 오버기어드 강화 성공·실패를 기록하면 단계별 성공률과 실패로 얻은 파브라늄이 자동으로 쌓입니다.'),
 'calc':    ('템빨 강화 기대값 계산기 — 평균 시도·필요 재료', '성공률과 1회 재료를 넣으면 평균 몇 번 만에 붙는지, 목표 확률까지 몇 번 준비해야 하는지 계산합니다.'),
 'godhand': ('템빨 갓 핸드 프리셋 메모 — 공격·방어·보조 조합', '갓 핸드 메모리 공격형·방어형·보조형 조합을 사냥·PvP·레이드 용도별로 저장하는 메모장.'),
 'homework':('템빨 숙제 체크리스트 — 오늘의 할 일', '템빨 오버기어드 일일 숙제 체크리스트. 게임 초기화 시각인 매일 새벽 5시에 풀리고, 8주 미션·왕실 무기고·비접속 모드까지 내 숙제로 고쳐 쓸 수 있어요.'),
 'starter': ('템빨 첫날 가이드 — 첫 주 할 일·체크리스트 12개', '템빨 오버기어드 첫 주 체크리스트: 사전등록 보상, 무기 선택, 갓 핸드, 출석부, 비접속 모드, 선점 캐릭터 마감까지 놓치기 쉬운 순서대로.'),
 'weapons': ('템빨 클래스 도감 — 레전드리·유니크·에픽 클래스 스킬 총정리', '템빨 오버기어드 클래스 도감. 서사시의 마검사·궁성·교황 레전드리, 신궁·저격수 등 유니크, 에픽 클래스의 능력치와 스킬, 초월자까지 정리.'),
 'systems': ('템빨 시스템 정리 — 오버기어드·갓 핸드·차원 리그', '오버기어드 강화와 돌파, 파브라늄, 코어 점수·오버클럭, 시그니처 장비, 갓 핸드 메모리, 차원 리그 핵심 정리.'),
 'roadmap': ('템빨 6개월 로드맵 — 레이드·공성전·신규 클래스', '템빨 오버기어드 출시 후 6개월 업데이트 계획: 헬가오 레이드, 공성전, 신규 클래스, 새 무기 계열.'),
 'bm':      ('템빨 상점 정리 — 파는 것과 팔지 않는 것', '템빨 오버기어드 과금 요소와 판매하지 않는 편의 기능, 운영 방침 정리.'),
 'coupons': ('템빨 오버기어드 쿠폰 코드 — 지금 쓸 수 있는 쿠폰·입력 방법·이벤트 총정리', '템빨 오버기어드 쿠폰 코드 현황(공식 확인), 게임 안·홈페이지 쿠폰 입력 방법, 사전등록 보상, 웹툰 단행본 쿠폰, SOOP 드롭스, 진행 중인 이벤트를 매일 정리해요.'),
 'community':('템빨 커뮤니티 — 오버기어드 자유게시판·길드 모집·실시간 채팅', '템빨 오버기어드 유저 커뮤니티. 자유 · 질문 · 공략 · 길드 모집 게시판과 실시간 채팅(전체 · 파티 · 거래 · 질문). 구글 로그인 후 닉네임으로 글쓰기.'),
 'streamers':('템빨 서버 목록 · 스트리머 서버 정리 — 일반 14 · 크리에이터 6, 똘끼·뜨뜨뜨뜨·우레 어느 서버?', '템빨 오버기어드 서버 20개(일반 14 · 크리에이터 6)와 유튜브·SOOP 방송인 서버 총정리. 라우엘·레가스·루나·하스터·루비·파그마 서버별 방송인, 유료 광고 방송 표시, 길드원 모집 여부를 한눈에.'),
 'news':    ('템빨 공식 소식 · 확인 중인 현상 — 버그 피하는 법 정리', '템빨 오버기어드 공식 공지 요약과 확인 중인 현상(거래소 수수료, 스케줄 모드 자동 정비, 펫 주얼 합성 표기 등) 9건을 피하는 법과 함께 매일 정리해요.'),
 'trade':   ('템빨 거래소 수수료 계산기 — 판매 수령액·묶음 단가·다이아 환산', '템빨 오버기어드 거래소에 올리기 전 수수료 빼고 받는 금액, 목표 금액을 받으려면 올릴 가격, 묶음 개당 단가 비교, 다이아 원화 환산을 바로 계산해요.'),
 'sim':     ('템빨 뽑기 시뮬레이터 · 강화 시뮬 — 11연 · 110연 소환, 레전드리 합성, +12 강화', '템빨 오버기어드 소환 시뮬레이터와 강화 시뮬레이터. 넥슨 공식 확률로 클래스 · 갓 핸드 11연 · 110연 뽑기(결과 이미지), 고급 소환권 레전드리, 유니크 합성 12% · 마일리지 15 · 초월자 도전, 일반 · 축복 강화 목표 계산기까지.'),
 'hunt':    ('템빨 사냥터 — 레벨별 사냥터 61곳 Lv.1~85 · 몬스터 · 오염된 존재 · 데이터 큐브', '템빨 오버기어드 레벨별 사냥터 총정리. 바이란 평원(Lv.1) · 바이란 폐광 · 얼음 가시 숲 · 망자의 설원 · 북쪽 절벽 해안 · 윈스톤 묘지 · 오크 습격지 · 회색 숲 · 폐허가 된 마을 · 붉은 바위 고원 · 잊혀진 뱀파이어 유적 ~ 동부 사막(Lv.80). 내 레벨 추천, 거점 텔레포트, 데이터 큐브, 필드 보스 위치, 33~34 레벨 막힐 때 요령.'),
 'map':     ('템빨 지도 — 오버기어드 지역 14곳 위치 · 데이터 큐브 · 명소 · 탐사 지도', '템빨 오버기어드 탐사 지도. 바이란 · 노튼 · 킨바이 · 윈스톤 · 라인하르트 · 알테스 · 엑카루 · 벨두인 · 레이단 · 코크로 섬 · 수아즈 협곡 · 크라임 숲 · 레베카 · 지브라 지역 위치와 데이터 큐브 · 명소 · 업적, 내 탐사 진행도.'),
 'codex':   ('템빨 아이템 도감 — 재료 획득처 · 사용처 · 펫 주얼 360종 · 제작템 · 갓 핸드 · 클래스 검색', '템빨 오버기어드 아이템 도감. 파브라늄 · 강화석 · 결속석 · 제작법 조각 등 재료를 어디서 얻는지(공식 확률표: 상자 · 분해 · 행운 상자)와 어디에 쓰는지(제작식), 펫 주얼 360종 소환 확률, 제작 장비 · 클래스 · 갓 핸드 · 펫 · 칭호 · 개조 무기 통합 검색.'),
 'archive': ('템빨 데이터 큐브 위치 · 히든 퀘스트 · 아카이브 달성도 — 지역별 탐사 체크리스트', '템빨 오버기어드 데이터 큐브 위치와 보상, S등급 히든 퀘스트, 아카이브 지역 달성도(메인 퀘스트 · 몬스터 도감 · 수집 · 데이터 큐브) 정리. 지역 12곳 탐사 체크리스트, 윈스톤 데이터 큐브 5곳 영상, 월드맵 · 보스 알림 · 채광 요령.'),
 'prob':    ('템빨 강화 확률 총정리 — +6 60% · 파괴 · 축복 · 소환 공식 확률', '템빨 오버기어드 강화 확률(넥슨 공식): 장비 일반 강화 +5까지 100%, +6 60% ~ +12 1%, 실패 시 파괴. 축복 강화 · 시그니처 · 오버기어드 · 스킬 강화 · 감정 · 클래스/갓 핸드 소환 · 합성 · 잠재력 확률 총정리.'),
 'craft':   ('템빨 제작 도감 — 레시피 231종 재료·성공률·골드 총정리', '템빨 오버기어드 제작 도감. 무기·방어구·장신구·유물·성물 레시피 231종의 재료, 성공률, 대성공(+6), 골드, 제작 경험치와 등급별 제작 규칙.'),
 'titles':  ('템빨 칭호 도감 — 칭호 53종 장착·보유 효과와 획득 조건', '템빨 오버기어드 칭호 53종의 장착 효과, 보유 효과, 획득 조건 정리. 사냥용 추천 칭호와 바로 챙길 칭호.'),
 'achieve': ('템빨 업적 목록 — 업적 182개 목표 수치 정리', '템빨 오버기어드 업적 목록. 클래스·갓 핸드·펫·강화·제작·사냥·퀘스트·생활 업적의 단계별 목표 수치.'),
 'pets':    ('템빨 펫 도감 — 동행 펫·비행 펫 28종 이미지', '템빨 오버기어드 펫 도감. 꽃잎 토끼, 말락서스, 선구자 등 동행 펫과 비행 펫 28종 이미지와 도감 보상 정리.'),
 'gear':    ('템빨 연금 옵션 확률 · 장비 비교 — 원하는 옵션 평균 몇 번? 공식 확률 1,701줄', '템빨 오버기어드 장비 연금 옵션을 부위 · 슬롯별로 정리했어요. 넥슨 공개 확률표로 원하는 옵션이 한 번에 뜰 확률과 평균 횟수를 계산하고, 두 장비를 사냥 · 보스 · PvP 기준으로 비교하세요.'),
 'outfit':  ('템빨 코디 미리보기 — 스킨 갈아입히기 · 펫 · 탈것 48종 돌려보기', '템빨 오버기어드 스킨(모르페우스의 계시자 · 미완의 시절 · 마스크 · 볼캡)을 갈아입혀 보고, 동행 · 비행 · 지상 펫과 펫 스킨 48종을 360도로 돌려 보세요. 등급별 장착 효과 포함.'),
 'timer':   ('템빨 보스 타이머 · 일정표', '템빨 오버기어드 필드 보스 처치 시각을 기록하면 다음 출현까지 카운트다운. 매일 반복 일정표와 1분 전 알림.'),
 'backup':  ('저장함 · 백업 | 템빨 : 대장간노트', '대장간노트 강화 기록·숙제·프리셋·보스 타이머 기록을 파일로 백업하고 복원.'),
 'videos':  ('템빨 추천 영상 — 조회수 1만 이상 오버기어드 유튜브 모음', '템빨 오버기어드 유튜브 영상 중 조회수 1만 회 이상만 모았어요. 무과금 입문 가이드, 직업 추천, 솔직 리뷰, 공식 쇼케이스·무기 소개.'),
 'official':('템빨 공식 채널·원작 웹툰·웹소설 보기', '템빨 오버기어드 공식 홈페이지·유튜브·카카오톡 채널과 원작 웹툰·웹소설 바로가기.'),
 'contact': ('문의하기 | 템빨 : 대장간노트', '광고·제휴 제안, 정보 제보, 오류 신고 문의: rnrwndgur124@naver.com'),
 'privacy': ('개인정보처리방침 | 템빨 : 대장간노트', '템빨 : 대장간노트의 개인정보처리방침과 쿠키·광고 안내.'),
 'terms':   ('이용약관 | 템빨 : 대장간노트', '템빨 : 대장간노트 이용약관.'),
 'about':   ('사이트 소개 | 템빨 : 대장간노트', '템빨 오버기어드 비공식 팬 도구 사이트 템빨 : 대장간노트 소개.'),
}
KEYS = [k for k in PAGES if k != 'home']

src = open(SRC, encoding='utf-8').read()

def url(k):
    return BASE + '/' if k == 'home' else f'{BASE}/{k}/'

import json
GROUPS = [g for g in re.findall(r"k:\[([^\]]+)\]", re.search(r'const GROUPS=\[(.*?)\];', src).group(1))]
GROUPS = [[x.strip().strip("'") for x in g.split(',')] for g in GROUPS]
def ldjson(k, title, desc):
    today = datetime.date.today().isoformat()
    if k == 'home':
        d = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "alternateName": ["대장간노트", "템빨 대장간노트"], "url": BASE + '/', "inLanguage": "ko"},
             {"@context": "https://schema.org", "@type": "Organization", "name": SITE, "url": BASE + '/', "logo": BASE + '/img/app/icon-512.png'}]
    else:
        d = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE, "item": BASE + '/'},
                {"@type": "ListItem", "position": 2, "name": title.split(" — ")[0].split(" | ")[0], "item": url(k)}]},
             {"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": url(k), "inLanguage": "ko",
              "dateModified": today, "isPartOf": {"@type": "WebSite", "name": SITE, "url": BASE + '/'}, "primaryImageOfPage": BASE + f'/img/og/{k}.jpg'}]
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>\n'

def related(k):
    # 같은 묶음 페이지 + 많이 찾는 페이지를 정적 링크로 (검색로봇이 따라갈 수 있게)
    grp = next((g for g in GROUPS if k in g), [])
    keys = [x for x in grp if x != k] + [x for x in ['coupons', 'streamers', 'news', 'craft', 'starter', 'calc'] if x != k and x not in grp]
    keys = keys[:10]
    links = ''.join(f'<a href="{url(x)}">{html.escape(PAGES[x][0].split(" — ")[0].split(" | ")[0])}</a>' for x in keys if x in PAGES)
    d = PDATE.get(k, {}).get('d', _today)
    dd = f'{int(d[5:7])}월 {int(d[8:10])}일'
    fix = ('<div class="wrap" style="padding:18px 20px 4px"><div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;'
           'border:1px solid #2a3b5a;border-radius:12px;padding:12px 16px;font-size:13.5px;color:#cfd8e6">'
           f'<span>이 페이지 마지막 수정 <b style="color:#e3c27a">{dd}</b> · 게임 화면 · 공식 가이드 기준. 패치로 바뀔 수 있어요.</span>'
           '<a href="/contact/" style="margin-left:auto;font-weight:800;color:#e3c27a">틀린 정보 · 바뀐 내용 제보 →</a></div></div>\n')
    return fix + ('<nav class="wrap relnav" aria-label="함께 보면 좋은 페이지" style="padding:8px 20px 28px">'
            '<p style="margin:0 0 8px;font-weight:800;color:#e3c27a">함께 보면 좋은 페이지</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px">{links}</div></nav>\n')

def build(k):
    s = src
    title, desc = PAGES[k]
    # 내부 링크: #home → /, #키 → /키/
    s = s.replace('href="#home"', 'href="/"')
    for key in KEYS:
        s = s.replace(f'href="#{key}"', f'href="/{key}/"')
    # 자바스크립트가 만드는 링크
    s = s.replace('href="#${k}"', 'href="/${k}/"').replace('href="#${r.k}"', 'href="/${r.k}/"')
    s = s.replace("${location.href.split('#')[0]}#quiz", 'https://tempalnote.com/quiz/')
    # 제목·설명·검색용 정보
    s = re.sub(r'<title>.*?</title>', f'<title>{html.escape(title)}</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc)}">', s, count=1)
    head = (f'<link rel="canonical" href="{url(k)}">\n<meta property="og:url" content="{url(k)}">\n'
            '<meta property="og:type" content="website">\n<meta property="og:site_name" content="템빨 : 대장간노트">\n'
            '<meta name="keywords" content="템빨, 템빨 오버기어드, 오버기어드, 템빨 강화, 템빨 계산기, 템빨 숙제, 템빨 무기 추천, 템빨 쿠폰, 템빨 웹툰, 갓 핸드, 파브라늄, 대장간노트">\n'
            '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<meta name="theme-color" content="#050a14">\n'
            f'<meta property="og:image" content="{BASE}/img/og/{k}.jpg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:locale" content="ko_KR">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{BASE}/img/og/{k}.jpg">\n'
            + ldjson(k, title, desc) +
            f'<script>window.START={k!r};window.PDATE={json.dumps({x: v.get("d") for x, v in PDATE.items()})};</script>\n')
    s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', head + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    # 3D 라이브러리는 홈에서만
    if k != 'home':
        s = s.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n', '')
    # 페이지 제목이 라우팅 후에도 유지되게
    s = s.replace("document.title=PAGES[v]?PAGES[v].t+' | 템빨 : 대장간노트':'템빨 : 대장간노트 | 템빨 오버기어드 강화 계산기·숙제·무기 추천';",
                  "document.title=v===window.START?document.title:(PAGES[v]?PAGES[v].t+' | 템빨 : 대장간노트':'템빨 : 대장간노트 | 템빨 오버기어드 강화 계산기·숙제·무기 추천');")
    # 페이지마다 자기 화면만 남긴다 (모든 주소가 같은 내용으로 보이면 검색엔진이 중복 페이지로 묶어 버림)
    s = re.sub(r'<section class="view" data-v="([^"]+)">.*?</section>\n?', lambda m: m.group(0) if m.group(1) == k else '', s, flags=re.S)
    s = s.replace("const $=s=>document.querySelector(s);", "const $=s=>document.querySelector(s)||document.createElement('div');", 1)
    # #쿠폰 같은 해시 링크를 누르면 그 화면이 이 페이지에 없으니 진짜 주소로 이동
    old_route = "function route(){const h=location.hash.slice(1);"
    assert old_route in s
    s = s.replace(old_route, old_route + "if(h&&PAGES[h]&&!document.querySelector('.view[data-v=\"'+h+'\"]')){location.replace(h==='home'?'/':'/'+h+'/');return}", 1)
    # 다른 페이지 화면이 없으니, 처음 실행될 때 빈 값으로 저장해 내 기록을 덮어쓰지 않게: 페이지 준비가 끝난 뒤부터만 저장
    old_save = "const save=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};"
    assert old_save in s
    s = s.replace(old_save, "let __live=0;document.addEventListener('DOMContentLoaded',()=>setTimeout(()=>__live=1,0));const save=(k,v)=>{if(!__live)return;try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};", 1)
    if k != 'home':
        s = s.replace('</main>', related(k) + '</main>', 1)
    return s

# 페이지마다 내용이 바뀐 날을 기록 (마지막 수정일 표시용)
import hashlib
PD_PATH = '/home/claude/tempal/data/page_dates.json'
try:
    PDATE = json.load(open(PD_PATH, encoding='utf-8'))
except Exception:
    PDATE = {}
_today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat()
for _k in PAGES:
    _m = re.search(r'<section class="view" data-v="%s">.*?</section>' % re.escape(_k), src, re.S)
    _h = hashlib.sha1((_m.group(0) if _m else '').encode('utf-8')).hexdigest()
    if PDATE.get(_k, {}).get('h') != _h:
        PDATE[_k] = {'h': _h, 'd': _today}
if OUT == '/home/claude/site':
    json.dump(PDATE, open(PD_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

os.makedirs(OUT, exist_ok=True)
for k in PAGES:
    d = OUT if k == 'home' else os.path.join(OUT, k)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(build(k))

# 404: 홈으로 보내기
open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
    '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
    '<meta http-equiv="refresh" content="0;url=/"><title>템빨 : 대장간노트</title></head>'
    '<body style="background:#050a14;color:#e8edf5;font-family:sans-serif;text-align:center;padding:80px">'
    '<p>페이지를 찾을 수 없어요. <a style="color:#e3c27a" href="/">홈으로 이동</a></p></body></html>')

today = datetime.date.today().isoformat()
pri = {'home': '1.0', 'calc': '0.9', 'enhance': '0.9', 'quiz': '0.9', 'coupons': '0.9', 'prob': '0.9', 'sim': '0.9', 'archive': '0.9', 'hunt': '0.9', 'map': '0.9', 'codex': '0.9', 'news': '0.9', 'streamers': '0.9', 'gear': '0.9', 'community': '0.9', 'trade': '0.8', 'homework': '0.8', 'starter': '0.8'}
urls = ''.join(f'  <url><loc>{url(k)}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>{pri.get(k, "0.6")}</priority></url>\n' for k in PAGES if k != 'community')
# RSS (네이버 서치어드바이저 제출용): 최근 수정된 페이지 순
import email.utils
def _rfc(d):
    dt = datetime.datetime.strptime(d, '%Y-%m-%d').replace(hour=12, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    return email.utils.format_datetime(dt)
_items = sorted([k for k in PAGES if k not in ('privacy', 'terms', 'contact', 'backup', 'community')], key=lambda k: PDATE.get(k, {}).get('d', _today), reverse=True)
_rss = ''.join(f"  <item><title>{html.escape(PAGES[k][0])}</title><link>{url(k)}</link><guid>{url(k)}</guid><description>{html.escape(PAGES[k][1])}</description><pubDate>{_rfc(PDATE.get(k, {}).get('d', _today))}</pubDate></item>\n" for k in _items)
open(os.path.join(OUT, 'rss.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
    f'  <title>{SITE}</title><link>{BASE}/</link><description>템빨: 오버기어드 강화 계산기 · 확률 · 쿠폰 · 사냥터 · 공략 정리</description><language>ko</language>\n'
    + _rss + '</channel></rss>\n')

open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
print('built', len(PAGES), 'pages into', OUT)
