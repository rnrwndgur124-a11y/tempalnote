#!/bin/bash
# 사용: ./deploy.sh "커밋 메시지"
set -e
# 동시에 두 번 돌지 않게 잠금 (앞 배포가 끝날 때까지 최대 10분 기다림)
exec 9>/tmp/tempal_deploy.lock
flock -w 600 9 || { echo '배포 중단: 다른 배포가 아직 진행 중'; exit 1; }
# 금지어(다른 사이트 이름): 원본·커밋 메시지·완성 파일에 있으면 올리지 않는다. 글자는 바이트 코드로만 적는다.
BAN="$(printf '\xea\xb9\xa8\xeb\xb9\x84')\|$(printf '\x6b\x6b\x61\x65\x62\x69')"
if printf '%s' "$1" | grep -qi "$BAN" || grep -qi "$BAN" /home/claude/tempal/index.html; then echo "배포 중단: 다른 사이트 이름이 들어 있어요"; exit 1; fi
cd /home/claude/site && git stash -q -u 2>/dev/null || true; git pull -q --rebase; git stash pop -q 2>/dev/null || true
cp /home/claude/tempal/data/ads.txt /home/claude/site/ads.txt && python3 /home/claude/tempal/build_site.py /home/claude/site && python3 /home/claude/tempal/gen_og.py && python3 /home/claude/tempal/gen_codex.py /home/claude/site && python3 /home/claude/tempal/gen_alchemy.py /home/claude/site && python3 /home/claude/tempal/gen_search.py /home/claude/site && python3 /home/claude/tempal/prerender.py /home/claude/site | tail -1 && python3 /home/claude/tempal/extract_assets.py /home/claude/site
if grep -rqi --exclude-dir=.git --include='*.html' --include='*.js' --include='*.txt' --include='*.json' --include='*.xml' --include='*.py' --include='*.sh' "$BAN" /home/claude/site; then echo "배포 중단: 다른 사이트 이름이 들어 있어요"; exit 1; fi
# 자동 점검: 실패하면 올리지 않는다
if ! python3 /home/claude/tempal/check_site.py /home/claude/site; then echo "배포 중단: 위 문제를 먼저 고치세요"; exit 1; fi
# 원본 소스도 저장소에 보관 (다음 작업 때 복구용, 페이지로 읽히지 않게 .txt)
mkdir -p /home/claude/site/_src && cp /home/claude/tempal/index.html /home/claude/site/_src/source_index.html.txt && mkdir -p /home/claude/site/_src/data && cp /home/claude/tempal/data/page_dates.json /home/claude/site/_src/data/ 2>/dev/null; cp /home/claude/tempal/{gen_alchemy.py,extract_assets.py,build_site.py,gen_og.py,gen_codex.py,gen_search.py,prerender.py,check_site.py,deploy.sh,firestore.rules} /home/claude/site/_src/ && mkdir -p /home/claude/site/_src/data && cp /home/claude/tempal/data/prob_items.json /home/claude/tempal/data/alchemy_raw.json /home/claude/site/_src/data/ && cp -r /home/claude/tempal/gfx /home/claude/site/_src/
git add -A && git commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Acpr1h6BLddixputi4M4Kd" && git push -q && git log --oneline -1
